"""fields.md: parameter resolution, templates and loud failures."""

from __future__ import annotations

import pytest

from sdfshow.clock import Clock
from sdfshow.fields import load, render_functions, split_params

CLOCK = Clock(bpm=120.0, bars=8, fps=30, width=960, height=540)

TEMPLATE = """\
# fields

bpm_mult: 2

## Fields

| name | template  | parameters |
|------|-----------|------------|
| core | sphere.glsl | radius=0.62*pulse, cx=0, cy=0, cz=0 |

## Tracks

| name  | kind  | values |
|-------|-------|--------|
| pulse | steps | 1\\|0.5 |
"""


def _load(tmp_path, text: str = TEMPLATE):
    """Write fields.md and load it against the fixture clock."""
    path = tmp_path / "fields.md"
    path.write_text(text, encoding="utf-8")
    return load(path, CLOCK)


def test_params_are_resolved_and_substituted(tmp_path):
    """Track names become calls; numbers stay literals."""
    fields = _load(tmp_path)
    body = fields.fields[0].body
    assert "0.62*track_pulse(t)" in body
    assert "track_pulse(t)" in body
    assert "{{" not in body


def test_render_functions_emit_one_per_field(tmp_path):
    """Each field becomes a named GLSL function."""
    text = render_functions(_load(tmp_path))
    assert "float field_core(vec3 p, float t)" in text
    assert "float track_pulse(float t)" in text


def test_missing_placeholder_fails_by_name(tmp_path):
    """A template hole with no value fails with the field and the key."""
    text = TEMPLATE.replace("radius=0.62*pulse, cx=0, cy=0, cz=0", "cx=0, cy=0, cz=0")
    with pytest.raises(SystemExit, match="field 'core' needs value 'radius'"):
        _load(tmp_path, text)


def test_clock_keys_are_rejected_in_fields_md(tmp_path):
    """`bar` comes from show.md; redefining it would drift."""
    text = TEMPLATE.replace("bpm_mult: 2", "bar: 2")
    with pytest.raises(SystemExit, match=r"come from show\.md"):
        _load(tmp_path, text)


def test_split_params_respects_parentheses():
    """A GLSL call inside a parameter does not split at its comma."""
    assert split_params("a=1, b=min(1, 2), c=3") == {
        "a": "1",
        "b": "min(1, 2)",
        "c": "3",
    }
