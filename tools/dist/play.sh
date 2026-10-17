#!/bin/bash
# Start the game. --portable keeps settings and saves next to gk, apart from other OpenGOAL installs.
cd "$(dirname "$0")"
if [ ! -d data/out/jak1 ]; then
  echo "먼저 ./install.sh 로 설치하세요." >&2
  exit 1
fi
exec ./gk --portable -- -boot -fakeiso
