#!/bin/bash
# Build the Korean patch into the local OpenGOAL tree.
# usage: tools/build_kr.sh [dev|release]
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
J=$ROOT/jak-project
POLICY=${1:-dev}
MENU_FONT=$ROOT/fonts/Jua-Regular.ttf          # D-002
SUB_FONT=$ROOT/fonts/Pretendard-SemiBold.otf   # D-002
source "$ROOT/tools/platform.sh"
kr_platform "$ROOT"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

"$KR_PYTHON" "$ROOT/tools/translation/cli.py" export "$J" "$ROOT/translation" "$POLICY"
cat "$J"/game/assets/jak1/text/*_ko-KR.json > "$TMP/menu.txt"
cat "$J"/game/assets/jak1/subtitle/subtitle_lines_ko-KR.json > "$TMP/subtitle.txt"
(cd "$ROOT/tools/kr_font" && "$KR_PYTHON" build_font.py \
  --set menu "$TMP/menu.txt" "$MENU_FONT" \
  --set subtitle "$TMP/subtitle.txt" "$SUB_FONT" \
  --out-tex "$J/custom_assets/jak1/texture_overlays/gamefontnew" \
  --out-goal "$J/goal_src/jak1/pc/kr-font-data.gc" \
  --out-charmap-dir "$J/game/assets/fonts")
rm -f "$J/game/assets/fonts/jak1_korean_charmap.json"
# full sheets from before the overlay switch would win over the overlays
rm -rf "$J/custom_assets/jak1/texture_replacements/gamefontnew"
(cd "$J" && "$KR_EXTRACTOR" -d -c --disable-ansi "$KR_ISO" > "$ROOT/build_kr.log" 2>&1) \
  || { grep -a -i "error" "$ROOT/build_kr.log" | head; exit 1; }
echo "$POLICY" > "$ROOT/source/last_build"  # package_kr.sh only ships release builds
echo "built ($POLICY); log: $ROOT/build_kr.log"
