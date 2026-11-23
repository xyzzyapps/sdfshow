"""One Markdown reader for ``show.md`` and ``fields.md``.

Scalars are ``key: value`` lines whose value is a single token. Tables split on
``|``; a ``\\|`` inside a cell is a literal pipe (so ``1\\|0\\|1`` is one cell whose
value is the list ``1|0|1``).
"""

from __future__ import annotations

import re

_SEP = re.compile(r"^\s*\|[\s:|.-]+\|\s*$")
_SCALAR = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(\S+)\s*$", re.MULTILINE)


def cells(line: str) -> list[str]:
    """Split a Markdown table row on unescaped ``|``."""
    inner = line.strip().removeprefix("|")
    if inner.endswith("|") and not inner.endswith("\\|"):
        inner = inner[:-1]
    return [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", inner)]


def scalars(text: str) -> dict[str, str]:
    """``key: value`` lines. The value is one token, substituted verbatim."""
    return {m.group(1): m.group(2) for m in _SCALAR.finditer(text)}


def tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    """Every Markdown table as ``(header cells, body rows)``."""
    found: list[tuple[list[str], list[list[str]]]] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if (
            lines[i].lstrip().startswith("|")
            and i + 1 < len(lines)
            and _SEP.match(lines[i + 1])
        ):
            header = cells(lines[i])
            body: list[list[str]] = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                body.append(cells(lines[j]))
                j += 1
            found.append((header, body))
            i = j
        else:
            i += 1
    return found


def rows(text: str, header: list[str]) -> list[list[str]]:
    """Body rows of the first table whose header matches *header* (case-insensitive)."""
    want = [h.lower() for h in header]
    for head, body in tables(text):
        if [c.lower() for c in head] == want:
            return body
    return []


def kv_table(text: str, first: str = "key", second: str = "value") -> dict[str, str]:
    """A two-column table as a dict (used by the Stage and Parameters tables)."""
    out: dict[str, str] = {}
    for row in rows(text, [first, second]):
        if len(row) >= 2 and row[0]:
            out[row[0]] = row[1]
    return out


def table_after(text: str, heading: str) -> tuple[list[str], list[list[str]]] | None:
    """The first table after a ``## <heading>`` line, or ``None``.

    Heading-based lookup keeps documentation tables (an intro table that happens to
    start with ``bars``, say) out of the data path.
    """
    lines = text.splitlines()
    want = f"## {heading}".lower()
    start = None
    for index, line in enumerate(lines):
        if line.strip().lower() == want:
            start = index + 1
            break
    if start is None:
        return None
    found = tables("\n".join(lines[start:]))
    return found[0] if found else None
