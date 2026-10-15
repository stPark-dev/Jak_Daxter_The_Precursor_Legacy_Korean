"""Apply a drafted batch: {scene: [[ko, [hold ids...]], ...]} -> translation/cutscenes/<scene>.json.
Refuses when line counts differ (protects source structure)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def apply(batch, base_note):
    for scene, lines in batch.items():
        p = ROOT / "translation" / "cutscenes" / f"{scene}.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        if len(d) != len(lines):
            raise SystemExit(f"{scene}: {len(d)} source lines but {len(lines)} drafts")
        for e, (ko, holds) in zip(d, lines):
            note = base_note + (f"; hold: {', '.join(holds)}" if holds else "")
            e.update(ko=ko, state="needs_human_review" if holds else "needs_review", note=note)
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"applied {sum(len(v) for v in batch.values())} lines in {len(batch)} scenes")


if __name__ == "__main__":
    apply(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")), sys.argv[2])
