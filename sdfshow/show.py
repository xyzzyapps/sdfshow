"""``show.md``: the clock, the stage, the field order and the arrangement.

The arrangement is a ``Sections`` table. Rows are bar ranges; columns are fields;
cells are composition operators. Unlike a gain matrix, the operators are
order-dependent because a distance field composes by ``min``/``max``:

``u``      union (the default base)
``u<k>``   smooth union with blend radius *k*
``s<k>``   smooth subtraction
``i<k>``   smooth intersection
``x``      absent

Row order is semantic: the table is applied top to bottom, and the first union in
a row becomes that row's base field.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from . import config as C
from .clock import Clock
from .md import kv_table, rows, scalars

_CELL = re.compile(r"^(?P<op>[usix])(?P<k>[0-9]*\.?[0-9]+)?$")
_RANGE = re.compile(r"^\s*(\d+)\s*-\s*(\d+)\s*$")

PATTERNS = ("none", "checker", "grid", "stripes")


@dataclass(frozen=True)
class Material:
    """A field's base colour and an optional procedural surface pattern."""

    color: tuple[float, float, float]
    pattern: str = "none"
    scale: float = 1.0


def pattern_id(name: str) -> int:
    """The integer used for *name* in the generated shader."""
    if name not in PATTERNS:
        raise SystemExit(
            f"show.md: unknown material pattern '{name}' " f"(use {'/'.join(PATTERNS)})"
        )
    return PATTERNS.index(name)


@dataclass(frozen=True)
class Cell:
    """One arrangement cell: a composition operator and its blend radius."""

    op: str
    k: float = 0.0

    @property
    def active(self) -> bool:
        """Is the field present in this section?"""
        return self.op != "x"


def cell(text: str, where: str = "") -> Cell:
    """Parse an arrangement cell (``u``, ``u0.35``, ``s0.1``, ``i``, ``x``)."""
    raw = text.strip().lower()
    if raw in ("", "x", "0"):
        return Cell("x")
    match = _CELL.fullmatch(raw)
    if not match:
        raise SystemExit(
            f"show.md: bad section cell '{text}'"
            + (f" in {where}" if where else "")
            + " (use u, u<k>, s<k>, i<k> or x)"
        )
    return Cell(match.group("op"), float(match.group("k") or 0.0))


@dataclass
class Section:
    """A bar range and the composition state of every field inside it."""

    lo: int
    hi: int
    cells: dict[str, Cell] = field(default_factory=dict)


@dataclass
class Show:
    """A parsed ``show.md``."""

    name: str
    clock: Clock
    stage: dict[str, str] = field(default_factory=dict)
    fields_order: list[str] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)
    materials: dict[str, Material] = field(default_factory=dict)
    audio: str = ""

    @property
    def dir(self) -> Path:
        """The show's folder under ``shows/``."""
        return C.SHOWS / self.name

    @property
    def show_md(self) -> Path:
        """Path to ``show.md``."""
        return self.dir / "show.md"

    @property
    def fields_md(self) -> Path:
        """Path to ``fields.md``."""
        return self.dir / "fields.md"

    @property
    def gen(self) -> Path:
        """Directory for this show's generated shader and score."""
        return C.GEN / self.name

    @property
    def output(self) -> Path:
        """Directory for this show's renders and logs."""
        return C.OUTPUT / self.name

    @property
    def logs(self) -> Path:
        """Directory for build logs and the lock."""
        return self.output / "logs"

    @property
    def scene(self) -> Path:
        """The generated libplacebo shader."""
        return self.gen / "scene.glsl"

    @property
    def script(self) -> Path:
        """The generated VapourSynth script."""
        return self.gen / "render.vpy"

    @property
    def lock(self) -> Path:
        """The build-lock file."""
        return self.logs / ".build.lock"

    @property
    def video(self) -> Path:
        """The master video path (versioned by the renderer)."""
        return self.output / "show.mp4"

    def stage_value(self, key: str) -> str:
        """A stage value with its default applied."""
        return self.stage.get(key, C.STAGE_DEFAULTS.get(key, ""))


