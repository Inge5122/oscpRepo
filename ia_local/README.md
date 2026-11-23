# IA Local — Agente SOC con Ollama (Capa 4 del plan)

Implementación de la **Capa 4: Agente Local de Razonamiento** descrita en la [sección 5 de PLAN_DE_ESTUDIO_Y_LABORATORIOS.md](../PLAN_DE_ESTUDIO_Y_LABORATORIOS.md). Toda la inferencia es local: ningún log ni IoC sale del equipo.

## 1. Hardware y límites

| Componente | Valor | Consecuencia |
|---|---|---|
| CPU | Intel i7-11800H, 8C/16T, AVX2 + AVX-512 | Buen rendimiento para las capas que no caben en GPU |
| RAM | 14 GiB (+4 GiB swap) | Techo práctico: modelos de hasta 8B cómodos; 14B muy justo |
| GPU | RTX 3050 Ti Laptop, **4 GB VRAM** | **Cuello de botella.** Solo los modelos ≤ 4B caben enteros en GPU |
| Ollama | v0.17.4, servicio systemd | — |

## 2. Arquitectura de dos niveles

```
Alertas ML (Isolation Forest / Random Forest)
        │
        ▼
┌──────────────────────────┐   falso_positivo
│ Nivel 1: soc-triage      │ ─────────────────► archivo / feedback al ML
│ qwen3:4b · 100% GPU      │
│ salida JSON por esquema  │
└──────────────────────────┘
        │ sospechoso / intrusion
        ▼
┌──────────────────────────┐
│ Nivel 2: soc-analista    │ ◄── RAG (nomic-embed-text): MITRE ATT&CK, Sigma
│ llama3.1:8b · GPU + CPU  │
│ correlación + reglas     │ ──► iptables · Sigma · Suricata (BORRADOR)
└──────────────────────────┘
```

**¿Por qué dos niveles?** Con 4 GB de VRAM, un modelo de 8B corre a ~10 tok/s (parte en CPU). Usarlo para cada alerta sería lento. El modelo de 4B filtra rápido y en GPU; el de 8B solo procesa lo que el Nivel 1 escala.

### Modelos descartados

| Modelo | Motivo |
|---|---|
| Mistral 7B | Generación anterior; peor en JSON estructurado y tool calling |
| DeepSeek-R1 7B/8B | Razonamiento largo antes de responder: minutos por alerta con este hardware |
| `qwen2.5-coder:7b` (ya instalado) | Especializado en código: útil para escribir el pipeline ETL, no para triage de logs |

## 3. Estructura

```
ia_local/
├── README.md                         # este documento
├── setup_ollama.sh                   # descarga modelos, crea soc-triage/soc-analista, instala override
├── test_agente.py                    # prueba de humo end-to-end (Nivel 1 → Nivel 2)
├── modelfiles/
│   ├── Modelfile.soc-triage          # Nivel 1: qwen3:4b + prompt de triage
│   └── Modelfile.soc-analista        # Nivel 2: llama3.1:8b + prompt de correlación/reglas
└── systemd/
    └── ollama-override.conf          # variables de entorno del servidor Ollama
```

## 4. Instalación

```bash
# 1) Variables del servidor (requiere sudo; respalda el override anterior)
sudo ./ia_local/setup_ollama.sh --systemd

# 2) Si ya aplicaste el override, basta con crear los modelos (sin sudo)
./ia_local/setup_ollama.sh

# 3) Prueba
python3 ia_local/test_agente.py              # Nivel 1 + Nivel 2
python3 ia_local/test_agente.py --solo-triage
ollama ps                                    # verificar columna PROCESSOR
```

## 5. Parámetros y justificación

### 5.1 Servidor (`systemd/ollama-override.conf`)

| Variable | Valor | Por qué |
|---|---|---|
| `OLLAMA_FLASH_ATTENTION` | `1` | Menos memoria en la atención; requisito para cuantizar la KV cache |
| `OLLAMA_KV_CACHE_TYPE` | `q8_0` | KV cache en 8 bits: ~½ VRAM para el contexto, pérdida de calidad despreciable |
| `OLLAMA_MAX_LOADED_MODELS` | `1` | 4 GB no alcanzan para dos modelos a la vez |
| `OLLAMA_NUM_PARALLEL` | `1` | Cada petición paralela multiplica la KV cache; el pipeline debe encolar |
| `OLLAMA_KEEP_ALIVE` | `10m` | Evita recargar el modelo entre alertas consecutivas |
| `OLLAMA_HOST` | `127.0.0.1:11434` | Solo loopback: la API no tiene autenticación. Ver sección 7 |

### 5.2 Modelos (`modelfiles/`)

| Parámetro | soc-triage | soc-analista | Por qué |
|---|---|---|---|
| Base | `qwen3:4b` | `llama3.1:8b` | Ver sección 2 |
| Prompt de sistema | Reglas de decisión + tabla MITRE | Tabla MITRE + restricciones técnicas + plantillas Sigma/Suricata/iptables | Ver lecciones de la sección 6 |
| `num_ctx` | 8192 | 8192 | Suficiente para logs recortados; más contexto = más VRAM |
| `temperature` | 0.1 | 0.2 | Triage determinista; algo de flexibilidad para redactar reglas |
| `top_p` / `top_k` | 0.9 / 20 | 0.9 / — | Recorta tokens improbables |
| `repeat_penalty` | 1.05 | 1.1 | Evita bucles en listas de evidencia y reglas largas |
| `num_predict` | 512 | 1536 | Un JSON de dictamen vs. reglas + explicación |

### 5.3 Llamada a la API (`test_agente.py`)

