"""Tracks: parsing, expression validation and generated GLSL."""

from __future__ import annotations

import pytest

from sdfshow.md import tables
from sdfshow.tracks import expression, glsl, parse_tracks

TEXT = """\
## Tracks

| name  | kind  | values                      | options     |
|-------|-------|-----------------------------|-------------|
| pulse | steps | 1\\|0.5\\|0.2\\|0.5             | ease=smooth |
| rise  | bars  | 0\\|0.5\\|1                   |             |
| dolly | keys  | 0:5.6\\|3:4.4\\|7:4.9         | ease=smooth |
| spin  | expr  | 0.45+0.12*t                 |             |
"""


def _tracks():
    """Parse the fixture tracks."""
    return parse_tracks(TEXT, tables(TEXT))


def test_kinds_parse():
    """All four kinds parse into their value shape."""
    tracks = _tracks()
    assert tracks["pulse"].values == (1.0, 0.5, 0.2, 0.5)
    assert tracks["rise"].values == (0.0, 0.5, 1.0)
    assert tracks["dolly"].keys == ((0.0, 5.6), (3.0, 4.4), (7.0, 4.9))
    assert tracks["spin"].expr == "0.45+0.12*t"
    assert tracks["pulse"].ease == "smooth"


def test_steps_glsl_is_a_looping_array():
    """Steps become a small const array sampled with mix()."""
    text = glsl(_tracks()["pulse"])
    assert "float track_pulse(float t)" in text
    assert "float v[N] = float[N](1.0, 0.5, 0.2, 0.5);" in text
    assert "mod(t, span)" in text
    assert "smoothstep" in text


def test_bars_loop_over_one_bar_each():
    """A bars track spans one bar per value."""
    text = glsl(_tracks()["rise"])
    assert "float span = BAR * 3.0;" in text


def test_keys_are_piecewise():
    """Keys interpolate from the first key and clamp outside."""
    text = glsl(_tracks()["dolly"])
    assert "float x = t / BAR;" in text
    assert text.count("v = mix(v,") == 2


def test_expression_expands_tracks():
    """A parameter expression becomes a GLSL call with the clock argument."""
    tracks = _tracks()
    assert expression("0.62*pulse", tracks) == "0.62*track_pulse(t)"
    assert expression("-0.16", tracks) == "-0.16"


def test_expression_rejects_unknown_identifier():
    """A typo in a parameter fails loudly instead of emitting a broken shader."""
    with pytest.raises(SystemExit, match="unknown identifier 'puls'"):
        expression("0.62*puls", _tracks())


def test_expression_rejects_prose():
    """Free text is not an expression."""
    with pytest.raises(SystemExit):
        expression("fast-ish", _tracks())
