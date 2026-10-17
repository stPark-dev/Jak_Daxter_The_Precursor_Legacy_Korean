#!/bin/bash
# Package the prebuilt Korean patch: patched OpenGOAL binaries + data, no game data.
# Users run install.bat/install.sh with their own ISO (extract, decompile, compile).
# usage: tools/package_kr.sh <version>   (after tools/build_kr.sh release)
# Linux, or Windows in Git Bash through tools\kr.bat package.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
J=$ROOT/jak-project
VERSION=${1:?usage: $0 <version>}
source "$ROOT/tools/platform.sh"
kr_platform "$ROOT"

if [ "$(cat "$ROOT/source/last_build" 2>/dev/null)" != release ]; then
  echo "run tools/build_kr.sh release first (only release builds are packaged)" >&2
  exit 1
fi

# static binaries run without the Visual C++ runtime / system libraries
(cd "$J" && cmake --preset="$KR_STATIC_PRESET" -B "$KR_STATIC_BUILD_DIR" > /dev/null \
  && cmake --build "$KR_STATIC_BUILD_DIR" --target gk goalc extractor)

NAME=jak1-korean-$VERSION-$KR_DIST_OS
OUT=$ROOT/dist/$NAME
rm -rf "$OUT"
mkdir -p "$OUT/data/log" "$OUT/data/launcher"
for b in "${KR_STATIC_BINS[@]}"; do
  cp "$J/$KR_STATIC_BUILD_DIR/$b" "$OUT/"
done
if [ "$KR_DIST_OS" = windows ]; then
  # the binaries still import the VC++ runtime; ship it app-local (redistributable) so a PC
  # without the Visual C++ Redistributable runs them. VCToolsRedistDir comes from vcvars64.
  CRT=$(ls -d "$(cygpath -u "${VCToolsRedistDir:?run through tools\\kr.bat package}")"x64/Microsoft.VC*.CRT | tail -n 1)
  cp "$CRT"/{msvcp140.dll,vcruntime140.dll,vcruntime140_1.dll} "$OUT/"
fi

# same data layout as OpenGOAL's .github/scripts/releases/extract_build_*.sh. Only tracked
# files and our generated ones (untracked, not ignored): extraction output is ignored.
# Jak 2/3/X files are left out, the package only runs Jak 1.
DATA_DIRS=(decompiler/config goal_src game/assets game/graphics/opengl_renderer/shaders custom_assets)
(cd "$J" && git -c core.quotePath=false ls-files --cached --others --exclude-standard -- "${DATA_DIRS[@]}") |
  grep -v -E '(^|/)(jak2|jak3|jakx)(/|$)' |
  while IFS= read -r f; do
    [ -f "$J/$f" ] || continue
    mkdir -p "$OUT/data/$(dirname "$f")"
    cp "$J/$f" "$OUT/data/$f"
  done
cp "$J/.github/scripts/releases/error-code-metadata.json" "$OUT/data/launcher/"

cp "$ROOT/tools/dist/"* "$OUT/"
if [ "$KR_DIST_OS" = windows ]; then rm "$OUT"/*.sh; else rm "$OUT"/*.bat; chmod +x "$OUT"/*.sh; fi
mkdir -p "$OUT/licenses"
cp "$J/LICENSE" "$OUT/licenses/OpenGOAL-LICENSE.txt"
cp "$ROOT/fonts/"*-OFL.txt "$OUT/licenses/"

# the package must not carry game data
leaks=$(cd "$OUT" && find . -ipath '*iso_data*' -o -ipath '*decompiler_out*' \
  -o -ipath '*texture_replacements/gamefontnew*' -o -iname '*.iso' -o -iname '*.cgo' \
  -o -iname '*.dgo' -o -iname '*.str' -o -iname '*.vag')
if [ -n "$leaks" ]; then
  echo "game data in package:" >&2
  echo "$leaks" >&2
  exit 1
fi
for f in "$OUT"/data/custom_assets/jak1/texture_overlays/gamefontnew/ascii.{24lo,24hi,12lo,12hi}.png \
         "$OUT"/data/goal_src/jak1/pc/kr-font-data.gc; do
  [ -f "$f" ] || { echo "missing from package: $f" >&2; exit 1; }
done

cd "$ROOT/dist"
rm -f "$NAME".zip "$NAME".tar.gz
if [ "$KR_DIST_OS" = windows ]; then
  powershell -NoProfile -Command "Compress-Archive -Path '$NAME' -DestinationPath '$NAME.zip'"
  echo "packaged: dist/$NAME.zip"
else
  tar czf "$NAME.tar.gz" "$NAME"
  echo "packaged: dist/$NAME.tar.gz"
fi
