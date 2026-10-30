#!/usr/bin/env bash
# Jalankan Streamlit di port 8501 lalu buka Cloudflare Quick Tunnel. Ctrl+C menghentikan keduanya.
set -euo pipefail
cd "$(dirname "$0")"

CLOUDFLARED=$(command -v cloudflared || true)
if [ -z "$CLOUDFLARED" ]; then
  if [ "$(uname -s)" = "Linux" ]; then
    ARCH=amd64
    if [ "$(uname -m)" = "aarch64" ]; then ARCH=arm64; fi
    curl -sSL -o cloudflared "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-$ARCH"
    chmod +x cloudflared
    CLOUDFLARED=./cloudflared
  else
    echo "cloudflared belum terpasang. macOS: brew install cloudflared" >&2
    exit 1
  fi
fi

python -m streamlit run app.py --server.port 8501 --server.headless true &
STREAMLIT_PID=$!
trap 'kill $STREAMLIT_PID' EXIT

until curl -sf http://localhost:8501/_stcore/health >/dev/null; do
  kill -0 $STREAMLIT_PID 2>/dev/null || { echo "Streamlit gagal jalan." >&2; exit 1; }
  sleep 1
done
echo "Streamlit jalan di http://localhost:8501. Link publik https://xxxx.trycloudflare.com muncul di bawah."
"$CLOUDFLARED" tunnel --url http://localhost:8501 --no-autoupdate
