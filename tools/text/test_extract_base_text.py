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
