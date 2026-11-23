#!/usr/bin/env python3
"""
test_agente.py — Prueba de humo del agente SOC local (Capa 4 del plan).

1. Envía una alerta de ejemplo (fuerza bruta SSH) a soc-triage con salida JSON
   forzada por esquema (structured outputs de Ollama) y razonamiento desactivado.
2. Si el dictamen es "sospechoso" o "intrusion", escala a soc-analista para
   correlación y generación de reglas.
3. Muestra tokens/s de cada nivel.

Solo usa la librería estándar. Uso:
    python3 ia_local/test_agente.py [--solo-triage]
"""
import json
import sys
import urllib.request

OLLAMA = "http://127.0.0.1:11434/api/chat"

ESQUEMA_TRIAGE = {
    "type": "object",
    "properties": {
        "veredicto": {"type": "string", "enum": ["falso_positivo", "sospechoso", "intrusion"]},
        "confianza": {"type": "number", "minimum": 0, "maximum": 1},
        "tecnica_mitre": {"type": "string"},
        "evidencia": {"type": "array", "items": {"type": "string"}},
        "justificacion": {"type": "string"},
        "accion_inmediata": {"type": "string"},
    },
    "required": ["veredicto", "confianza", "tecnica_mitre", "evidencia", "justificacion", "accion_inmediata"],
}

ALERTA_EJEMPLO = """Origen ML: Isolation Forest (score=-0.31, umbral=-0.20) — alerta no concluyente
Host: metasploitable3 (10.0.2.15) — Servicio: OpenSSH 6.6.1p1 Ubuntu
Ventana: 2026-11-22 03:12:04 a 03:12:41 (37 s)
Fragmento /var/log/auth.log:
Nov 22 03:12:04 msf3 sshd[2211]: Failed password for invalid user admin from 10.0.2.99 port 51022 ssh2
Nov 22 03:12:05 msf3 sshd[2213]: Failed password for invalid user oracle from 10.0.2.99 port 51030 ssh2
Nov 22 03:12:05 msf3 sshd[2215]: Failed password for root from 10.0.2.99 port 51034 ssh2
... (184 líneas similares, 61 usuarios distintos)
Nov 22 03:12:40 msf3 sshd[2601]: Accepted password for vagrant from 10.0.2.99 port 51990 ssh2
Nov 22 03:12:41 msf3 sshd[2603]: pam_unix(sshd:session): session opened for user vagrant by (uid=0)
Historial: 10.0.2.99 no aparece en los 30 días previos."""


def chat(model, messages, **extra):
    body = {"model": model, "messages": messages, "stream": False, **extra}
    req = urllib.request.Request(OLLAMA, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        resp = json.load(r)
    tps = resp["eval_count"] / (resp["eval_duration"] / 1e9) if resp.get("eval_duration") else 0
    return resp["message"]["content"], tps


def main():
    print("=== Nivel 1: soc-triage ===")
    contenido, tps = chat(
        "soc-triage",
        [{"role": "user", "content": ALERTA_EJEMPLO}],
        format=ESQUEMA_TRIAGE,   # salida JSON validada por esquema
        think=False,             # qwen3: sin razonamiento largo -> respuesta rápida
    )
    dictamen = json.loads(contenido)
    print(json.dumps(dictamen, indent=2, ensure_ascii=False))
    print(f"[velocidad] {tps:.1f} tok/s")

    if "--solo-triage" in sys.argv or dictamen["veredicto"] == "falso_positivo":
        return

    print("\n=== Nivel 2: soc-analista ===")
    prompt = (f"Alerta original:\n{ALERTA_EJEMPLO}\n\n"
              f"Dictamen del Nivel 1:\n{json.dumps(dictamen, ensure_ascii=False)}\n\n"
              "Correlaciona, propone contención y genera una regla Sigma y una regla iptables.")
    contenido, tps = chat("soc-analista", [{"role": "user", "content": prompt}])
    print(contenido)
    print(f"[velocidad] {tps:.1f} tok/s")


if __name__ == "__main__":
    main()
