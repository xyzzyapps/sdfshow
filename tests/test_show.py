"""show.md: cells, arrangement validation and materials."""

from __future__ import annotations

import pytest

from sdfshow.show import Show, cell, parse

BASE = """\
bpm: 120
bars: 4
fps: 30
size: 640x360

## Fields

| field |
|-------|
| core  |
| ring  |

## Sections

| bars | core | ring |
|------|------|------|
{rows}
"""


def _write(tmp_path, rows: str) -> Show:
    """Write a show.md with the given Sections rows and parse it."""
    path = tmp_path / "show.md"
    path.write_text(BASE.replace("{rows}", rows), encoding="utf-8")
    return parse("test", path)


def test_cells():
    """Every operator form parses, and blanks are absent cells."""
    assert cell("u").op == "u"
    assert cell("u0.35").k == 0.35
    assert cell("s0.1").op == "s"
    assert cell("i").op == "i"
    assert cell("x").active is False
    assert cell("").active is False


def test_bad_cell_raises():
    """A cell that is not an operator fails loudly."""
    with pytest.raises(SystemExit):
        cell("union-ish")


def test_sections_cover_the_show(tmp_path):
    """A contiguous arrangement ending at `bars` parses."""
    show = _write(tmp_path, "| 0-2  | u | x |\n| 2-4 | u | u0.3 |")
    assert show.clock.frames == 240
    assert len(show.sections) == 2
    assert show.sections[1].cells["ring"].k == 0.3


def test_section_gap_raises(tmp_path):
    """A hole in the arrangement fails loudly."""
    with pytest.raises(SystemExit, match="does not follow"):
        _write(tmp_path, "| 0-2 | u | x |\n| 3-4 | u | x |")


def test_section_must_end_at_bars(tmp_path):
    """Leaving bars unexplained fails loudly."""
    with pytest.raises(SystemExit, match="sections end at bar"):
        _write(tmp_path, "| 0-2 | u | x |")


def test_first_active_cell_must_be_union(tmp_path):
    """A section cannot start by subtracting from nothing."""
    with pytest.raises(SystemExit, match="first active field"):
        _write(tmp_path, "| 0-4 | s | u |")


def test_materials(tmp_path):
    """A material row sets the field colour, pattern and scale."""
    text = BASE.replace("{rows}", "| 0-4 | u | u |") + (
        "\n## Materials\n\n"
        "| field | color | pattern | scale |\n"
        "|---|---|---|---|\n"
        "| core | 1\\|0.5\\|0 | checker | 2.5 |\n"
    )
    path = tmp_path / "show.md"
    path.write_text(text, encoding="utf-8")
    show = parse("test", path)
    material = show.materials["core"]
    assert material.color == (1.0, 0.5, 0.0)
    assert material.pattern == "checker"
    assert material.scale == 2.5


def test_effects_keep_table_order_and_params(tmp_path):
    """Effects run in first-appearance order; rows merge into one parameter set."""
    text = BASE.replace("{rows}", "| 0-4 | u | u |") + (
        "\n## Effects\n\n| effect | key | value |\n|---|---|---|\n"
        "| bloom | strength | 0.7 |\n"
        "| chroma | amount | 0.02 |\n"
        "| bloom | radius | 3 |\n"
    )
    path = tmp_path / "show.md"
    path.write_text(text, encoding="utf-8")
    show = parse("test", path)
    assert show.effects == ["bloom", "chroma"]
    assert show.effect_params["bloom"] == {"strength": "0.7", "radius": "3"}


def test_unknown_effect_raises(tmp_path):
    """A typo in the effect chain fails by name."""
    text = BASE.replace("{rows}", "| 0-4 | u | u |") + (
        "\n## Effects\n\n| effect | key | value |\n|---|---|---|\n"
        "| blooom | strength | 1 |\n"
    )
    path = tmp_path / "show.md"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(SystemExit, match="unknown effect 'blooom'"):
        parse("test", path)


def test_fold_defaults_and_validation(tmp_path):
    """fold is none by default and rejects unknown modes."""
    text = BASE.replace("{rows}", "| 0-4 | u | u |") + (
        "\n## Stage\n\n| key | value |\n|---|---|\n| fold | kaleido |\n"
        "| fold_count | 8 |\n"
    )
    path = tmp_path / "show.md"
    path.write_text(text, encoding="utf-8")
    show = parse("test", path)
    assert show.stage_value("fold") == "kaleido"
    assert show.stage_value("fold_count") == "8"

    bad = text.replace("kaleido", "spiral")
    path.write_text(bad, encoding="utf-8")
    with pytest.raises(SystemExit, match="fold"):
        parse("test", path)


def test_bad_material_pattern_raises(tmp_path):
    """An unknown surface pattern fails loudly."""
    text = BASE.replace("{rows}", "| 0-4 | u | u |") + (
        "\n## Materials\n\n| field | color | pattern |\n|---|---|---|\n"
        "| core | 0.5\\|0.5\\|0.5 | tartan |\n"
    )
    path = tmp_path / "show.md"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(SystemExit, match="unknown material pattern"):
        parse("test", path)