def parse(name: str, path: Path) -> Show:
    """Parse ``show.md`` and validate the arrangement against the field order."""
    text = path.read_text(encoding="utf-8")
    scalar = scalars(text)
    for key in ("bpm", "bars", "fps"):
        if key not in scalar:
            raise SystemExit(f"show.md: missing scalar '{key}'")

    width, height = 1280, 720
    size = scalar.get("size", "")
    if size:
        match = re.fullmatch(r"(\d+)[xX](\d+)", size)
        if not match:
            raise SystemExit(f"show.md: 'size' must be WxH (got '{size}')")
        width, height = int(match.group(1)), int(match.group(2))

    clock = Clock(
        bpm=float(scalar["bpm"]),
        bars=int(float(scalar["bars"])),
        fps=int(float(scalar["fps"])),
        width=width,
        height=height,
    )
    if clock.bpm <= 0 or clock.bars <= 0 or clock.fps <= 0:
        raise SystemExit("show.md: bpm, bars and fps must be positive")

    order = [row[0] for row in rows(text, ["field"]) if row and row[0]]
    if not order:
        raise SystemExit("show.md: missing Fields table")
    if len(set(order)) != len(order):
        raise SystemExit("show.md: Fields has a duplicate name")

    show = Show(
        name=name,
        clock=clock,
        stage=kv_table(text),
        fields_order=order,
        audio=scalar.get("audio", ""),
    )

    for header, body in _sections_tables(text):
        cols = [h for h in header[1:] if h]
        for col in cols:
            if col not in order:
                raise SystemExit(
                    f"show.md: Sections column '{col}' is not in the Fields table"
                )
        for row in body:
            match = _RANGE.match(row[0])
            if not match:
                raise SystemExit(f"show.md: bad section range '{row[0]}'")
            lo, hi = int(match.group(1)), int(match.group(2))
            section = Section(lo, hi)
            for index, col in enumerate(cols):
                section.cells[col] = cell(
                    row[index + 1] if index + 1 < len(row) else "", f"{lo}-{hi}"
                )
            show.sections.append(section)

    for _header, body in _material_tables(text):
        for row in body:
            if len(row) < 2 or not row[0]:
                continue
            if row[0] not in order:
                raise SystemExit(
                    f"show.md: Materials row '{row[0]}' is not in the Fields table"
                )
            parts = [p.strip() for p in row[1].split("|") if p.strip()]
            if len(parts) != 3:
                raise SystemExit(
                    f"show.md: material '{row[0]}' must be r|g|b (got '{row[1]}')"
                )
            try:
                color = tuple(float(p) for p in parts)
            except ValueError as exc:
                raise SystemExit(
                    f"show.md: material '{row[0]}' is not numeric"
                ) from exc
            pattern = row[2].strip().lower() if len(row) > 2 and row[2] else "none"
            pattern_id(pattern)
            scale = 1.0
            if len(row) > 3 and row[3]:
                try:
                    scale = float(row[3])
                except ValueError as exc:
                    raise SystemExit(
                        f"show.md: material '{row[0]}' scale is not a number"
                    ) from exc
            show.materials[row[0]] = Material(color, pattern, scale)  # type: ignore[arg-type]

    if not show.sections:
        # No arrangement: every field is unioned for the whole show.
        show.sections = [Section(0, clock.bars, {name: Cell("u") for name in order})]

    _check(show)
    return show


def _sections_tables(text: str):
    """Yield the single table that follows ``## Sections``."""
    from .md import table_after

    found = table_after(text, "Sections")
    if found is not None:
        yield found


def _material_tables(text: str):
    """Yield the single table that follows ``## Materials``."""
    from .md import table_after

    found = table_after(text, "Materials")
    if found is not None:
        yield found


def _check(show: Show) -> None:
    """Sections must cover ``0..bars`` with no gap, and place every field."""
    end = 0
    for section in show.sections:
        if section.hi <= section.lo:
            raise SystemExit(f"show.md: section {section.lo}-{section.hi} is empty")
        if section.lo != end:
            raise SystemExit(
                f"show.md: section {section.lo}-{section.hi} does not follow bar {end}"
            )
        end = section.hi
    if end != show.clock.bars:
        raise SystemExit(
            f"show.md: sections end at bar {end}, but bars is {show.clock.bars}"
        )
    for section in show.sections:
        missing = [f for f in show.fields_order if f not in section.cells]
        if missing:
            raise SystemExit(
                f"show.md: section {section.lo}-{section.hi} has no cell for "
                + ", ".join(missing)
            )
        active = [name for name in show.fields_order if section.cells[name].active]
        if active and section.cells[active[0]].op != "u":
            raise SystemExit(
                f"show.md: section {section.lo}-{section.hi} starts with a "
                f"'{section.cells[active[0]].op}' cell for '{active[0]}'; the first "
                "active field of a section must be a union"
            )


def names() -> list[str]:
    """Show names: the folders under ``shows/``."""
    if not C.SHOWS.exists():
        return []
    return sorted(p.name for p in C.SHOWS.iterdir() if p.is_dir())


def load(name: str) -> Show:
    """Return the parsed show called *name*."""
    if name not in names():
        raise SystemExit(
            f"unknown show '{name}' (have: {', '.join(names()) or 'none'})"
        )
    return parse(name, C.SHOWS / name / "show.md")
