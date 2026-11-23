"""Shader assembly: the whole scene is one inspectable artifact."""

from __future__ import annotations

from sdfshow import config as C
from sdfshow.fields import load
from sdfshow.glsl import assemble
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
