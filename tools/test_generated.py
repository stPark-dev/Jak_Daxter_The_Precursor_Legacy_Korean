"""Tests for tools/generated.sh (the ISO-free release outputs CI packages from)."""
import subprocess
from pathlib import Path

from test_platform import _bash

GENERATED = Path(__file__).resolve().parent / "generated.sh"
ROOT = Path(__file__).resolve().parents[1]


def _sh(script, cwd=None):
    return subprocess.run([_bash(), "-c", f'source "{GENERATED}"; {script}'], cwd=cwd,
                          capture_output=True, text=True, check=True).stdout


def _repo(tmp_path):
    for d in ("translation", "tools/kr_font", "patches"):
        (tmp_path / d).mkdir(parents=True)
    (tmp_path / "translation/a.json").write_text("[]\n")
    (tmp_path / "tools/kr_font/build_font.py").write_text("x = 1\n")
    (tmp_path / "tools/kr_font/test_build_font.py").write_text("t = 1\n")
    (tmp_path / "patches/opengoal-kr.patch").write_text("p\n")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    return tmp_path


def _hash(root):
    return _sh(f'kr_inputs_hash "{root}"').strip()


def test_inputs_hash_follows_translations_and_tools_but_not_tests(tmp_path):
    root = _repo(tmp_path)
    h = _hash(root)
    (root / "tools/kr_font/test_build_font.py").write_text("t = 2\n")
    assert _hash(root) == h
    (root / "translation/a.json").write_text('[{"ko": "가"}]\n')
    assert _hash(root) != h


def test_inputs_hash_ignores_line_endings(tmp_path):
    root = _repo(tmp_path)
    subprocess.run(["git", "-C", str(root), "config", "core.autocrlf", "true"], check=True)
    h = _hash(root)
    (root / "translation/a.json").write_bytes(b"[]\r\n")
    assert _hash(root) == h


def test_generated_files_cover_build_outputs():
    # every jak-project path build_kr.sh / cli.py export / build_font.py writes
    files = set(_sh('printf "%s\\n" "${KR_GENERATED_FILES[@]}"').split())
    build = (ROOT / "tools/build_kr.sh").read_text(encoding="utf-8")
    cli = (ROOT / "tools/translation/cli.py").read_text(encoding="utf-8")
    assert "texture_overlays/gamefontnew" in build and "kr-font-data.gc" in build
    for name in ("subtitle_lines_ko-KR.json", "subtitle_meta_ko-KR.json", "game_base_text_ko-KR.json",
                 "game_custom_text_ko-KR.json"):
        assert name in cli
        assert any(f.endswith(name) for f in files), name
    assert {f"custom_assets/jak1/texture_overlays/gamefontnew/ascii.{s}.png"
            for s in ("24lo", "24hi", "12lo", "12hi")} <= files
    assert "goal_src/jak1/pc/kr-font-data.gc" in files
    assert {"game/assets/fonts/jak1_korean_charmap_menu.json",
            "game/assets/fonts/jak1_korean_charmap_subtitle.json"} <= files


def test_committed_snapshot_is_complete():
    files = _sh('printf "%s\\n" "${KR_GENERATED_FILES[@]}"').split()
    for f in files + ["INPUTS_HASH"]:
        assert (ROOT / "generated" / f).is_file(), f
