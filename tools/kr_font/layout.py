"""Layout and encoding rules for the Jak 1 Korean font (OpenGOAL).

Encoding: a Korean glyph is two bytes <lead><trail>.
  * lead selects a code page (byte 1 is the existing kanji page, so we start at 2).
  * the font table entry is 239 + 128*(lead-1) + (trail & 0x7F), matching the
    GOAL draw-string / get-string-length patch.
  * trail bit 7 selects the "hi" texture, otherwise "lo"; both share the entry UV.

Texture: the original glyph sheet is upscaled by SCALE and kept in the top-left
corner of a larger canvas. All UVs are fractions, so the 24 and 12 fonts share one
layout (the 12-font canvas is just half the resolution).
"""

# original 24-font sheet and canvas (pixels)
ORIG_W, ORIG_H = 256, 512
SCALE = 2
CANVAS_W, CANVAS_H = 2048, 2048
ORIG_REGION_W, ORIG_REGION_H = ORIG_W * SCALE, ORIG_H * SCALE

# original grid step 0.09375 x 0.0625 of the sheet = 24 x 32 px, upscaled
CELL_W, CELL_H = 24 * SCALE, 32 * SCALE
# glyph offset inside a cell (original tables use ~1px inset)
INSET_X, INSET_Y = 1, 0

# glyph UV extent (font-work size-st), original values rescaled to the canvas
ORIG_ST_W, ORIG_ST_H = 0.08985, 0.06153846
UV_SCALE_X = ORIG_REGION_W / CANVAS_W
UV_SCALE_Y = ORIG_REGION_H / CANVAS_H
ST_W, ST_H = ORIG_ST_W * UV_SCALE_X, ORIG_ST_H * UV_SCALE_Y

TABLE_BASE = 239  # (b & 127) + 255 - 16
LEADS = (2, 4, 5, 6, 7, 8, 9, 11, 12, 14, 15)  # skips 3 (large space), 10/13 (newlines)
# skips space and '~'; also '_' (0x5F), which the subtitle word-wrap turns into a space
TRAIL_LO = tuple(b for b in range(0x21, 0x7E) if b != 0x5F)  # 92 values
TRAIL_HI = tuple(b | 0x80 for b in range(0x21, 0x7E))  # 93 values
GLYPHS_PER_PAGE = len(TRAIL_LO) + len(TRAIL_HI)


def lead_bytes():
    return list(LEADS)


def trail_bytes():
    return list(TRAIL_LO + TRAIL_HI)


def capacity():
    return len(LEADS) * GLYPHS_PER_PAGE


def code_for_index(i):
    """i-th glyph of the repertoire -> (lead, trail)."""
    if not 0 <= i < capacity():
        raise ValueError(f"glyph index {i} out of range 0..{capacity() - 1}")
    page, j = divmod(i, GLYPHS_PER_PAGE)
    return LEADS[page], trail_bytes()[j]


def table_index(lead, trail):
    return TABLE_BASE + 128 * (lead - 1) + (trail & 0x7F)


def table_length():
    return TABLE_BASE + 128 * max(LEADS)


def entries_needed(n_glyphs):
    return len({table_index(*code_for_index(i)) for i in range(n_glyphs)})


def free_cells():
    """Cells outside the upscaled original region, row-major."""
    cells = []
    for row in range(CANVAS_H // CELL_H):
        for col in range(CANVAS_W // CELL_W):
            if col * CELL_W < ORIG_REGION_W and row * CELL_H < ORIG_REGION_H:
                continue
            cells.append((col, row))
    return cells


def cell_uv(col, row):
    return (col * CELL_W + INSET_X) / CANVAS_W, (row * CELL_H + INSET_Y) / CANVAS_H


def scale_orig_uv(u, v):
    return u * UV_SCALE_X, v * UV_SCALE_Y


def assign(n_glyphs):
    """Assign codes and table cells for n glyphs.

    Returns (codes, entry_cells): codes[i] = (lead, trail); entry_cells maps a
    table index to its (col, row) cell, shared by the lo and hi textures.
    """
    codes = [code_for_index(i) for i in range(n_glyphs)]
    cells = iter(free_cells())
    entry_cells = {}
    for lead, trail in codes:
        idx = table_index(lead, trail)
        if idx not in entry_cells:
            entry_cells[idx] = next(cells)
    return codes, entry_cells
