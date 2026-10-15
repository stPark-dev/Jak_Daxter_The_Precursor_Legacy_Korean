"""Translation workspace for the Jak 1 Korean patch.

Units (logical translation batches) are built from the OpenGOAL English sources:
  text/base, text/custom, speakers, cutscene/<scene>, hint/<name>
Each entry: {"id", "src", "speaker"?, "ko", "state", "note"}.
"src" and "id" are protected (owned by the extraction baseline); translators edit
"ko", "state" and "note" only.
"""
import re

STATES = ("untranslated", "in_progress", "needs_review", "needs_human_review",
          "distribution_eligible")
TRANSLATED_STATES = STATES[1:]

FORMAT_TOKEN = re.compile(r"~[0-9+\-]*[A-Za-z]")
PAD_TOKEN = re.compile(r"<[A-Z_]+>")
_PAIR = re.compile(r'\{"((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\}')


class NotEligible(Exception):
    pass


def _entry(id_, src, speaker=None):
    e = {"id": id_, "src": src}
    if speaker is not None:
        e["speaker"] = speaker
    return e


def build_baseline(lines, meta, base_text, custom_text):
    units = {
        "text/base": [_entry(f"base:{k}", v) for k, v in base_text.items()],
        "text/custom": [_entry(f"custom:{k}", v) for k, v in custom_text.items()],
        "speakers": [_entry(f"speaker:{k}", v) for k, v in lines["speakers"].items()],
    }
    for scene, texts in lines["cutscenes"].items():
        speakers = [m["speaker"] for m in meta["cutscenes"][scene] if not m["clear"]]
        units[f"cutscene/{scene}"] = [
            _entry(f"cut:{scene}:{i}", t, speakers[i]) for i, t in enumerate(texts)]
    for name, texts in lines["hints"].items():
        speakers = [m["speaker"] for m in meta["hints"][name]["lines"] if not m["clear"]]
        units[f"hint/{name}"] = [
            _entry(f"hint:{name}:{i}", t, speakers[i]) for i, t in enumerate(texts)]
    return units


def sync(base_unit, work):
    """Merge authored work (by id) into the baseline unit. A changed source invalidates."""
    out = []
    for b in base_unit:
        e = dict(b, ko="", state="untranslated", note="")
        w = work.get(b["id"])
        if w:
            if w.get("src", b["src"]) == b["src"]:
                e.update(ko=w.get("ko", ""), state=w.get("state", "untranslated"),
                         note=w.get("note", ""))
            else:
                e["stale_ko"] = w.get("ko", "")
                e["note"] = w.get("note", "")
        out.append(e)
    return out


def allowed_chars(font_db_path, source_texts=()):
    """Characters the Jak 1 (v2) font can draw, besides Hangul syllables.

    Besides the font DB tables, any character the English source already uses is
    allowed: it passes through the encoder unchanged and is drawn from the original sheet.
    """
    src = open(font_db_path, encoding="utf-8").read()
    chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 \n")
    for t in source_texts:
        chars |= set(PAD_TOKEN.sub("", FORMAT_TOKEN.sub("", t)))
    passthru = src[src.index("passthrus_jak1"):src.index("std::vector<EncodeInfo> encode_info_jak1 ")]
    chars |= set(re.findall(r"'(.)'", passthru))
    encode_v2 = src[src.index("std::vector<EncodeInfo> encode_info_jak1_v2"):]
    for utf8, _ in _PAIR.findall(encode_v2):
        if len(utf8) == 1:
            chars.add(utf8)
    return chars


def is_hangul(ch):
    return 0xAC00 <= ord(ch) <= 0xD7A3


def check_entry(e, allowed):
    """Mechanical checks only (never judges wording)."""
    ko = e.get("ko", "")
    problems = []
    if FORMAT_TOKEN.findall(e["src"]) != FORMAT_TOKEN.findall(ko):
        problems.append(f"format tokens differ: {FORMAT_TOKEN.findall(e['src'])} vs {FORMAT_TOKEN.findall(ko)}")
    if sorted(PAD_TOKEN.findall(e["src"])) != sorted(PAD_TOKEN.findall(ko)):
        problems.append("token set differs (<PAD_*>)")
    bare = PAD_TOKEN.sub("", FORMAT_TOKEN.sub("", ko))
    bad = sorted({c for c in bare if not is_hangul(c) and c not in allowed})
    if bad:
        problems.append(f"char not drawable by the Jak 1 font: {bad!r}")
    return problems


def _pick(e, policy):
    if policy == "release":
        if e["state"] != "distribution_eligible":
            raise NotEligible(f"{e['id']} is {e['state']}")
        return e["ko"]
    if e["state"] in TRANSLATED_STATES and e["ko"]:
        return e["ko"]
    return e["src"]


def export(units, lines_template, policy):
    """Build OpenGOAL ko-KR file contents. policy: 'dev' (source fallback) or 'release'."""
    if policy not in ("dev", "release"):
        raise ValueError(policy)
    by_id = {e["id"]: _pick(e, policy) for unit in units.values() for e in unit}
    sub = {
        "cutscenes": {s: [by_id[f"cut:{s}:{i}"] for i in range(len(t))]
                      for s, t in lines_template["cutscenes"].items()},
        "hints": {h: [by_id[f"hint:{h}:{i}"] for i in range(len(t))]
                  for h, t in lines_template["hints"].items()},
        "speakers": {k: by_id[f"speaker:{k}"] for k in lines_template["speakers"]},
    }
    pick = lambda prefix: {i.split(":", 1)[1]: v for i, v in by_id.items() if i.startswith(prefix)}
    return {"subtitle_lines": sub, "base_text": pick("base:"), "custom_text": pick("custom:"),
            "dev_build": policy == "dev"}
