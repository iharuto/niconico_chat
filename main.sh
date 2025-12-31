#!/usr/bin/env bash
set -euo pipefail

ROOM_CODE="${ROOM_CODE:-BIO2025}"
PORT="${PORT:-3000}"
MAX_CLIENTS="${MAX_CLIENTS:-30}"
TMUX_SESSION="${TMUX_SESSION:-lan_chat}"

get_lan_ip() {
  # Linux: ip route get 1.1.1.1
  if command -v ip >/dev/null 2>&1; then
    ip route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src") {print $(i+1); exit}}'
    return
  fi
  # macOS: route + ipconfig
  if command -v route >/dev/null 2>&1 && command -v ipconfig >/dev/null 2>&1; then
    local iface
    iface="$(route get 1.1.1.1 2>/dev/null | awk '/interface:/{print $2; exit}')"
    if [[ -n "${iface:-}" ]]; then
      ipconfig getifaddr "$iface" 2>/dev/null || true
      return
    fi
  fi
  # Fallback: hostname -I
  if command -v hostname >/dev/null 2>&1; then
    hostname -I 2>/dev/null | awk '{print $1}'
    return
  fi
  echo ""
}

cleanup() {
  echo ""
  echo "[main] stopping tmux session: ${TMUX_SESSION}"
  tmux kill-session -t "${TMUX_SESSION}" 2>/dev/null || true
  exit 0
}

trap cleanup INT TERM

# Kill existing session
if tmux has-session -t "${TMUX_SESSION}" 2>/dev/null; then
  echo "[main] tmux session already exists, killing: ${TMUX_SESSION}"
  tmux kill-session -t "${TMUX_SESSION}"
fi

# Start server window
tmux new-session -d -s "${TMUX_SESSION}" -n server \
  "cd \"$(pwd)\" && ROOM_CODE=\"${ROOM_CODE}\" PORT=\"${PORT}\" MAX_CLIENTS=\"${MAX_CLIENTS}\" node server.js"

# Start client window
tmux new-window -t "${TMUX_SESSION}" -n client \
  "cd \"$(pwd)\" && /usr/bin/python3 chat_display_client.py"

# Startup delay
sleep 0.4

LAN_IP="$(get_lan_ip)"
if [[ -z "${LAN_IP}" ]]; then
  LAN_IP="(IP detection failed - use localhost)"
fi

echo "[main] server started in tmux session: ${TMUX_SESSION}"
echo "[main] ROOM_CODE=${ROOM_CODE}  PORT=${PORT}  MAX_CLIENTS=${MAX_CLIENTS}"
echo ""
echo "Access URL:"
echo "  http://${LAN_IP}:${PORT}"
echo ""
echo "Press Ctrl+C to stop (this will also stop server/client)."

# Keep alive (Ctrl+C wait)
while true; do
  if ! tmux has-session -t "${TMUX_SESSION}" 2>/dev/null; then
    echo "[main] tmux session ended."
    exit 0
  fi
  sleep 1
done
