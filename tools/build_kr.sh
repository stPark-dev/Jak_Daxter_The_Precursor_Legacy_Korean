#!/bin/bash
# Build the Korean patch into the local OpenGOAL tree.
# usage: tools/build_kr.sh [dev|release]
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
J=$ROOT/jak-project
POLICY=${1:-dev}
MENU_FONT=$ROOT/fonts/Jua-Regular.ttf          # D-002
SUB_FONT=$ROOT/fonts/Pretendard-SemiBold.otf   # D-002
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

python3 "$ROOT/tools/translation/cli.py" export "$J" "$ROOT/translation" "$POLICY"
cat "$J"/game/assets/jak1/text/*_ko-KR.json > "$TMP/menu.txt"
cat "$J"/game/assets/jak1/subtitle/subtitle_lines_ko-KR.json > "$TMP/subtitle.txt"
(cd "$ROOT/tools/kr_font" && python3 build_font.py \
  --orig-dir "$J/decompiler_out/jak1/textures/gamefontnew" \
  --set menu "$TMP/menu.txt" "$MENU_FONT" \
  --set subtitle "$TMP/subtitle.txt" "$SUB_FONT" \
  --out-tex "$J/custom_assets/jak1/texture_replacements/gamefontnew" \
  --out-goal "$J/goal_src/jak1/pc/kr-font-data.gc" \
  --out-charmap-dir "$J/game/assets/fonts")
rm -f "$J/game/assets/fonts/jak1_korean_charmap.json"
(cd "$J" && build/Release/bin/decompiler/extractor -d -c --disable-ansi "$ROOT/source/jak1.iso" > "$ROOT/build_kr.log" 2>&1) \
  || { grep -a -i "error" "$ROOT/build_kr.log" | head; exit 1; }
echo "built ($POLICY); log: $ROOT/build_kr.log"
