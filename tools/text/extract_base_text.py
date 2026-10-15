"""Extract one language column of the decompiled Jak 1 game_text.txt as base-text JSON.

The output matches OpenGOAL's game/assets/jak1/text/game_base_text_*.json format:
{"<hex id without #x and leading zeros>": "text"}.

Usage: python3 extract_base_text.py <game_text.txt> <column> <out.json>
"""
import json
import re
import sys

ENTRY = re.compile(r"\(#x([0-9a-fA-F]+)\s*((?:\"(?:[^\"\\]|\\.)*\"\s*)+)\)")
STRING = re.compile(r"\"((?:[^\"\\]|\\.)*)\"")


def _unescape(s):
    return re.sub(r"\\(.)", r"\1", s)


def extract(text, column):
    out = {}
    for hex_id, body in ENTRY.findall(text):
        strings = STRING.findall(body)
        if column >= len(strings):
            raise ValueError(f"#x{hex_id} has no column {column}")
        out[format(int(hex_id, 16), "x")] = _unescape(strings[column])
    return out


def main():
    src, column, dst = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    with open(src, encoding="utf-8") as f:
        data = extract(f.read(), column)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"{len(data)} entries -> {dst}")


if __name__ == "__main__":
    main()
