"""``fields.md``: field instances, their parameters, and the animation tracks.

A field is one row in the ``## Fields`` table: ``name | template | parameters``.
The template is a GLSL function body in ``fields/<template>`` with ``{{placeholder}}``
holes; the parameters fill them. There are no defaults - a missing placeholder, an
unknown identifier or a bad value fails the build by name.

Templates are written over several indented lines for readability. Blank lines and
lines whose first non-space character is ``#`` are comments; the remaining lines are
joined with a single space. Use ``//`` for a GLSL comment (a leading ``#`` is a
Markdown comment, not a preprocessor directive). A line must not split a token.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from . import config as C
from .md import scalars, tables
from .tracks import Track, expression, parse_tracks
from .tracks import glsl as track_glsl

_PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")
_CLOCKS = ("bar", "beat", "step", "dur", "frames", "fps", "w", "h")
_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class Field:
    """One instance of a GLSL SDF template."""

    name: str
    template: str
    params: dict[str, str] = field(default_factory=dict)
    body: str = ""

    @property
    def function(self) -> str:
        """The generated GLSL field function name."""
        return f"field_{self.name}"


@dataclass
class Fields:
    """A parsed ``fields.md``: globals, tracks and the field list."""

    globals: dict[str, str] = field(default_factory=dict)
    tracks: dict[str, Track] = field(default_factory=dict)
    fields: list[Field] = field(default_factory=list)

    def by_name(self) -> dict[str, Field]:
        """Fields keyed by name."""
        return {f.name: f for f in self.fields}


def split_params(cell: str) -> dict[str, str]:
    """Parse a ``key=value, key=value`` cell at top-level commas only."""
    out: dict[str, str] = {}
    depth = 0
    start = 0
    for index, char in enumerate(cell + ","):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            part = cell[start:index]
            start = index + 1
            if "=" in part:
                key, value = part.split("=", 1)
                out[key.strip()] = value.strip()
    return out


def _preprocess(text: str) -> str:
    """Drop blanks, ``#`` lines and ``//`` comments, then join lines with one space.

    ``//`` comments are removed before joining, so a comment can never swallow the
    code that follows it on the next line.
    """
    lines = []
    for raw in text.splitlines():
        line = re.sub(r"//.*$", "", raw).strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return " ".join(lines)


def _expand(values: dict[str, str], where: str) -> dict[str, str]:
    """Resolve ``{{key}}`` references *between* globals (clocks may be referenced)."""
    out = dict(values)
    for _ in range(16):
        changed = False
        for key, raw in list(out.items()):

            def repl(match: re.Match[str], current: dict[str, str] = out) -> str:
                """Substitute one placeholder from the current value map."""
                token = match.group(1)
                return current.get(token, match.group(0))

            new = _PLACEHOLDER.sub(repl, raw)
            if new != raw:
                changed = True
                out[key] = new
        if not changed:
            return out
    raise SystemExit(f"fields.md: '{where}' placeholders did not settle")


def _simple(text: str, values: dict[str, str], field_name: str) -> str:
    """Substitute every ``{{key}}``, failing by name on an unknown key."""

    def repl(match: re.Match[str]) -> str:
        """Return the value for one placeholder, or raise a named error."""
        key = match.group(1)
        if key not in values:
            raise SystemExit(f"fields.md: field '{field_name}' needs value '{key}'")
        return values[key]

    return _PLACEHOLDER.sub(repl, text)


def load(
    path: Path, clock, extra_tracks: str = "", gen_dir: Path | None = None
) -> Fields:
    """Parse ``fields.md`` and render every field body for *clock*.

    *extra_tracks* is the show's ``show.md`` text: a ``## Tracks`` table may live in
    either file, so camera tracks can sit next to the Stage table and field tracks
    next to the fields. A name defined in both files is an error.

    *gen_dir* is searched for templates before ``fields/``. Generated per-speaker
    bubble templates land there.
    """
    text = path.read_text(encoding="utf-8")
    scalar = scalars(text)
    banned = [key for key in _CLOCKS if key in scalar]
    if banned:
        raise SystemExit(
            "fields.md: "
            + ", ".join(banned)
            + " come from show.md (bpm, bars, fps, size). Delete them."
        )

    globals_ = _expand({**scalar, **clock.tokens()}, "globals")
    tracks = parse_tracks(text, tables(text))
    if extra_tracks:
        extra = parse_tracks(extra_tracks, tables(extra_tracks))
        clash = sorted(set(extra) & set(tracks))
        if clash:
            raise SystemExit(
                "tracks.md: '"
                + "', '".join(clash)
                + "' is defined in both fields.md and show.md"
            )
        tracks = {**tracks, **extra}

    read = tables(text)
    body_rows: list[list[str]] = []
    for header, body in read:
        if [h.lower() for h in header] == ["name", "template", "parameters"]:
            body_rows = body
            break
    if not body_rows:
        raise SystemExit("fields.md: missing Fields table")

    fields: list[Field] = []
    seen: set[str] = set()
    for row in body_rows:
        if not row or not row[0]:
            continue
        name = row[0]
        if not _NAME.match(name) or name in _CLOCKS:
            raise SystemExit(f"fields.md: bad field name '{name}'")
        if name in seen:
            raise SystemExit(f"fields.md: duplicate field '{name}'")
        seen.add(name)
        template = row[1] if len(row) > 1 else ""
        if not template:
            raise SystemExit(f"fields.md: field '{name}' has no template")
        params = split_params(row[2] if len(row) > 2 else "")

        values = dict(globals_)
        for key, raw in params.items():
            if not _NAME.match(key):
                raise SystemExit(f"fields.md: field '{name}' has bad key '{key}'")
            expanded = _expand({key: raw}, name)[key]
            values[key] = expression(expanded, tracks)

        # Generated templates (per-speaker bubbles) live in gen/ and win over fields/,
        # so a build artifact can never shadow the hand-written source.
        path = gen_dir / template if gen_dir and (gen_dir / template).exists() else None
        if path is None:
            path = C.FIELDS / template
        if not path.exists():
            raise SystemExit(
                f"fields.md: field '{name}' names a template that does not exist: "
                f"{template}"
            )
        body = _preprocess(path.read_text(encoding="utf-8"))
        rendered = _simple(body, values, name)
        if "return" not in rendered:
            raise SystemExit(
                f"fields.md: field '{name}' template '{template}' has no return"
            )
        if _PLACEHOLDER.search(rendered):
            raise SystemExit(f"fields.md: field '{name}' has an unresolved placeholder")
        fields.append(Field(name, template, params, rendered))
    return Fields(globals_, tracks, fields)


def render_tracks(fields: Fields) -> str:
    """The GLSL definitions for every track.

    Emitted before the camera and the dialogue helpers, because both may reference a
    track (`distance: dolly`).
    """
    return "\n".join(track_glsl(track) for track in fields.tracks.values())


def render_functions(fields: Fields) -> str:
    """The GLSL definitions for every field, in order."""
    parts: list[str] = []
    for entry in fields.fields:
        parts.append(
            f"float {entry.function}(vec3 p, float t, float sf_detail) {{\n"
            f"    {entry.body}\n"
            f"}}\n"
        )
    return "\n".join(parts)
