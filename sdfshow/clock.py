"""The clock: one timing truth derived from ``bpm``, ``bars`` and ``fps``.

A bar is four beats; a beat is four steps. Durations are in seconds, so the same
numbers can be substituted into a GLSL template (``mod(t, {{bar}})``) and into the
Python-side frame count. The frame index is the only clock the shader sees, so a
render is seekable: frame *n* is always the same picture.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Clock:
    """Tempo and output geometry for one show."""

    bpm: float
    bars: int
    fps: int
    width: int
    height: int

    @property
    def beat(self) -> float:
        """Seconds in one beat."""
        return 60.0 / self.bpm

    @property
    def bar(self) -> float:
        """Seconds in one bar (four beats)."""
        return self.beat * 4.0

    @property
    def step(self) -> float:
        """Seconds in one 16th-note step (a quarter of a beat)."""
        return self.beat / 4.0

    @property
    def duration(self) -> float:
        """Show length in seconds."""
        return self.bars * self.bar

    @property
    def frames(self) -> int:
        """Total frames at the show's frame rate."""
        return max(1, round(self.duration * self.fps))

    def frame_at(self, seconds: float) -> int:
        """The frame index containing *seconds* (clamped to the show)."""
        return max(0, min(self.frames - 1, round(seconds * self.fps)))

    def frame_limit(self, seconds: float) -> int:
        """The exclusive end frame for *seconds* (may equal ``frames``).

        Used by ``--from/--to``: ``--to 5`` on a 30 fps show ends at frame 150, so
        the clip is exactly five seconds long.
        """
        return max(0, min(self.frames, round(seconds * self.fps)))

    def tokens(self) -> dict[str, str]:
        """Timing tokens substituted into templates and parameters.

        ``bar``, ``beat``, ``step`` and ``dur`` are **durations in seconds** - the
        same convention as the fftechno project this descends from. Template code
        that wants an index writes ``floor(t / {{bar}})``.
        """
        return {
            "beat": _num(self.beat),
            "bar": _num(self.bar),
            "step": _num(self.step),
            "dur": _num(self.duration),
            "frames": str(self.frames),
            "fps": str(self.fps),
            "w": str(self.width),
            "h": str(self.height),
        }


def _num(value: float) -> str:
    """A decimal GLSL can parse, without a trailing ``.0`` on integers."""
    return f"{value:.12f}".rstrip("0").rstrip(".")
