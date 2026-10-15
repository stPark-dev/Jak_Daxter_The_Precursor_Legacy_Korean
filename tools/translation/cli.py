"""Translation workspace CLI.

  python3 cli.py init   <jak-project> <workspace>   # create/sync work files from English sources
  python3 cli.py check  <jak-project> <workspace>   # mechanical checks + state counts
  python3 cli.py export <jak-project> <workspace> [dev|release]  # write OpenGOAL ko-KR files
"""
import json
import sys
from collections import Counter
from pathlib import Path

import ws

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "text"))
import extract_base_text  # noqa: E402

SUB = "game/assets/jak1/subtitle"
TXT = "game/assets/jak1/text"
FONT_DB = "common/util/font/dbs/font_db_jak1.cpp"


def _read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _write(p, data):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def _sources(jak):
    jak = Path(jak)
    lines = _read(jak / SUB / "subtitle_lines_en-US.json")
    meta = _read(jak / SUB / "subtitle_meta_en-US.json")
    base = extract_base_text.extract(
        (jak / "decompiler_out/jak1/assets/game_text.txt").read_text(encoding="utf-8"), 0)
    custom = _read(jak / TXT / "game_custom_text_en-US.json")
    return lines, meta, base, custom


def unit_path(ws_dir, unit):
    ws_dir = Path(ws_dir)
    if unit.startswith("cutscene/"):
        return ws_dir / "cutscenes" / (unit.split("/", 1)[1] + ".json")
    if unit.startswith("hint/"):
        return ws_dir / "hints.json"
    return ws_dir / (unit.replace("/", "_") + ".json")


def _load_work(ws_dir):
    work = {}
    for p in Path(ws_dir).rglob("*.json"):
        for e in _read(p):
            work[e["id"]] = e
    return work


def load_units(jak, ws_dir):
    baseline = ws.build_baseline(*_sources(jak))
    work = _load_work(ws_dir)
    return {u: ws.sync(entries, work) for u, entries in baseline.items()}


def init(jak, ws_dir):
    files = {}
    for unit, entries in load_units(jak, ws_dir).items():
        files.setdefault(unit_path(ws_dir, unit), []).extend(entries)
    for path, entries in files.items():
        _write(path, entries)


def counts(ws_dir):
    c = Counter()
    for e in _load_work(ws_dir).values():
        kind = e["id"].split(":", 1)[0]
        c[{"base": "text/base", "custom": "text/custom", "speaker": "speakers"}.get(kind, "subtitles")] += 1
    return c


def check(jak, ws_dir):
    units = load_units(jak, ws_dir)
    english = [e["src"] for unit in units.values() for e in unit if not e["id"].startswith("base:")
               or e["src"].isascii()]
    allowed = ws.allowed_chars(Path(jak) / FONT_DB, english)
    states, problems = Counter(), []
    for unit in units.values():
        for e in unit:
            states[e["state"]] += 1
            if e["state"] != "untranslated":
                problems += [f"{e['id']}: {p}" for p in ws.check_entry(e, allowed)]
    return states, problems


def export(jak, ws_dir, policy):
    jak = Path(jak)
    lines, meta, _, _ = _sources(jak)
    out = ws.export(load_units(jak, ws_dir), lines, policy)
    _write(jak / SUB / "subtitle_lines_ko-KR.json", out["subtitle_lines"])
    _write(jak / SUB / "subtitle_meta_ko-KR.json", meta)
    _write(jak / TXT / "game_base_text_ko-KR.json", out["base_text"])
    _write(jak / TXT / "game_custom_text_ko-KR.json", out["custom_text"])
    return out


def main():
    cmd, jak, ws_dir = sys.argv[1:4]
    if cmd == "init":
        init(jak, ws_dir)
        print(dict(counts(ws_dir)))
    elif cmd == "check":
        states, problems = check(jak, ws_dir)
        print(dict(states))
        print("\n".join(problems) or "no mechanical problems")
        sys.exit(1 if problems else 0)
    elif cmd == "export":
        policy = sys.argv[4] if len(sys.argv) > 4 else "dev"
        states, problems = check(jak, ws_dir)
        if problems:
            sys.exit("refusing to export:\n" + "\n".join(problems))
        export(jak, ws_dir, policy)
        print(f"exported ({policy}) {dict(states)}")


if __name__ == "__main__":
    main()
