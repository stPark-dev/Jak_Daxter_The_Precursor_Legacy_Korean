#!/bin/bash
# QA runtime: OpenGOAL game in a small visible window + a persistent goalc REPL fed by a FIFO.
# Settings come from tools/qa/settings-template (960x540 window, Korean text/subtitles = 17).
#   runtime.sh start | stop | send '<goal form>' [wait_seconds]
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
J=$ROOT/jak-project
QA=$ROOT/.qa
mkdir -p "$QA"

stop() {
  for f in gk goalc holder; do
    [ -f "$QA/$f.pid" ] && kill "$(cat "$QA/$f.pid")" 2>/dev/null || true
    rm -f "$QA/$f.pid"
  done
}

case "${1:-}" in
  stop) stop ;;
  start)
    stop; sleep 1
    mkdir -p "$QA/cfg/OpenGOAL/jak1/settings"
    cp "$ROOT"/tools/qa/settings-template/* "$QA/cfg/OpenGOAL/jak1/settings/"
    rm -f "$QA/repl.in"; mkfifo "$QA/repl.in"
    cd "$J"
    DISPLAY=${DISPLAY:-:1} setsid build/Release/bin/game/gk --config-path "$QA/cfg" --disable-ansi \
      -- -boot -fakeiso -debug > "$QA/gk.log" 2>&1 < /dev/null & echo $! > "$QA/gk.pid"
    setsid sleep 86400 > "$QA/repl.in" 2>/dev/null < /dev/null & echo $! > "$QA/holder.pid"
    setsid build/Release/bin/goalc/goalc --disable-ansi --game jak1 < "$QA/repl.in" > "$QA/repl.log" 2>&1 &
    echo $! > "$QA/goalc.pid"
    for _ in $(seq 60); do
      W=$(xwininfo -root -tree 2>/dev/null | grep '"OpenGOAL' | awk '{print $1}' | head -1 || true)
      [ -n "$W" ] && break; sleep 1
    done
    echo "$W" > "$QA/win.id"
    sleep 15
    "$ROOT/tools/qa/runtime.sh" send '(mi)' 40; "$ROOT/tools/qa/runtime.sh" send '(lt)' 5
    echo "ready (window $W)"
    ;;
  send)
    echo "$2" > "$QA/repl.in"
    sleep "${3:-1}"
    sed 's/\x1b\[[0-9;]*m//g' "$QA/repl.log" | grep -v "^\[ *[0-9]*%\]\|Build Game Text" | tail -3
    ;;
  *) echo "usage: $0 start|stop|send <form> [wait]"; exit 1 ;;
esac
