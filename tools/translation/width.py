"""Screen-text width heuristic. Flags candidates for in-game review; never edits text.

Width is estimated in font24 advance units: ASCII from *font24-table* (font.gc),
Hangul at the fixed advance kr-font.gc gives every Korean glyph. A translation wider
than its English source may wrap or overflow where the source fit.

  python3 width.py <jak-project> <workspace> [ratio]
"""
import json
import re
import sys
from pathlib import Path

from ws import FORMAT_TOKEN, PAD_TOKEN

HANGUL_ADVANCE = 24.0  # kr-font-extend-table: (set-vector! ... 1.0 24.0)
ICON_ADVANCE = 24.0
_ROW = re.compile(r":w ([\d.]+)\)")


def load_table(font_gc):
    lines = Path(font_gc).read_text(encoding="utf-8").split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("(define *font24-table*"))
    widths = []
    for l in lines[start:]:
        widths += [float(w) for w in _ROW.findall(l)]
        if len(widths) >= 289:
            break
    return {chr(i + 16): w for i, w in enumerate(widths[:289]) if 32 <= i + 16 < 127}


def _line_width(line, table):
    w = ICON_ADVANCE * len(PAD_TOKEN.findall(line))
    line = PAD_TOKEN.sub("", line)
    w += 2 * table.get("0", HANGUL_ADVANCE) * len(FORMAT_TOKEN.findall(line))
    for ch in FORMAT_TOKEN.sub("", line):
        w += table.get(ch, HANGUL_ADVANCE)
    return w


def text_width(text, table):
    return max(_line_width(l, table) for l in text.split("\n"))


def flag(entries, table, ratio=1.0):
    out = []
    for e in entries:
        if not e.get("ko"):
            continue
        src, ko = text_width(e["src"], table), text_width(e["ko"], table)
        if src and ko > src * ratio:
            out.append({"id": e["id"], "src": e["src"], "ko": e["ko"], "ratio": round(ko / src, 2)})
    return out


def main():
    jak, ws_dir = sys.argv[1:3]
    ratio = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    table = load_table(Path(jak) / "goal_src/jak1/engine/gfx/font.gc")
    for unit in ("text_base", "text_custom"):
        entries = json.loads((Path(ws_dir) / f"{unit}.json").read_text(encoding="utf-8"))
        for f in flag(entries, table, ratio):
            print(f"{f['ratio']:.2f}\t{f['id']}\t{f['src']}\t{f['ko']}")


if __name__ == "__main__":
    main()
