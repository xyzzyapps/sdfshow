"""The VapourSynth script: the TIME0 hand-off that makes renders seekable."""

from __future__ import annotations

from sdfshow import config as C
from sdfshow.clock import Clock
from sdfshow.render import write_script
from sdfshow.show import Show


def _show(tmp_path, monkeypatch) -> Show:
    """A minimal show whose generated directory is under tmp_path."""
    monkeypatch.setattr(C, "GEN", tmp_path / "gen")
    show = Show(
        name="probe",
        clock=Clock(bpm=120.0, bars=2, fps=30, width=320, height=180),
    )
    show.gen.mkdir(parents=True)
    show.scene.write_text("//!HOOK MAIN\n", encoding="utf-8")
    return show


def test_time_offset_is_injected(tmp_path, monkeypatch):
    """A range render tells the shader its absolute start frame."""
    show = _show(tmp_path, monkeypatch)
    script = write_script(show, script=tmp_path / "s.vpy", time_offset=150)
    text = script.read_text(encoding="utf-8")
    assert 'replace("// @TIME0@", "#define TIME0 150")' in text
    assert "NF = 320, 180, 30, 120" in text  # 2 bars at 120 BPM and 30 fps
    assert "format=vs.YUV444P16" in text


def test_time_offset_zero_for_a_full_render(tmp_path, monkeypatch):
    """A full render starts at zero."""
    show = _show(tmp_path, monkeypatch)
    script = write_script(show, script=tmp_path / "s.vpy")
    assert "#define TIME0 0" in script.read_text(encoding="utf-8")
