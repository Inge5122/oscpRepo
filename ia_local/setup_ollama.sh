#!/usr/bin/env bash
# =====================================================================
#  setup_ollama.sh — Configura los modelos del agente SOC local (Capa 4)
#
#  Uso:
#    ./ia_local/setup_ollama.sh            # descarga modelos base y crea soc-triage / soc-analista
#    sudo ./ia_local/setup_ollama.sh --systemd   # además instala el override del servicio
# =====================================================================
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_MODELS=(qwen3:4b llama3.1:8b nomic-embed-text)

if [[ "${1:-}" == "--systemd" ]]; then
    if [[ $EUID -ne 0 ]]; then
        echo "[!] --systemd requiere sudo." >&2
        exit 1
    fi
    dest=/etc/systemd/system/ollama.service.d/override.conf
    mkdir -p "$(dirname "$dest")"
    if [[ -f "$dest" ]]; then
        cp "$dest" "$dest.bak.$(date +%Y%m%d%H%M%S)"
        echo "[*] Respaldo del override anterior creado junto a $dest"
    fi
    install -m 644 "$DIR/systemd/ollama-override.conf" "$dest"
    systemctl daemon-reload
    systemctl restart ollama
    echo "[+] Override instalado y servicio reiniciado."
    # Esperar a que la API responda antes de seguir.
    for _ in $(seq 1 20); do
        curl -sf http://127.0.0.1:11434/api/version >/dev/null && break
        sleep 1
    done
    systemctl show ollama --property=Environment | tr ' ' '\n' | grep OLLAMA_
fi

for m in "${BASE_MODELS[@]}"; do
    echo "[*] Descargando $m"
    ollama pull "$m"
done

echo "[*] Creando soc-triage (Nivel 1)"
ollama create soc-triage -f "$DIR/modelfiles/Modelfile.soc-triage"
echo "[*] Creando soc-analista (Nivel 2)"
ollama create soc-analista -f "$DIR/modelfiles/Modelfile.soc-analista"

echo "[+] Listo. Prueba con:  python3 $DIR/test_agente.py"
ollama list
