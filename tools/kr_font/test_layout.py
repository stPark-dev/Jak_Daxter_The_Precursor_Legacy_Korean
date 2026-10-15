"""Tests for the Jak 1 Korean font layout / encoding rules (PoC)."""
import pytest

import layout as L

# 0x5F: subtitle word-wrap (subtitle.gc print-game-subtitle) turns '_' into a space
FORBIDDEN_TRAIL = {0x00, 0x0A, 0x0D, 0x20, 0x5F, 0x7E}


def test_trail_bytes_are_safe_and_unique():
    trails = L.trail_bytes()
    assert len(trails) == L.GLYPHS_PER_PAGE == 185
    assert len(set(trails)) == len(trails)
    for b in trails:
        assert b not in FORBIDDEN_TRAIL
        assert 0x21 <= (b & 0x7F) <= 0x7D  # never a control, space or '~'


def test_lead_bytes_avoid_reserved_codes():
    leads = L.lead_bytes()
    assert 1 not in leads  # existing kanji page
    assert 3 not in leads  # "large space" in jak1-v2 encoding
    assert not {0, 10, 13, 126} & set(leads)
    assert {11, 12, 14, 15} <= set(leads)  # capacity extension (2026-10-15)


def test_capacity_covers_two_typefaces():
    # menu (Jua) + subtitle (Pretendard) glyphs are separate; forecast > 1,295
    assert L.capacity() >= 2000
    assert len(L.free_cells()) >= L.entries_needed(L.capacity())


def test_code_for_index_is_unique_and_two_bytes():
    n = L.capacity()
    codes = [L.code_for_index(i) for i in range(n)]
    assert len(set(codes)) == n
    for lead, trail in codes:
        assert lead in L.lead_bytes()
        assert trail in L.trail_bytes()


def test_code_for_index_out_of_range():
    with pytest.raises(ValueError):
        L.code_for_index(L.capacity())


def test_table_index_does_not_touch_existing_entries():
    # existing *font24-table* has 289 entries (0..288); page 1 owns 239..366.
    idx = {L.table_index(*L.code_for_index(i)) for i in range(L.capacity())}
    assert min(idx) > 366
    assert max(idx) < L.table_length()


def test_lo_and_hi_trail_share_one_table_entry():
    lead = L.lead_bytes()[0]
    assert L.table_index(lead, 0x21) == L.table_index(lead, 0xA1)


def test_free_cells_avoid_original_region_and_fit_canvas():
    cells = L.free_cells()
    assert len(cells) >= L.entries_needed(L.capacity())
    for col, row in cells:
        x0, y0 = col * L.CELL_W, row * L.CELL_H
        assert x0 + L.CELL_W <= L.CANVAS_W and y0 + L.CELL_H <= L.CANVAS_H
        in_orig = x0 < L.ORIG_REGION_W and y0 < L.ORIG_REGION_H
        assert not in_orig


def test_entry_uv_glyph_box_stays_inside_cell():
    for col, row in L.free_cells()[:50]:
        u, v = L.cell_uv(col, row)
        x0, y0 = col * L.CELL_W / L.CANVAS_W, row * L.CELL_H / L.CANVAS_H
        assert x0 <= u and u + L.ST_W <= x0 + L.CELL_W / L.CANVAS_W
        assert y0 <= v and v + L.ST_H <= y0 + L.CELL_H / L.CANVAS_H


def test_scaled_original_uv_points_at_same_upscaled_pixel():
    # 'B' in original 24lo: x=0.0039 y=0.3144 on a 256x512 texture
    u, v = L.scale_orig_uv(0.0039, 0.3144)
    assert u * L.CANVAS_W == pytest.approx(0.0039 * 256 * L.SCALE)
    assert v * L.CANVAS_H == pytest.approx(0.3144 * 512 * L.SCALE)
