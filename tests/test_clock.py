"""Clock arithmetic: one timing truth for templates and frame counts."""

from __future__ import annotations

from sdfshow.clock import Clock


def test_derived_durations():
    """A bar is four beats and a step is a quarter of a beat."""
    clock = Clock(bpm=120.0, bars=8, fps=30, width=960, height=540)
    assert clock.beat == 0.5
    assert clock.bar == 2.0
    assert clock.step == 0.125
    assert clock.duration == 16.0
    assert clock.frames == 480


def test_frame_at_is_clamped():
    """A seek outside the show lands on a real frame."""
    clock = Clock(bpm=100.0, bars=4, fps=24, width=640, height=360)
    assert clock.frame_at(0.0) == 0
    assert clock.frame_at(1.0) == 24
    assert clock.frame_at(-1.0) == 0
    assert clock.frame_at(10_000.0) == clock.frames - 1


def test_frame_limit_is_half_open():
    """``--to 5`` ends at frame 150, so a 5 s clip is exactly 5 s long."""
    clock = Clock(bpm=120.0, bars=8, fps=30, width=960, height=540)
    assert clock.frame_limit(0.0) == 0
    assert clock.frame_limit(5.0) == 150
    assert clock.frame_limit(clock.duration) == clock.frames
    assert clock.frame_limit(10_000.0) == clock.frames


def test_tokens_are_seconds():
    """Clock tokens substituted into templates are durations in seconds."""
    clock = Clock(bpm=120.0, bars=8, fps=30, width=960, height=540)
    tokens = clock.tokens()
    assert tokens["bar"] == "2"
    assert tokens["beat"] == "0.5"
    assert tokens["step"] == "0.125"
    assert tokens["frames"] == "480"
