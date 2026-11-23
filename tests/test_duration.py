"""`bars: auto` ends the show where the dialogue ends."""

from __future__ import annotations

import pytest

from sdfshow.show import parse

BASE = """\
bpm: 120
bars: {bars}
fps: 30
size: 640x360

## Fields

| field |
|-------|
| core |

## Sections

| bars | core |
|------|------|
| 0-{last} | u |
{dialogue}
"""

DIALOGUE = """
## Dialogue

| speaker | bars | text | voice |
|---------|------|------|-------|
{rows}
"""


def _write(tmp_path, bars: str, last: int, rows: str):
    text = BASE.replace("{bars}", bars).replace("{last}", str(last))
    text = text.replace("{dialogue}", DIALOGUE.replace("{rows}", rows))
    path = tmp_path / "show.md"
    path.write_text(text, encoding="utf-8")
    return parse("test", path)


def test_auto_ends_at_the_last_line(tmp_path):
    show = _write(
        tmp_path,
        "auto",
        3,
        "| AINA | 1-3 | This is not the same room. | slt |",
    )
    assert show.clock.bars == 3
    assert show.clock.duration == 6.0  # three bars at 120 BPM
    assert show.clock.frames == 180


def test_auto_uses_the_latest_line_not_the_first(tmp_path):
    show = _write(
        tmp_path,
        "auto",
        7,
        "| AINA | 1-2 | One. | slt |\n| BORIS | 5-7 | Two. | rms |",
    )
    assert show.clock.bars == 7


def test_auto_without_dialogue_fails(tmp_path):
    text = BASE.replace("{bars}", "auto").replace("{last}", "4")
    text = text.replace("{dialogue}", "")
    path = tmp_path / "show.md"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(SystemExit, match="needs a ## Dialogue"):
        parse("test", path)


def test_a_line_past_the_last_bar_fails(tmp_path):
    with pytest.raises(SystemExit, match="past the last bar"):
        _write(
            tmp_path,
            "2",
            2,
            "| AINA | 1-3 | This is not the same room. | slt |",
        )


def test_bars_must_be_a_number_or_auto(tmp_path):
    with pytest.raises(SystemExit, match="number or 'auto'"):
        _write(tmp_path, "lots", 4, "")
