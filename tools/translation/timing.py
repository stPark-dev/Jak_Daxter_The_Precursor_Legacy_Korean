"""Subtitle reading-speed heuristic. Flags candidates for human review; never edits text.

Each subtitle line is shown from its frame_start until the next meta event (a new line
or a clear). FPS = 30 is a working hypothesis (English source median ~13.6 chars/s).

  python3 timing.py <jak-project> <workspace> [max_cps]
"""
import json
import sys
from pathlib import Path

FPS = 30
MAX_CPS = 12  # Netflix Korean adult guideline, characters incl. spaces per second


def durations(meta, fps=FPS):
    """Seconds each non-clear line stays up (None for the last line: open-ended)."""
    out = []
    for i, m in enumerate(meta):
        if m["clear"]:
            continue
        nxt = meta[i + 1]["frame_start"] if i + 1 < len(meta) else None
        out.append(None if nxt is None else (nxt - m["frame_start"]) / fps)
    return out


def flag(entries, secs, max_cps=MAX_CPS):
    flagged = []
    for e, s in zip(entries, secs):
        if not e.get("ko") or not s:
            continue
        cps = round(len(e["ko"]) / s, 1)
        if cps > max_cps:
            flagged.append({"id": e["id"], "cps": cps, "secs": round(s, 2), "ko": e["ko"]})
    return flagged


def main():
    jak, ws_dir = Path(sys.argv[1]), Path(sys.argv[2])
    max_cps = float(sys.argv[3]) if len(sys.argv) > 3 else MAX_CPS
    meta = json.loads((jak / "game/assets/jak1/subtitle/subtitle_meta_en-US.json").read_text(encoding="utf-8"))
    for p in sorted((ws_dir / "cutscenes").glob("*.json")):
        entries = json.loads(p.read_text(encoding="utf-8"))
        for f in flag(entries, durations(meta["cutscenes"][p.stem]), max_cps):
            print(f"{f['id']}\t{f['cps']} cps\t{f['secs']}s\t{f['ko']}")


if __name__ == "__main__":
    main()
