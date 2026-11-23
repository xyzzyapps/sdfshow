"""Speech bubbles as numpy SDFs, composited by VapourSynth.

Text is drawn by evaluating the stroke font in :mod:`sdfshow.glyphs` and taking
coverage - signed-distance text rendering, with the field computed at build time
instead of sampled from a texture atlas. A bubble becomes two float masks (panel and
ink), which the generated VapourSynth script blends over the finished frame. Text does
not animate, so the per-frame cost is one copy.

Lines are word-wrapped and the cap height is reduced until the bubble fits its budget,
because a bubble that overruns the frame is worse than smaller type.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np

from .glyphs import ADVANCE, G

PAD_X = 0.55
PAD_Y = 0.42
LINE_GAP = 0.34
RADIUS = 0.30
TAIL_W = 0.30
TAIL_H = 0.62
STROKE = 0.135


@dataclass(frozen=True)
class Bubble:
    """Two coverage masks plus the box they occupy, in pixels."""

    panel: np.ndarray
    ink: np.ndarray
    lines: tuple[str, ...]

    @property
    def size(self) -> tuple[int, int]:
        """``(width, height)`` in pixels."""
        return (int(self.panel.shape[1]), int(self.panel.shape[0]))


def _segment_distance(
    x: np.ndarray, y: np.ndarray, ax: float, ay: float, bx: float, by: float
) -> np.ndarray:
    """Distance from every point in *x*/*y* to the segment a-b."""
    dx, dy = bx - ax, by - ay
    denom = dx * dx + dy * dy
    if denom < 1e-12:
        return np.hypot(x - ax, y - ay)
    t = np.clip(((x - ax) * dx + (y - ay) * dy) / denom, 0.0, 1.0)
    return np.hypot(x - (ax + t * dx), y - (ay + t * dy))


def _coverage(distance: np.ndarray, half: float) -> np.ndarray:
    """Signed distance to antialiased coverage: 1 inside, 0 outside.

    *half* is the half-width of the shape in pixels. The transition is one pixel wide,
    which is the antialiasing: no supersampling, no texture, and it stays crisp at any
    scale because the field is analytic.
    """
    return np.clip(0.5 + (half - distance), 0.0, 1.0)


def wrap(text: str, cap: float, max_width: float) -> list[str]:
    """Greedy word wrap of *text* at *cap* pixels per cap height."""
    advance = ADVANCE * cap
    limit = max(6, int(max_width / advance))
    words = text.upper().split()
    if not words:
        return [""]
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= limit or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def fit(
    text: str, cap: float, max_width: float, max_lines: int = 3
) -> tuple[list[str], float]:
    """Wrap *text* and shrink *cap* until it fits in *max_lines*."""
    for _ in range(24):
        lines = wrap(text, cap, max_width)
        widest = max(len(line) for line in lines) * ADVANCE * cap
        if len(lines) <= max_lines and widest <= max_width:
            return lines, cap
        cap *= 0.93
    return wrap(text, cap, max_width)[:max_lines], cap


def text_mask(
    lines: list[str], cap: float, stroke: float = STROKE, pad: float = 0.12
) -> np.ndarray:
    """Coverage mask for a stack of lines, glyphs drawn as capsule chains."""
    advance = ADVANCE * cap
    cols = max((len(line) for line in lines), default=1)
    width = round(advance * cols) + 1
    row = cap * (1.0 + LINE_GAP)
    # Glyphs are drawn from a baseline upwards, so the first baseline must sit one full
    # cap height below the top edge plus the padding. Getting this wrong clips the tops of
    # the first line's letters - the canvas is sized from the same numbers, so the two
    # must agree.
    baseline0 = cap * (1.0 + pad)
    height = round(baseline0 + row * (len(lines) - 1) + cap * pad) + 1
    usable = np.full((height, width), 1e9, np.float32)
    for row_index, text in enumerate(lines):
        baseline = baseline0 + row_index * row
        for index, char in enumerate(text):
            strokes = G.get(char)
            if not strokes:
                continue
            x0 = index * advance
            for line in strokes:
                for (ax, ay), (bx, by) in itertools.pairwise(line):
                    lo_x = int(max(0, np.floor(x0 + min(ax, bx) * cap - cap)))
                    hi_x = int(min(width, np.ceil(x0 + max(ax, bx) * cap + cap) + 1))
                    lo_y = int(max(0, np.floor(baseline - max(ay, by) * cap - cap)))
                    hi_y = int(
                        min(height, np.ceil(baseline - min(ay, by) * cap + cap) + 1)
                    )
                    if lo_x >= hi_x or lo_y >= hi_y:
                        continue
                    ys, xs = np.mgrid[lo_y:hi_y, lo_x:hi_x]
                    d = _segment_distance(
                        xs.astype(np.float32) + 0.5,
                        ys.astype(np.float32) + 0.5,
                        x0 + ax * cap,
                        baseline - ay * cap,
                        x0 + bx * cap,
                        baseline - by * cap,
                    )
                    block = usable[lo_y:hi_y, lo_x:hi_x]
                    np.minimum(block, d, out=block)

    return _coverage(usable, stroke * cap * 0.5)


def _rounded_box(h: int, w: int, radius: float, cx: float, cy: float) -> np.ndarray:
    """Signed distance to a rounded box centred at (cx, cy)."""
    ys, xs = np.mgrid[0:h, 0:w]
    dx = np.abs(xs.astype(np.float32) + 0.5 - cx) - (w * 0.5 - radius)
    dy = np.abs(ys.astype(np.float32) + 0.5 - cy) - (h * 0.5 - radius)
    outside = np.hypot(np.maximum(dx, 0.0), np.maximum(dy, 0.0))
    inside = np.minimum(np.maximum(dx, dy), 0.0)
    return outside + inside - radius


def bubble(
    text: str,
    cap: float,
    tail_right: bool,
    max_width: float,
    max_lines: int = 3,
    panel_scale: float = 1.0,
) -> Bubble:
    """A wrapped bubble: rounded panel, a tail, and the ink inside it.

    *cap* is the cap height of the type; *panel_scale* pads the panel relative to the
    type. They are separate on purpose: shrinking the type must not shrink the bubble,
    because a smaller bubble is harder to read than smaller letters inside a comfortable
    one.
    """
    lines, cap = fit(text, cap, max_width, max_lines)
    ink = text_mask(lines, cap)
    ink_h, ink_w = ink.shape

    scale = cap * panel_scale
    pad_x = round(PAD_X * scale)
    pad_y = round(PAD_Y * scale)
    tail_h = round(TAIL_H * scale) + 2
    radius = RADIUS * scale

    w = ink_w + 2 * pad_x
    body_h = ink_h + 2 * pad_y
    h = body_h + tail_h

    panel = np.pad(
        _rounded_box(body_h, w, radius, w / 2.0, body_h / 2.0),
        ((0, tail_h), (0, 0)),
        constant_values=1e9,
    )

    # Tail: an isosceles triangle from the panel's bottom edge to a point below it,
    # leaning towards its own character.
    tip_x = w * (0.78 if tail_right else 0.22)
    base_x = w * (0.58 if tail_right else 0.42)
    ys, xs = np.mgrid[0:h, 0:w]
    span = np.clip((ys - body_h) / max(tail_h, 1), 0.0, 1.0)
    centre = base_x + (tip_x - base_x) * span
    half = (1.0 - span) * TAIL_W * scale * 0.5
    tail = np.where(ys >= body_h, np.abs(xs - centre) - half, 1e9)
    panel = np.minimum(panel, tail)

    out_ink = np.zeros((h, w), np.float32)
    out_ink[pad_y : pad_y + ink_h, pad_x : pad_x + ink_w] = ink
    return Bubble(_coverage(panel, 0.0), out_ink, tuple(lines))
