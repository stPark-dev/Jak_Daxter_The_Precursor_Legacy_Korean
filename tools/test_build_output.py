"""Integration checks on the built Korean product files (run after tools/build_kr.sh)."""
import json
from pathlib import Path

J = Path(__file__).resolve().parents[1] / "jak-project"
FONTS = J / "game/assets/fonts"
MENU_MAP = json.loads((FONTS / "jak1_korean_charmap_menu.json").read_text(encoding="utf-8"))
SUB_MAP = json.loads((FONTS / "jak1_korean_charmap_subtitle.json").read_text(encoding="utf-8"))
SUBTIT = (J / "out/jak1/iso/17SUBTIT.TXT").read_bytes()
COMMON = (J / "out/jak1/iso/17COMMON.TXT").read_bytes()
KO_LINES = json.loads((J / "game/assets/jak1/subtitle/subtitle_lines_ko-KR.json").read_text(encoding="utf-8"))


def _hangul_in(obj):
    s = json.dumps(obj, ensure_ascii=False)
    return {c for c in s if 0xAC00 <= ord(c) <= 0xD7A3}


def test_no_raw_utf8_hangul_in_built_text():
    for ch in _hangul_in(KO_LINES) | set(MENU_MAP) | set(SUB_MAP):
        assert ch.encode() not in SUBTIT, ch
        assert ch.encode() not in COMMON, ch


def test_korean_subtitle_lines_are_encoded_with_charmap():
    for ch in _hangul_in(KO_LINES):
        assert bytes(SUB_MAP[ch]) in SUBTIT, ch


KO_BASE = json.loads((J / "game/assets/jak1/text/game_base_text_ko-KR.json").read_text(encoding="utf-8"))


def test_korean_menu_text_uses_menu_charmap():
    for ch in _hangul_in(KO_BASE):
        assert bytes(MENU_MAP[ch]) in COMMON, ch


def test_no_glyph_byte_is_rewritten_by_subtitle_wrap():
    # subtitle.gc print-game-subtitle turns '_' (0x5F) into a space ("라" bug, 2026-10-15)
    for m in (MENU_MAP, SUB_MAP):
        assert all(trail != 0x5F for _, trail in m.values())


# og:kr the Korean language needs a name in the options menu (was "UNKNOWN ID 0", 2026-10-16)
GOAL = J / "goal_src/jak1"
TEXT_DIR = J / "game/assets/jak1/text"


def test_korean_has_a_language_name_text_id():
    assert "(korean #x1121)" in (GOAL / "engine/ui/text-h.gc").read_text(encoding="utf-8")


def test_korean_is_listed_in_pc_language_menus():
    src = (GOAL / "pc/progress-pc.gc").read_text(encoding="utf-8")
    for name in ("*language-remap-info-pc*", "*text-languages*", "*subtitle-languages*"):
        block = src[src.index(name):]
        block = block[:block.index("))")]
        assert "korean" in block.split(), name


def test_every_custom_text_file_names_korean():
    for p in TEXT_DIR.glob("game_custom_text_*.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        want = "한국어" if p.name.endswith("ko-KR.json") else "KOREAN"
        assert d.get("1121") == want, p.name


def test_korean_language_name_is_encoded_in_korean_common_text():
    assert b"".join(bytes(MENU_MAP[c]) for c in "한국어") in COMMON


def test_credits_keep_korean_text_language():
    # credits.gc swaps text-language to the voice language during credits; Korean has its own
    # credit headings (base b00..cbd), so Korean must not be swapped to English (2026-10-16)
    src = (GOAL / "engine/ui/credits.gc").read_text(encoding="utf-8")
    assert "(pc-language korean)" in src


def test_korean_base_text_has_credit_headings():
    assert KO_BASE.get("b39", "").startswith("~33L") and KO_BASE["b39"] != "~33LVOICE ACTORS"
