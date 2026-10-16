#!/bin/bash
# Fetch OpenGOAL at the supported commit, apply the Korean patch, build, and extract your ISO.
# usage: tools/setup_opengoal.sh <path to your Jak 1 NTSC-U (SCUS-97124) ISO>
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
J=$ROOT/jak-project
OPENGOAL_COMMIT=b6c8430c0b0a5cb139b939bcf0ffd25285b896c7
ISO=${1:?usage: $0 <jak1.iso>}

mkdir -p "$ROOT/source"
ln -sf "$(realpath "$ISO")" "$ROOT/source/jak1.iso"

if [ ! -d "$J/.git" ]; then
  git clone https://github.com/open-goal/jak-project.git "$J"
fi
git -C "$J" checkout --detach "$OPENGOAL_COMMIT"
git -C "$J" apply "$ROOT/patches/opengoal-kr.patch"

(cd "$J" && cmake --preset=Release-linux-clang && cmake --build build/Release/bin -j"$(nproc)")
(cd "$J" && build/Release/bin/decompiler/extractor -e -v -d --disable-ansi "$ROOT/source/jak1.iso" \
   --decomp-config-override '{"save_texture_pngs": true}')
python3 "$ROOT/tools/translation/cli.py" init "$J" "$ROOT/translation"
echo "OpenGOAL ready. Next: tools/build_kr.sh release"
