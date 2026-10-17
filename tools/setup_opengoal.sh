#!/bin/bash
# Fetch OpenGOAL at the supported commit, apply the Korean patch, build, and extract your ISO.
# usage: tools/setup_opengoal.sh <path to your Jak 1 NTSC-U (SCUS-97124) ISO>
# Linux, or Windows in Git Bash (see README).
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
J=$ROOT/jak-project
OPENGOAL_COMMIT=b6c8430c0b0a5cb139b939bcf0ffd25285b896c7
ISO=${1:?usage: $0 <jak1.iso>}
source "$ROOT/tools/platform.sh"

mkdir -p "$ROOT/source"
realpath "$ISO" > "$ROOT/source/iso_path"
kr_platform "$ROOT"

if [ ! -d "$J/.git" ]; then
  # no CRLF conversion on Windows, or the patch will not apply
  git clone -c core.autocrlf=false https://github.com/open-goal/jak-project.git "$J"
fi
git -C "$J" checkout --detach "$OPENGOAL_COMMIT"
git -C "$J" apply "$ROOT/patches/opengoal-kr.patch"

(cd "$J" && cmake --preset="$KR_PRESET" && cmake --build "$KR_BUILD_DIR" -j"$(nproc)")
(cd "$J" && "$KR_EXTRACTOR" -e -v -d --disable-ansi "$KR_ISO")
"$KR_PYTHON" "$ROOT/tools/translation/cli.py" init "$J" "$ROOT/translation"
echo "OpenGOAL ready. Next: tools/build_kr.sh release"
