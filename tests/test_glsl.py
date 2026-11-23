"""Shader assembly: the whole scene is one inspectable artifact."""

from __future__ import annotations

import pytest

from sdfshow import config as C
from sdfshow.clock import Clock
from sdfshow.fields import load
from sdfshow.glsl import assemble, assemble_effect
from sdfshow.show import parse


def _scene() -> str:
    """Assemble the worked example's shader."""
    show = parse("first", C.SHOWS / "first" / "show.md")
    fields = load(show.fields_md, show.clock)
    return assemble(show, fields)


def test_shader_is_a_placebo_hook():
    """The output is a libplacebo fragment hook, not a standalone shader."""
    text = _scene()
    assert text.startswith("//!HOOK MAIN")
    assert "//!BIND HOOKED" in text
    assert "vec4 hook()" in text


def test_clock_constants_are_baked():
    """BPM, bars and fps become compile-time defines shared by templates and tracks."""
    text = _scene()
    assert "#define FPS 30.0" in text
    assert "#define BAR 2.0" in text
    assert "#define STEP 0.125" in text
    assert "#define TIME0 0.0" in text


def test_time_comes_from_the_frame_index():
    """The clock is seekable: no wall time, no accumulated state."""
    text = _scene()
    assert "float t = (float(frame) + TIME0) / FPS;" in text


def test_fields_and_tracks_are_named_functions():
    """Every field and track is its own function, in the generated source."""
    text = _scene()
    assert "float field_core(vec3 p, float t)" in text
    assert "float field_ring(vec3 p, float t)" in text
    assert "float track_pulse(float t)" in text
    assert "float track_ring_radius(float t)" in text


def test_sections_select_composition_operators():
    """The arrangement is visible in the scene function."""
    text = _scene()
    assert "smin(d, field_ring(p, t), 0.3)" in text
    assert "t < 4.0" in text and "t < 8.0" in text and "t < 12.0" in text


def test_no_placeholders_survive():
    """A complete shader has no unresolved template holes."""
    assert "{{" not in _scene()


def test_braces_balance():
    """A cheap guard against a codegen branch that forgets a closing brace."""
    text = _scene()
    assert text.count("{") == text.count("}")


def test_demo_assembles_all_scene_templates():
    """The demoscene show compiles every template it uses into one shader."""
    show = parse("demo", C.SHOWS / "demo" / "show.md")
    fields = load(show.fields_md, show.clock)
    text = assemble(show, fields)
    for field in ("tunnel", "menger", "gyroid", "sun", "pillars", "floor"):
        assert f"float field_{field}(vec3 p, float t)" in text
    assert "smin(d, field_pillars(p, t), 0.0)" in text
    assert text.count("{") == text.count("}")


def test_patterns_and_post_pass_are_generated():
    """Material patterns and the CRT pass reach the shader."""
    show = parse("demo", C.SHOWS / "demo" / "show.md")
    fields = load(show.fields_md, show.clock)
    text = assemble(show, fields)
    assert "vec3 apply_pattern(int pat, float scale, vec3 c, vec3 p)" in text
    assert "int ptn[" in text and "float scl[" in text
    assert "vec3 post(vec3 col, vec2 uv, vec2 screen, float t)" in text
    assert "col *= 1.0 - 0.13 * sl;" in text  # scanlines from the demo's stage
    assert "hue_rotate(base," in text


def _folded_scene(tmp_path, stage: str) -> str:
    """Assemble a one-sphere show with a custom Stage table."""
    clock = Clock(bpm=120.0, bars=2, fps=30, width=320, height=180)
    show_md = tmp_path / "show.md"
    fields_md = tmp_path / "fields.md"
    show_md.write_text(
        f"""bpm: 120
bars: 2
fps: 30
size: 320x180

## Stage
| key | value |
|-----|-------|
{stage}

## Fields
| field |
|-------|
| core  |

## Sections
| bars | core |
|------|------|
| 0-2  | u    |
""",
        encoding="utf-8",
    )
    fields_md.write_text(
        "## Fields\n\n| name | template | parameters |\n|---|---|---|\n"
        "| core | sphere.glsl | radius=1, cx=0, cy=0, cz=0 |\n",
        encoding="utf-8",
    )
    show = parse("fold", show_md)
    assert show.clock == clock
    return assemble(show, load(fields_md, show.clock))


def test_kaleido_fold_is_generated(tmp_path):
    """A kaleido fold duplicates space into mirrored sectors."""
    text = _folded_scene(tmp_path, "| fold | kaleido |\n| fold_count | 8 |")
    assert "float sector = TAU / max(8.0, 2.0);" in text
    assert "a = abs(a);" in text
    assert "p = fold_space(p, t);" in text


def test_mirror_fold_is_generated(tmp_path):
    """A mirror fold reflects space across two planes."""
    text = _folded_scene(tmp_path, "| fold | mirror |")
    assert "p.x = abs(p.x);" in text
    assert "p.z = abs(p.z);" in text


def test_effect_passes_are_placebo_hooks():
    """Every effect is a complete pass over the previous one."""
    clock = Clock(bpm=120.0, bars=8, fps=30, width=960, height=540)
    for name in ("bloom", "chroma", "crt", "glitch"):
        text = assemble_effect(name, {}, clock)
        assert text.startswith("//!HOOK MAIN")
        assert f"//!DESC effect: {name}" in text
        assert "vec4 hook()" in text
    assert "HOOKED_texOff" in assemble_effect("bloom", {}, clock)
    assert "HOOKED_tex(" in assemble_effect("chroma", {}, clock)
    assert "hash11" in assemble_effect("glitch", {}, clock)


def test_effect_parameters_are_numeric_literals():
    """Effect knobs are validated and baked in."""
    clock = Clock(bpm=120.0, bars=8, fps=30, width=960, height=540)
    text = assemble_effect(
        "bloom", {"threshold": "0.2", "strength": "1.5", "radius": "4"}, clock
    )
    assert "smoothstep(0.2, 1.0, lum)" in text
    assert "* 1.5" in text
    assert "* 4.0" in text


def test_effect_knobs_may_be_tracks():
    """An effect pass can be animated by the scene's tracks."""
    from sdfshow.md import tables
    from sdfshow.tracks import parse_tracks

    clock = Clock(bpm=120.0, bars=8, fps=30, width=960, height=540)
    text_src = (
        "## Tracks\n\n| name | kind | values |\n|---|---|---|\n"
        "| gain | keys | 0:0.2\\|4:1.2 |\n"
    )
    tracks = parse_tracks(text_src, tables(text_src))
    text = assemble_effect("bloom", {"strength": "gain"}, clock, tracks)
    assert "float track_gain(float t)" in text
    assert "k * track_gain(t)" in text

    with pytest.raises(SystemExit, match="unknown identifier 'nope'"):
        assemble_effect("bloom", {"strength": "nope"}, clock, tracks)
