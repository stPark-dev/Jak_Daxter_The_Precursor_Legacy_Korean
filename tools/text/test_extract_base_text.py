"""Tests for extracting one language column of the decompiled game_text.txt."""
import pytest

import extract_base_text as X

SAMPLE = '''(group-name "common")
(language-id 0 1 2 3 4 5 6)
(text-version jak1-v2)

(#x0103
  "<PAD_X> = YES, <PAD_TRIANGLE> = NO"
  "<PAD_X> = OUI, <PAD_TRIANGLE> = NON"
  "x" "x" "x" "x" "x"
  )

(#x016e
  "PRESS START"
  "APPUIE SUR START"
  "x" "x" "x" "x" "x"
  )

(#x0200
  "SAY \\"HI\\" \\\\ BYE"
  "x" "x" "x" "x" "x" "x"
  )
'''


def test_extracts_english_column_keyed_like_custom_text():
    out = X.extract(SAMPLE, column=0)
    assert out["103"] == "<PAD_X> = YES, <PAD_TRIANGLE> = NO"
    assert out["16e"] == "PRESS START"


def test_other_column():
    assert X.extract(SAMPLE, column=1)["16e"] == "APPUIE SUR START"


def test_unescapes_quotes_and_backslashes():
    assert X.extract(SAMPLE, column=0)["200"] == 'SAY "HI" \\ BYE'


def test_counts_every_entry():
    assert len(X.extract(SAMPLE, column=0)) == 3


def test_missing_column_fails():
    with pytest.raises(ValueError):
        X.extract(SAMPLE, column=9)


CREDITS = SAMPLE + '''
(credits :begin #x0b00
  ("~33LCREATED AND DEVELOPED BY"
   "~33LCREE PAR" "x" "x" "x" "x" "x"
   )
  "NAUGHTY DOG, INC."
  ""
  ("~34LVOICE ACTORS" "y" "y" "y" "y" "y" "y")
  "~34LDAXTER"
  )
'''


def test_credits_lists_are_extracted_with_running_ids():
    # og:kr per-language credit headings; ids count every line, names and blanks included
    d = X.extract(CREDITS, 0)
    assert d["b00"] == "~33LCREATED AND DEVELOPED BY"
    assert d["b03"] == "~34LVOICE ACTORS"
    assert X.extract(CREDITS, 1)["b00"] == "~33LCREE PAR"


def test_credits_single_strings_are_not_translatable():
    # names are the same in every language: left to the original text
    d = X.extract(CREDITS, 0)
    assert "b01" not in d and "b02" not in d


def test_credits_single_headings_are_translatable():
    # a heading (starts with a ~3nL size token) shared by all languages, e.g. ~34LDAXTER
    assert X.extract(CREDITS, 0)["b04"] == "~34LDAXTER"
    assert X.extract(CREDITS, 3)["b04"] == "~34LDAXTER"
