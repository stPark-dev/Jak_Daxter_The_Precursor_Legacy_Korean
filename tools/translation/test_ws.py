"""Tests for the translation workspace: baseline, sync, checks and export."""
import pytest

import ws

from pathlib import Path

FONT_DB = str(Path(__file__).resolve().parents[2] / "jak-project/common/util/font/dbs/font_db_jak1.cpp")

LINES = {
    "cutscenes": {"intro": ["HELLO JAK.", "WHAT?"]},
    "hints": {"H01": ["GOT ~D CELLS!"]},
    "speakers": {"DAXTER": "DAXTER", "SAMOS": "SAMOS"},
}
META = {
    "cutscenes": {"intro": [
        {"clear": False, "frame_start": 0, "speaker": "SAMOS"},
        {"clear": True, "frame_start": 10, "speaker": ""},
        {"clear": False, "frame_start": 12, "speaker": "DAXTER"},
    ]},
    "hints": {"H01": {"id": "1", "lines": [{"clear": False, "frame_start": 0, "speaker": "DAXTER"}]}},
}
BASE = {"16e": "PRESS START", "200": "<PAD_X> = YES"}
CUSTOM = {"1000": "CAMERA OPTIONS"}


@pytest.fixture
def baseline():
    return ws.build_baseline(LINES, META, BASE, CUSTOM)


def _entry(units, unit, i=0):
    return units[unit][i]


def test_cutscene_speakers_skip_clear_meta(baseline):
    e0, e1 = baseline["cutscene/intro"]
    assert (e0["id"], e0["speaker"], e0["src"]) == ("cut:intro:0", "SAMOS", "HELLO JAK.")
    assert (e1["id"], e1["speaker"]) == ("cut:intro:1", "DAXTER")


def test_hints_speakers_and_text_units(baseline):
    assert _entry(baseline, "hint/H01")["speaker"] == "DAXTER"
    assert _entry(baseline, "text/base")["id"] == "base:16e"
    assert _entry(baseline, "text/custom")["id"] == "custom:1000"
    assert _entry(baseline, "speakers")["id"] == "speaker:DAXTER"


def test_sync_keeps_translation_when_source_unchanged(baseline):
    work = {"cut:intro:0": {"ko": "안녕, 잭.", "state": "in_progress", "note": ""}}
    unit = ws.sync(baseline["cutscene/intro"], work)
    assert unit[0]["ko"] == "안녕, 잭." and unit[0]["state"] == "in_progress"
    assert unit[1]["state"] == "untranslated" and unit[1]["ko"] == ""


def test_sync_invalidates_translation_when_source_changed(baseline):
    work = {"cut:intro:0": {"ko": "안녕, 잭.", "state": "in_progress", "src": "HI JAK."}}
    e = ws.sync(baseline["cutscene/intro"], work)[0]
    assert e["state"] == "untranslated" and e["ko"] == "" and e["stale_ko"] == "안녕, 잭."


def test_allowed_chars_come_from_font_db():
    allowed = ws.allowed_chars(FONT_DB)
    assert {"A", "Z", "0", "?", "!", "'"} <= allowed
    assert "a" not in allowed and "…" not in allowed


@pytest.mark.parametrize("src,ko,problem", [
    ("GOT ~D CELLS!", "셀 ~D개 획득!", None),
    ("GOT ~D CELLS!", "셀 획득!", "format"),
    ("<PAD_X> = YES", "예 = <PAD_X>", None),
    ("<PAD_X> = YES", "예", "token"),
    ("HELLO", "Hello 잭", "char"),
    ("WAIT...", "잠깐…", "char"),
])
def test_check_entry(src, ko, problem):
    problems = ws.check_entry({"id": "x", "src": src, "ko": ko}, ws.allowed_chars(FONT_DB))
    if problem is None:
        assert problems == []
    else:
        assert any(p.startswith(problem) for p in problems)


def test_export_dev_falls_back_to_source_and_release_refuses(baseline):
    units = {k: ws.sync(v, {}) for k, v in baseline.items()}
    units["cutscene/intro"][0].update(ko="안녕, 잭.", state="in_progress")
    out = ws.export(units, LINES, policy="dev")
    assert out["subtitle_lines"]["cutscenes"]["intro"] == ["안녕, 잭.", "WHAT?"]
    assert out["base_text"]["16e"] == "PRESS START"
    with pytest.raises(ws.NotEligible):
        ws.export(units, LINES, policy="release")


def test_chars_used_by_the_english_source_are_allowed():
    # '"' passes through the encoder unchanged and is drawn from the original sheet
    allowed = ws.allowed_chars(FONT_DB, source_texts=['SAY "HI"'])
    assert '"' in allowed
    assert ws.check_entry({"id": "x", "src": 'SAY "HI"', "ko": '"안녕"'}, allowed) == []


def test_text_kept_identical_to_source_skips_the_char_check():
    # e.g. language names (ESPAÑOL, にほんご): drawn by the original encoder exactly as in English
    allowed = ws.allowed_chars(FONT_DB)
    assert ws.check_entry({"id": "x", "src": "ESPAÑOL", "ko": "ESPAÑOL"}, allowed) == []
    assert ws.check_entry({"id": "x", "src": "ESPAÑOL", "ko": "에스파뇰…"}, allowed) != []


def test_composed_glyphs_from_the_replace_table_are_allowed():
    # Ñ is drawn by replace_info_jak1 (N + tilde), shared by the v1 and v2 banks
    allowed = ws.allowed_chars(FONT_DB)
    assert "Ñ" in allowed
