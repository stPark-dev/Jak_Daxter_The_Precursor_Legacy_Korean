"""Tests for build_font: overlay sheets, GOAL data and charmap output."""
import json
from pathlib import Path

import pytest

import build_font as B
import layout as L

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
NANUM = "/usr/share/fonts/truetype/nanum/NanumSquareRoundEB.ttf"
MENU_FONT = str(Path(__file__).resolve().parents[2] / "fonts" / "Jua-Regular.ttf")  # shipped, works on every OS


def test_overlay_has_no_original_pixels():
    sheet = B.overlay_sheet(full_res=True, glyphs={}, fonts={})
    assert sheet.size == (L.CANVAS_W, L.CANVAS_H)
    assert sheet.getextrema()[3] == (0, 0)


def test_overlay_half_res_for_small_font():
    sheet = B.overlay_sheet(full_res=False, glyphs={}, fonts={})
    assert sheet.size == (L.CANVAS_W // 2, L.CANVAS_H // 2)


def test_glyph_drawn_in_its_cell_with_ps2_alpha():
    cell = L.free_cells()[0]
    sheet = B.overlay_sheet(full_res=True,
                            glyphs={cell: ("menu", "한")}, fonts={"menu": B.load_font(MENU_FONT, full_res=True)})
    col, row = cell
    box = (col * L.CELL_W, row * L.CELL_H, (col + 1) * L.CELL_W, (row + 1) * L.CELL_H)
    alphas = [p[3] for p in sheet.crop(box).getdata()]
    assert max(alphas) == 128  # PS2 full alpha, never 255
    assert sum(a > 0 for a in alphas) > 50


@pytest.mark.skipif(not (Path(FONT).exists() and Path(NANUM).exists()),
                    reason="needs the Linux fonts-noto-cjk and fonts-nanum packages")
def test_load_font_uses_korean_face_of_ttc_and_first_face_of_ttf():
    assert B.load_font(FONT, full_res=True).getname()[0] == "Noto Sans CJK KR"
    assert "NanumSquareRound" in B.load_font(NANUM, full_res=True).getname()[0]


def test_plan_splits_lo_and_hi_glyphs():
    plan = B.plan({"menu": "가나"})
    assert plan.codes == {("menu", "가"): L.code_for_index(0), ("menu", "나"): L.code_for_index(1)}
    assert all(t < 0x80 for _, t in plan.codes.values())  # first 93 go to lo
    assert set(plan.lo.values()) == {("menu", "가"), ("menu", "나")} and plan.hi == {}


def test_plan_gives_each_typeface_its_own_codes():
    plan = B.plan({"menu": "가", "subtitle": "가나"})
    assert len(plan.codes) == 3
    assert plan.codes[("menu", "가")] != plan.codes[("subtitle", "가")]


def test_plan_rejects_non_hangul_and_duplicates_are_merged():
    with pytest.raises(ValueError):
        B.plan({"menu": "가A"})
    assert len(B.plan({"menu": "가가나"}).codes) == 2


def test_goal_data_lists_every_entry():
    plan = B.plan({"menu": "가나다"})
    src = B.goal_data(plan)
    assert f"(define *kr-font-table-length* {L.table_length()})" in src
    for idx in plan.entry_cells:
        assert f" {idx} " in src or f" {idx})" in src


def test_charmap_per_typeface():
    plan = B.plan({"menu": "가", "subtitle": "가"})
    menu = json.loads(B.charmap_json(plan, "menu"))
    sub = json.loads(B.charmap_json(plan, "subtitle"))
    assert menu["가"] == list(L.code_for_index(0))
    assert sub["가"] == list(L.code_for_index(1))
