"""The Markdown reader: scalars, tables and escaped pipes."""

from __future__ import annotations

from sdfshow.md import cells, kv_table, rows, scalars, table_after, tables

TEXT = """\
bpm: 120
bars: 8

## Fields

| field | template |
|-------|----------|
| core  | sphere   |

## Tracks

| name  | kind  | values       |
|-------|-------|--------------|
| pulse | steps | 1\\|0.5\\|0.2 |
"""


def test_scalars():
    """Scalars are single-token key/value lines."""
    assert scalars(TEXT) == {"bpm": "120", "bars": "8"}


def test_cells_keep_escaped_pipes():
    """An escaped pipe stays inside a cell as a literal pipe."""
    assert cells("| pulse | steps | 1\\|0.5\\|0.2 |") == [
        "pulse",
        "steps",
        "1|0.5|0.2",
    ]


def test_tables_and_rows():
    """Tables are found by header, case-insensitively."""
    assert len(tables(TEXT)) == 2
    assert rows(TEXT, ["NAME", "KIND", "VALUES"]) == [["pulse", "steps", "1|0.5|0.2"]]
    assert rows(TEXT, ["field", "template"]) == [["core", "sphere"]]


def test_kv_table():
    """A two-column table becomes a dict."""
    text = "| key | value |\n|---|---|\n| a | 1 |\n| b | 2 |\n"
    assert kv_table(text) == {"a": "1", "b": "2"}


def test_table_after_ignores_documentation_tables():
    """A prose table before the heading does not become data."""
    text = (
        "| bars | scene |\n|---|---|\n| 0-4 | intro |\n\n"
        "## Sections\n\n| bars | a |\n|---|---|\n| 0-4 | u |\n"
    )
    found = table_after(text, "Sections")
    assert found is not None
    assert found[0] == ["bars", "a"]
    assert found[1] == [["0-4", "u"]]
    assert table_after(text, "Materials") is None
