"""Tests for the subtitle reading-speed heuristic (flags candidates only)."""
import timing

META = [
    {"clear": False, "frame_start": 0, "speaker": "SAMOS"},
    {"clear": False, "frame_start": 30, "speaker": "SAMOS"},
    {"clear": True, "frame_start": 90, "speaker": ""},
    {"clear": False, "frame_start": 100, "speaker": "DAXTER"},
]


def test_durations_follow_next_event_and_skip_clear():
    assert timing.durations(META, fps=30) == [1.0, 2.0, None]


def test_flags_lines_faster_than_limit():
    entries = [{"id": "a", "ko": "가" * 20}, {"id": "b", "ko": "가나다"}, {"id": "c", "ko": "가"}]
    flagged = timing.flag(entries, timing.durations(META, fps=30), max_cps=12)
    assert [f["id"] for f in flagged] == ["a"]
    assert flagged[0]["cps"] == 20.0


def test_open_ended_lines_use_english_length_estimate():
    # last line has no next event: estimate duration from the English length (13.6 chars/s)
    entries = [{"id": "x", "src": "A" * 27, "ko": "가" * 30}]
    flagged = timing.flag(entries, [None], max_cps=12)
    assert flagged and flagged[0]["estimated"]
    assert timing.flag([{"id": "y", "src": "A" * 27, "ko": "가" * 20}], [None], max_cps=12) == []
