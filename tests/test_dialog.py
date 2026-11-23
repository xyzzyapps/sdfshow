"""Dialogue voice cells: a flite voice, optionally with a pitch factor."""

from __future__ import annotations

import pytest

from sdfshow.dialog import _voice_spec


def test_plain_voice_has_no_shift():
    assert _voice_spec("slt") == ("slt", 1.0)


def test_pitch_suffix_is_parsed():
    assert _voice_spec("slt*0.92") == ("slt", 0.92)
    assert _voice_spec(" slt * 1.05 ") == ("slt", 1.05)


def test_non_numeric_pitch_fails():
    with pytest.raises(SystemExit, match="not a number"):
        _voice_spec("slt*low")


def test_pitch_out_of_range_fails():
    with pytest.raises(SystemExit, match=r"between 0\.5 and 2\.0"):
        _voice_spec("slt*3")


def test_empty_voice_fails():
    with pytest.raises(SystemExit, match="voice is empty"):
        _voice_spec("*1.1")
