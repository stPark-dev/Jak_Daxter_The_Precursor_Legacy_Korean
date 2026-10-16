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


CREDITS = re.compile(r"\(credits :begin #x([0-9a-fA-F]+)")
HEADING = re.compile(r"~3\d+L")
CREDIT_ITEM = re.compile(r"\(((?:\s*\"(?:[^\"\\]|\\.)*\")+)\s*\)|\"((?:[^\"\\]|\\.)*)\"|(\))")


def _credits(text, column):
    """og:kr per-language lines of a (credits :begin #x...) block. Ids advance on every line;
    single strings are the same in every language: names and blanks are left out, headings
    (starting with a ~3nL size token, e.g. ~34LDAXTER) are kept so they can be translated."""
    out = {}
    for m in CREDITS.finditer(text):
        cur = int(m.group(1), 16)
        for item in CREDIT_ITEM.finditer(text, m.end()):
            if item.group(3):  # end of the credits block
                break
            if item.group(1) is not None:
                strings = STRING.findall(item.group(1))
                if column >= len(strings):
                    raise ValueError(f"#x{cur:x} has no column {column}")
                out[format(cur, "x")] = _unescape(strings[column])
            elif HEADING.match(item.group(2)):
                out[format(cur, "x")] = _unescape(item.group(2))
            cur += 1
    return out


def extract(text, column):
    out = {}
    for hex_id, body in ENTRY.findall(text):
        strings = STRING.findall(body)
        if column >= len(strings):
            raise ValueError(f"#x{hex_id} has no column {column}")
        out[format(int(hex_id, 16), "x")] = _unescape(strings[column])
    out.update(_credits(text, column))
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
