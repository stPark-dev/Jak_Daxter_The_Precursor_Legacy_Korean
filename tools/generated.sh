# The release build outputs that need no ISO, committed under generated/ so CI can package
# without game data. Source this file; build_kr.sh saves them, ci_package.sh restores them.

# paths inside jak-project/
KR_GENERATED_FILES=(
  game/assets/jak1/subtitle/subtitle_lines_ko-KR.json
  game/assets/jak1/subtitle/subtitle_meta_ko-KR.json
  game/assets/jak1/text/game_base_text_ko-KR.json
  game/assets/jak1/text/game_custom_text_ko-KR.json
  game/assets/fonts/jak1_korean_charmap_menu.json
  game/assets/fonts/jak1_korean_charmap_subtitle.json
  goal_src/jak1/pc/kr-font-data.gc
  custom_assets/jak1/texture_overlays/gamefontnew/ascii.24lo.png
  custom_assets/jak1/texture_overlays/gamefontnew/ascii.24hi.png
  custom_assets/jak1/texture_overlays/gamefontnew/ascii.12lo.png
  custom_assets/jak1/texture_overlays/gamefontnew/ascii.12hi.png
)

# Hash of everything the outputs are made from. git hash-object normalizes line endings,
# so Windows and Linux checkouts agree.
kr_inputs_hash() {
  local root=$1
  local files
  files=$(cd "$root" &&
    git -c core.quotePath=false ls-files --cached --others --exclude-standard -- \
      translation fonts tools/kr_font tools/translation tools/text patches tools/build_kr.sh |
    grep -v -E '(^|/)test_[^/]*$' | LC_ALL=C sort |
    while IFS= read -r f; do [ -f "$f" ] && echo "$f"; done)
  (cd "$root" && paste -d ' ' <(echo "$files") <(echo "$files" | git hash-object --stdin-paths) |
    git hash-object --stdin)
}

# copy between jak-project/ and generated/ (direction: save | restore)
kr_generated_copy() {
  local root=$1 direction=$2 f src dst
  for f in "${KR_GENERATED_FILES[@]}"; do
    if [ "$direction" = save ]; then src=$root/jak-project/$f; dst=$root/generated/$f
    else src=$root/generated/$f; dst=$root/jak-project/$f; fi
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
  done
}