- **`format: <esquema JSON>`** (structured outputs): Ollama restringe la generación al esquema, así que el JSON siempre es parseable y `veredicto` solo puede ser `falso_positivo`, `sospechoso` o `intrusion`.
- **`think: false`**: desactiva el razonamiento de qwen3 para respuestas rápidas. Para un caso dudoso puede activarse (`think: true`), a costa de tiempo.

## 6. Resultados medidos (2026-11-22)

Alerta de prueba: 184 fallos SSH desde `10.0.2.99` contra 61 usuarios y, al final, login exitoso como `vagrant`.

### Nivel 1 — soc-triage

| Prueba | Veredicto | MITRE | Velocidad | Procesador |
|---|---|---|---|---|
| Prompt inicial (sin reglas de decisión) | ❌ `sospechoso` — afirmó que el ataque "se detuvo" | ❌ T1068 | 32.8 tok/s | 18% CPU / 82% GPU |
| Prompt con reglas de decisión + tabla MITRE | ✅ `intrusion`, confianza 0.95 | ✅ T1078 (T1110.003 en la justificación) | 34.9 tok/s | 18% CPU / 82% GPU |
| Mismo prompt **+ override aplicado** (Flash Attention + KV `q8_0`) | ✅ `intrusion` | ✅ T1078 | 25–37 tok/s | **100% GPU** (3.7 GB, antes 4.2 GB) |

La velocidad varía entre ejecuciones (25–49 tok/s) según la carga de la GPU y si el modelo ya estaba en memoria. Lo determinante es que, con el override, el modelo cabe entero en la VRAM.

**Lección:** un modelo de 4B necesita reglas de decisión explícitas en el prompt. Sin ellas, confunde la consecuencia (escalada) con la técnica observada (fuerza bruta) e ignora eventos que contradicen su primera impresión. Limitaciones residuales observadas: a veces deja solo una técnica en `tecnica_mitre` y puede mencionar EventIDs de Windows al analizar logs de Linux. Lo dudoso se corrige en el Nivel 2.

En una ejecución posterior, con el modelo ya cargado en memoria, el Nivel 1 llegó a **49.2 tok/s**.

### Nivel 2 — soc-analista

| Prueba | Correlación / MITRE | Reglas generadas | Velocidad | Procesador |
|---|---|---|---|---|
| Prompt inicial (sin plantillas) | Cadena correcta, pero ❌ T1590 (reconocimiento) para la fuerza bruta | ❌ Sigma con sintaxis inventada (`selectors`, `action`) y lógica invertida · ❌ Suricata no compila y busca texto dentro de SSH cifrado · ✅ iptables | 10.0 tok/s | 45% CPU / 55% GPU |
| Prompt con plantillas + restricciones técnicas | ✅ T1110 + T1078 · ⚠️ fase marcada como "ejecución" (es acceso inicial) | ✅ Sigma con estructura válida · ✅ iptables marcada como BORRADOR · Suricata omitida (correcto: evidencia de host, no de red) | 8.6 tok/s | 45% CPU / 55% GPU |

Con el override aplicado el Nivel 2 se mantiene igual (8.8 tok/s, 45% CPU / 55% GPU): sus pesos (4.9 GB) no caben en 4 GB de VRAM, así que la KV cache cuantizada apenas influye. Una respuesta completa del Nivel 2 tarda **~1–2 minutos**. Por eso solo debe recibir lo que escala el Nivel 1.

**Lecciones:**
- Un modelo de 8B **no conoce de memoria la sintaxis de Sigma ni de Suricata**: sin ejemplos, inventa formatos plausibles pero inválidos. Con plantillas en el prompt genera reglas válidas, pero tiende a **copiar la plantilla casi literal**. Para ataques distintos de la fuerza bruta SSH hace falta el **RAG con reglas reales de SigmaHQ** (paso 2 de la sección 8), que le dé ejemplos del tipo de evento correcto.
- Hay que explicarle las restricciones físicas del entorno (por ejemplo, que el tráfico cifrado no se puede inspeccionar). El modelo no las deduce.
- Toda regla generada debe validarse con herramientas antes de desplegarla: `sigma check` (de `sigma-cli`) para Sigma y `suricata -T -S regla.rules` para Suricata.

## 7. Seguridad

- **`OLLAMA_HOST=127.0.0.1`** (aplicado el 2026-11-22; verificado con `ss -ltnp | grep 11434`). La configuración anterior usaba `0.0.0.0`, que exponía la API de Ollama, sin autenticación, a toda la red, incluidas las VMs vulnerables del laboratorio como Metasploitable 3. Cualquiera de ellas podía usar los modelos y leer los prompts con telemetría. Si se necesita acceso remoto, usar un túnel SSH (`ssh -L 11434:127.0.0.1:11434 usuario@host`) en lugar de volver a `0.0.0.0`.
- `setup_ollama.sh --systemd` guarda un respaldo del override anterior en `/etc/systemd/system/ollama.service.d/override.conf.bak.<fecha>`.
- Las reglas generadas por el Nivel 2 son **borradores**: revisarlas antes de desplegarlas.
- No enviar al modelo logs completos sin recortar: además de saturar el contexto, pueden contener credenciales en texto claro.

## 8. Próximos pasos

1. ~~Aplicar el override y confirmar `100% GPU` para soc-triage~~ ✅ Hecho el 2026-11-22.
1. Validar automáticamente las reglas del Nivel 2 con `sigma check` y `suricata -T` antes de mostrarlas.
2. Indexar MITRE ATT&CK y el repositorio SigmaHQ con `nomic-embed-text` (RAG para el Nivel 2).
3. Conectar la salida de Isolation Forest / Random Forest (Capa 3) a `soc-triage` con una cola (una alerta a la vez).
4. Crear un conjunto de alertas etiquetadas a partir de los laboratorios propios (Fase 1) para medir la precisión del triage.
