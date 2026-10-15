"""Integration test on the real OpenGOAL sources (requires the decompiled game_text.txt)."""
import json

import cli

from pathlib import Path

JAK = str(Path(__file__).resolve().parents[2] / "jak-project")


def test_init_creates_full_denominator(tmp_path):
    cli.init(JAK, tmp_path)
    counts = cli.counts(tmp_path)
    assert counts["text/base"] == 279
    assert counts["text/custom"] == 231
    assert counts["speakers"] == 27
    assert counts["subtitles"] == 1502  # + 27 speakers = 1529 strings
    e = json.loads((tmp_path / "text_base.json").read_text(encoding="utf-8"))[0]
    assert set(e) >= {"id", "src", "ko", "state", "note"}


def test_init_twice_keeps_work(tmp_path):
    cli.init(JAK, tmp_path)
    p = tmp_path / "speakers.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data[0].update(ko="덱스터", state="in_progress")
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    cli.init(JAK, tmp_path)
    again = json.loads(p.read_text(encoding="utf-8"))
    assert again[0]["ko"] == "덱스터"
