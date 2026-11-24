"""Bubble masks: the type inside the panel, and the tail that points at a speaker."""

from __future__ import annotations

import numpy as np

from sdfshow import textmask


def test_first_line_is_not_clipped():
    """The canvas must leave a full cap height above the first baseline.

    This is the regression that put every first line's top row outside the mask: the
    canvas was sized from one set of numbers and the baseline placed from another.
    """
    cap = 20
    mask = textmask.text_mask(["HELLO"], cap)
    assert mask[0].max() == 0.0, "ink in the top row means the first line is clipped"
    assert mask[:cap].max() > 0.5, "the first line should be inside the canvas"


def test_wrap_never_exceeds_the_width():
    cap = 14
    max_width = 240
    lines = textmask.wrap("WE HAVE BEEN SITTING HERE FOR AN HOUR", cap, max_width)
    assert len(lines) > 1
    for line in lines:
        assert len(line) * textmask.ADVANCE * cap <= max_width + cap


def test_fit_respects_the_line_budget():
    lines, _cap = textmask.fit(
        "THE FURNITURE MOVED WITH US AND NOBODY SAID ANYTHING", 40, 200, max_lines=2
    )
    assert len(lines) <= 2


def test_panel_scale_grows_the_bubble_not_the_type():
    """`panel` is padding, so it must not change the ink size."""
    plain = textmask.bubble("HELLO THERE", 16, True, 400, panel_scale=1.0)
    padded = textmask.bubble("HELLO THERE", 16, True, 400, panel_scale=2.0)
    assert padded.size[0] > plain.size[0]
    assert padded.size[1] > plain.size[1]
    # The ink is the same glyphs at the same cap height, only placed in a bigger panel.
    assert np.isclose(padded.ink.sum(), plain.ink.sum(), rtol=1e-6)


def test_tail_points_at_the_requested_fraction():
    """The tail is how a bubble says who is talking; it must lean where it is asked."""
    for tip in (0.2, 0.8):
        item = textmask.bubble(
            "THIS IS NOT THE SAME ROOM", 16, tip > 0.5, 400, tip_frac=tip
        )
        panel = item.panel
        h, w = panel.shape
        tail = panel[int(h * 0.88) :]
        _ys, xs = np.nonzero(tail > 0.5)
        assert len(xs), "the tail should have coverage"
        centroid = xs.mean() / w
        assert abs(centroid - tip) < 0.2, f"tail at {centroid:.2f}, wanted {tip}"


def test_caption_is_ink_inside_a_thin_outline():
    """A caption is not a panel: the alpha is the ink grown by a couple of pixels."""
    cap = textmask.caption("MAPS LIE.", 18, 600)
    assert np.all(cap.panel >= cap.ink), "every glyph must be inside the alpha"
    assert cap.panel.sum() > cap.ink.sum(), "there must be an outline ring"
    ratio = float(cap.panel.sum()) / float(cap.ink.sum())
    assert ratio < 4.0, f"outline grew to {ratio:.2f}x the ink - that is a panel"
