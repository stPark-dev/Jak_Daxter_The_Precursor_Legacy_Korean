"""Play a Jak 1 cutscene or hint in a running game and capture its subtitles.

Generates the same GOAL forms as OpenGOAL's Subtitle Editor
(game/tools/subtitle_editor/subtitle_editor_repl_client.cpp) from
game/assets/jak1/subtitle-editor-db.json, and sends them through tools/qa/runtime.sh.

  tools/qa/runtime.sh start               # game window (960x540) + persistent REPL
  python3 tools/qa/play.py <scene|hint[@continue]> [...]   # play, capture -> .qa/sheets/<name>.png
  tools/qa/runtime.sh stop
"""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JAK = ROOT / "jak-project"
QA = ROOT / ".qa"
FPS = 30  # working hypothesis, see tools/translation/timing.py


def _proc(entry):
    return f"(the-as {entry['entity_type']} (process-by-name \"{entry['process_name']}\" *active-pool*))"


def _reset():
    return ["(set! (-> *game-info* mode) 'debug)",
            "(initialize! *game-info* 'game (the-as game-save #f) (the-as string #f))"]


def _position(entry):
    forms = []
    if entry.get("continue_name"):
        forms.append(f"(start 'play (get-continue-by-name *game-info* \"{entry['continue_name']}\"))")
    if entry.get("move_to"):
        x, y, z = entry["move_to"]
        forms.append("(move-to-point! (-> *target* control) (new 'static 'vector "
                     f":x (meters {x:.3f}) :y (meters {y:.3f}) :z (meters {z:.3f})))")
        forms.append("(send-event *camera* 'teleport)")
    return forms


def cutscene_forms(entry):
    forms = _reset()
    reqs = [r.replace("__GET-PROCESS__", _proc(entry)) for r in entry.get("requirements", [])]
    if entry.get("move_first"):
        forms += _position(entry) + reqs
    else:
        forms += reqs + _position(entry)
    if entry.get("execute_code"):
        code = entry["execute_code"].replace("__GET-PROCESS__", _proc(entry))
        forms.append("(send-event *camera* 'teleport)")
        delay = entry.get("delay_frames", 0)
        if delay:
            code = f"(process-spawn-function process (lambda () (dotimes (i {delay}) (suspend)) {code}))"
        forms.append(code)
    return forms


def hint_forms(name, continue_name=None):
    """Hints need their level loaded (voice + subtitles); go to `continue_name` first."""
    forms = _reset() + _position({"continue_name": continue_name})
    return forms + [f"(level-hint-spawn (text-id zero) \"{name}\" (the-as entity #f) "
                    "*entity-pool* (game-task none))"]


def parse_target(arg):
    """'NAME@continue-point' -> (NAME, continue-point); plain 'NAME' -> (NAME, None)."""
    name, _, cont = arg.partition("@")
    return name, (cont or None)


def duration_seconds(meta_lines):
    return max(m["frame_start"] for m in meta_lines) / FPS


def forms_for(name, db, hints, continue_name=None):
    if name in db:
        return cutscene_forms(db[name])
    if name in hints:
        return hint_forms(name, continue_name)
    raise KeyError(f"{name}: not in subtitle-editor-db.json and not a hint")


def _send(form, wait=1.0):
    subprocess.run([str(ROOT / "tools/qa/runtime.sh"), "send", form, str(wait)], check=True,
                   stdout=subprocess.DEVNULL)


def _capture(win, out_dir, seconds, every=1.0):
    out_dir.mkdir(parents=True, exist_ok=True)
    frames, t0 = [], time.time()
    while time.time() - t0 < seconds:
        f = out_dir / f"f{len(frames):04d}.png"
        subprocess.run(["import", "-window", win, str(f)], check=False, stderr=subprocess.DEVNULL)
        frames.append(f)
        time.sleep(every)
    return frames


def _sheet(frames, out, band=(385, 480)):
    from PIL import Image, ImageChops
    kept, prev = [], None
    for f in frames:
        if not f.exists():
            continue
        b = Image.open(f).convert("RGB").crop((0, band[0], 960, band[1]))
        if prev is None or ImageChops.difference(b.convert("L"), prev.convert("L")).point(
                lambda v: 255 if v > 60 else 0).getbbox():
            kept.append(b)
            prev = b
    h = band[1] - band[0]
    sheet = Image.new("RGB", (960, max(1, h * len(kept))))
    for i, b in enumerate(kept):
        sheet.paste(b, (0, h * i))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return len(kept)


def main():
    db = json.loads((JAK / "game/assets/jak1/subtitle-editor-db.json").read_text(encoding="utf-8"))
    meta = json.loads((JAK / "game/assets/jak1/subtitle/subtitle_meta_en-US.json").read_text(encoding="utf-8"))
    win = (QA / "win.id").read_text().strip()
    for target in sys.argv[1:]:
        name, cont = parse_target(target)
        for form in forms_for(name, db, meta["hints"], cont):
            # after moving to another level, wait out loading and the level-name card
            _send(form, wait=(12.0 if cont else 3.0) if form.startswith("(start ") else 1.0)
        lines = meta["cutscenes"][name] if name in meta["cutscenes"] else meta["hints"][name]["lines"]
        secs = duration_seconds(lines) + 6
        frames = _capture(win, QA / "frames" / name, secs)
        n = _sheet(frames, QA / "sheets" / f"{name}.png")
        ws = ROOT / "translation" / ("cutscenes/" + name + ".json" if name in meta["cutscenes"] else "hints.json")
        entries = [e for e in json.loads(ws.read_text(encoding="utf-8"))
                   if e["id"].split(":")[1] == name]
        (QA / "sheets" / f"{name}.txt").write_text(
            "\n".join(f"{e['id']}\t{e.get('speaker', '')}\t{e['src']}\t{e['ko']}" for e in entries) + "\n",
            encoding="utf-8")
        print(f"{name}: {secs:.0f}s captured, {n} distinct subtitle bands -> .qa/sheets/{name}.png")


if __name__ == "__main__":
    main()
