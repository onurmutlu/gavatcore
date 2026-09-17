#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PYTHON="$ROOT/.venv/bin/python"
LAUNCHER="$ROOT/launchers/baron_bot_launcher.py"
PID_FILE="${TMPDIR:-/tmp}/gavatcore-baron-live.pid"
LOCK_FILE="$ROOT/data/baron_live.lock"
LOG_FILE="$ROOT/logs/baron_live.log"

mkdir -p "$ROOT/logs"

read_pid() {
  if [ -s "$LOCK_FILE" ]; then
    tr -cd '0-9' < "$LOCK_FILE"
  elif [ -f "$PID_FILE" ]; then
    tr -cd '0-9' < "$PID_FILE"
  fi
}

is_running() {
  pid=$(read_pid)
  [ -n "$pid" ] || return 1
  if ! kill -0 "$pid" 2>/dev/null; then
    "$PYTHON" "$LAUNCHER" campaign-alive >/dev/null 2>&1 && return 0
    return 1
  fi
  command=$(ps -p "$pid" -o command= 2>/dev/null || true)
  # Restricted shells may deny process inspection even when kill -0 confirms it.
  [ -z "$command" ] && return 0
  case "$command" in
    *baron_bot_launcher.py*start*) return 0 ;;
    *) return 1 ;;
  esac
}

start_live() {
  if is_running; then
    echo "Baron zaten çalışıyor (PID $(read_pid))."
    return 0
  fi
  cd "$ROOT"
  nohup "$PYTHON" "$LAUNCHER" start >> "$LOG_FILE" 2>&1 &
  pid=$!
  printf '%s\n' "$pid" > "$PID_FILE"
  sleep 3
  if is_running; then
    echo "Baron canlı yayın başladı (PID $pid)."
    echo "Log: $LOG_FILE"
  else
    echo "Baron başlatılamadı. Son loglar:"
    tail -n 40 "$LOG_FILE" || true
    return 1
  fi
}

stop_live() {
  if ! is_running; then
    echo "Baron çalışmıyor."
    return 0
  fi
  pid=$(read_pid)
  kill "$pid"
  count=0
  while kill -0 "$pid" 2>/dev/null && [ "$count" -lt 20 ]; do
    sleep 1
    count=$((count + 1))
  done
  if kill -0 "$pid" 2>/dev/null; then
    echo "Baron kapanma süresini aştı (PID $pid)."
    return 1
  fi
  : > "$PID_FILE"
  echo "Baron durduruldu."
}

case "${1:-help}" in
  run|foreground)
    cd "$ROOT"
    printf '%s\n' "$$" > "$PID_FILE"
    exec "$PYTHON" "$LAUNCHER" start
    ;;
  live)
    cd "$ROOT"
    "$PYTHON" "$LAUNCHER" activate-candidates
    start_live
    ;;
  start) start_live ;;
  stop) stop_live ;;
  restart)
    stop_live
    start_live
    ;;
  status)
    if is_running; then
      echo "Baron çalışıyor (PID $(read_pid))."
    else
      echo "Baron çalışmıyor."
    fi
    cd "$ROOT"
    "$PYTHON" "$LAUNCHER" campaign-report
    ;;
  report)
    cd "$ROOT"
    "$PYTHON" "$LAUNCHER" campaign-report
    ;;
  scan)
    cd "$ROOT"
    "$PYTHON" "$LAUNCHER" scan-groups
    ;;
  activate)
    shift
    cd "$ROOT"
    "$PYTHON" "$LAUNCHER" activate-candidates "$@"
    ;;
  disable)
    cd "$ROOT"
    "$PYTHON" "$LAUNCHER" campaign-disable
    ;;
  logs)
    lines=${2:-80}
    tail -n "$lines" "$LOG_FILE"
    ;;
  follow)
    tail -f "$LOG_FILE"
    ;;
  *)
    echo "Kullanım: $0 {run|live|start|stop|restart|status|report|scan|activate|disable|logs [satır]|follow}"
    exit 1
    ;;
esac
