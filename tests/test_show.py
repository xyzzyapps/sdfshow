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
    assert cell("u0.35").k == "0.35"
    assert cell("s0.1").op == "s"
    assert cell("i").op == "i"
    assert cell("m0.5").k == "0.5"
    assert cell("mw").k == "w"
    assert cell("x").active is False
    assert cell("").active is False


def test_bad_cell_raises():
    """A cell that is not an operator fails loudly."""
    with pytest.raises(SystemExit):
        cell("union-ish")
    with pytest.raises(SystemExit):
        cell("q0.4")


def test_morph_cell_generates_a_mix(tmp_path):
    """An `m` cell blends one field into the accumulator, driven by a track."""
    text = BASE.replace("{rows}", "| 0-4 | u | mw |")
    path = tmp_path / "show.md"
    path.write_text(text, encoding="utf-8")
    show = parse("test", path)
    assert show.sections[0].cells["ring"].op == "m"

    from sdfshow.fields import load
    from sdfshow.glsl import assemble

    fields_md = tmp_path / "fields.md"
    fields_md.write_text(
        "## Fields\n\n| name | template | parameters |\n|---|---|---|\n"
        "| core | sphere.glsl | radius=1, cx=0, cy=0, cz=0 |\n"
        "| ring | sphere.glsl | radius=1.4, cx=0, cy=0, cz=0 |\n"
        "\n## Tracks\n\n| name | kind | values |\n|---|---|---|\n"
        "| w | keys | 0:0\\|2:1 |\n",
        encoding="utf-8",
    )
    shader = assemble(show, load(fields_md, show.clock))
    assert "d = mix(d, field_ring(p, t, 0.0), clamp(track_w(t), 0.0, 1.0));" in shader


def test_morph_cannot_start_a_section(tmp_path):
    """A morph needs something to blend from."""
    with pytest.raises(SystemExit, match="first active field"):
        _write(tmp_path, "| 0-4 | m0.5 | u |")


def test_tracks_may_live_in_show_md(tmp_path):
    """A show.md Tracks table is merged with fields.md's."""
    from sdfshow.fields import load

    show_md = tmp_path / "show.md"
    show_md.write_text(
        BASE.replace("{rows}", "| 0-4 | u | u |")
        + "\n## Tracks\n\n| name | kind | values |\n|---|---|---|\n"
        "| cam | keys | 0:1\\|2:3 |\n",
        encoding="utf-8",
    )
    fields_md = tmp_path / "fields.md"
    fields_md.write_text(
        "## Fields\n\n| name | template | parameters |\n|---|---|---|\n"
        "| core | sphere.glsl | radius=1, cx=0, cy=0, cz=0 |\n"
        "| ring | sphere.glsl | radius=2, cx=0, cy=0, cz=0 |\n",
        encoding="utf-8",
    )
    show = parse("test", show_md)
    fields = load(fields_md, show.clock, show_md.read_text(encoding="utf-8"))
    assert "cam" in fields.tracks


def test_duplicate_track_across_files_raises(tmp_path):
    """The same track name in both files is an error, not a silent override."""
    from sdfshow.fields import load

    show_md = tmp_path / "show.md"
    show_md.write_text(
        BASE.replace("{rows}", "| 0-4 | u | u |")
        + "\n## Tracks\n\n| name | kind | values |\n|---|---|---|\n"
        "| cam | keys | 0:1\\|2:3 |\n",
        encoding="utf-8",
    )
    fields_md = tmp_path / "fields.md"
    fields_md.write_text(
        "## Fields\n\n| name | template | parameters |\n|---|---|---|\n"
        "| core | sphere.glsl | radius=1, cx=0, cy=0, cz=0 |\n"
        "| ring | sphere.glsl | radius=2, cx=0, cy=0, cz=0 |\n"
        "\n## Tracks\n\n| name | kind | values |\n|---|---|---|\n"
        "| cam | keys | 0:9\\|2:9 |\n",
        encoding="utf-8",
    )
    show = parse("test", show_md)
    with pytest.raises(SystemExit, match="defined in both"):
        load(fields_md, show.clock, show_md.read_text(encoding="utf-8"))


def test_sections_cover_the_show(tmp_path):
    """A contiguous arrangement ending at `bars` parses."""
    show = _write(tmp_path, "| 0-2  | u | x |\n| 2-4 | u | u0.3 |")
    assert show.clock.frames == 240
    assert len(show.sections) == 2
    assert show.sections[1].cells["ring"].k == "0.3"


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


SPRITE_SHOW = """\
bpm: 120
bars: 4
fps: 30
size: 640x360

## Fields

| field |
|-------|
| core |

## Sections

| bars | core |
|------|------|
| 0-4 | u |

## Sprites

| id | sheet | cell | bars | frame | x | y | height |
|----|-------|------|------|-------|-----|-----|--------|
| girl | sheet.png | 16x16 | 0-2 | 0 | 0.2 | -0.2 | 0.3 |
| girl | sheet.png | 16x16 | 2-4 | 1 | 0.2 | -0.2 | 0.3 |
"""


def test_sprites_parse(tmp_path):
    """A Sprites row becomes a placement with a sheet, a cell and a bar window."""
    (tmp_path / "sheet.png").write_bytes(b"not really a png")
    path = tmp_path / "show.md"
    path.write_text(SPRITE_SHOW, encoding="utf-8")
    show = parse("test", path)
    assert len(show.sprites) == 2
    sprite = show.sprites[0]
    assert sprite.id == "girl"
    assert sprite.cell == (16, 16)
    assert (sprite.lo, sprite.hi) == (0.0, 2.0)
    assert sprite.frame == 0
    assert sprite.height == 0.3


def test_sprite_sheet_must_exist(tmp_path):
    """A missing sheet fails by name."""
    path = tmp_path / "show.md"
    path.write_text(SPRITE_SHOW, encoding="utf-8")
    with pytest.raises(SystemExit, match="sheet not found"):
        parse("test", path)
