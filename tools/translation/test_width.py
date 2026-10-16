import width

TABLE = {" ": 15.0, "A": 19.0, "B": 18.0, "I": 11.0, "0": 17.0, "_": 15.0}


def test_hangul_uses_fixed_advance():
    assert width.text_width("가나", TABLE) == 2 * width.HANGUL_ADVANCE


def test_ascii_uses_font_table():
    assert width.text_width("A I", TABLE) == 19.0 + 15.0 + 11.0


def test_pad_token_counts_as_one_icon():
    assert width.text_width("<PAD_X>", TABLE) == width.ICON_ADVANCE


def test_format_token_counts_as_two_digits():
    assert width.text_width("~D", TABLE) == 2 * 17.0


def test_unknown_char_falls_back_to_hangul_advance():
    assert width.text_width("Ç", TABLE) == width.HANGUL_ADVANCE


def test_multiline_uses_widest_line():
    assert width.text_width("AA\nA", TABLE) == 38.0


def test_flag_lists_only_translations_wider_than_source():
    entries = [
        {"id": "a", "src": "AB", "ko": "가"},       # 24 <= 37
        {"id": "b", "src": "I", "ko": "가나"},      # 48 > 11
        {"id": "c", "src": "I", "ko": ""},          # untranslated: skipped
    ]
    flagged = width.flag(entries, TABLE)
    assert [f["id"] for f in flagged] == ["b"]
    assert flagged[0]["ratio"] > 1.0


def test_load_table_reads_font24_widths(tmp_path):
    rows = "\n".join(f"(new 'static 'vector :x 0.0 :y 0.0 :z 1.0 :w {float(i)})" for i in range(289))
    p = tmp_path / "font.gc"
    p.write_text("(define *font24-table*\n (new 'static 'inline-array vector 289\n" + rows + "))\n")
    t = width.load_table(p)
    assert t[" "] == 16.0  # char 32 -> index 16
    assert t["A"] == 49.0
