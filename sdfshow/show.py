"""``show.md``: the clock, the stage, the field order and the arrangement.

The arrangement is a ``Sections`` table. Rows are bar ranges; columns are fields;
cells are composition operators. Unlike a gain matrix, the operators are
order-dependent because a distance field composes by ``min``/``max``:

``u``      union (the default base)
``u<k>``   smooth union with blend radius *k*
``s<k>``   smooth subtraction
``i<k>``   smooth intersection
``m<w>``   morph: ``mix`` the accumulated field towards this one by *w*
``x``      absent

The operand after the operator may be a number or a track name, so a blend radius or
a morph weight can be animated. Row order is semantic: the table is applied top to
bottom, and the first union in a row becomes that row's base field. A morph cannot
start a row, because there is nothing to blend from.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import config as C
from . import dialog
from .clock import Clock
from .dialog import Line
from .md import kv_table, rows, scalars, table_after

_CELL = re.compile(r"^(?P<op>[usixm])(?P<k>.*)$")
_RANGE = re.compile(r"^\s*(\d+)\s*-\s*(\d+)\s*$")

PATTERNS = ("none", "checker", "grid", "stripes")
OPS = ("u", "s", "i", "x", "m")


@dataclass(frozen=True)
class Sprite:
    """A raster sprite placed for a bar window.

    ``cell`` is the frame size in the sheet, ``frame`` its index left to right, ``x``/``y``
    the feet anchor in screen units and ``height`` the sprite's height in screen units.
    """

    id: str
    sheet: Path
    cell: tuple[int, int]
    lo: float
    hi: float
    frame: int
    x: float
    y: float
    height: float


@dataclass(frozen=True)
class Material:
    """A field's base colour, an optional pattern and its outline weight.

    ``rim`` scales the layer's outline: 1 draws the full rim, 0 none. Tone layers (a lit
    cheek, a shadow panel) set 0 so the two fills meet without a dark seam; silhouettes
    keep 1.
    """

    color: tuple[float, float, float]
    pattern: str = "none"
    scale: float = 1.0
    rim: float = 1.0


def pattern_id(name: str) -> int:
    """The integer used for *name* in the generated shader."""
    if name not in PATTERNS:
        raise SystemExit(
            f"show.md: unknown material pattern '{name}' " f"(use {'/'.join(PATTERNS)})"
        )
    return PATTERNS.index(name)


@dataclass(frozen=True)
class Cell:
    """One arrangement cell: a composition operator and its blend operand.

    ``k`` is the raw text after the operator - empty, a number, or a track name
    (``u0.3``, ``m<morph>``). It is resolved to GLSL at assembly time so a cell
    blend can be animated.
    """

    op: str
    k: str = ""

    @property
    def active(self) -> bool:
        """Is the field present in this section?"""
        return self.op != "x"


def cell(text: str, where: str = "") -> Cell:
    """Parse an arrangement cell.

    ``u``/``u<k>`` union, ``s<k>`` subtract, ``i<k>`` intersect, ``m<w>`` morph
    (``mix``), ``x`` absent. The operand may be a number or a track name.
    """
    raw = text.strip().lower()
    if raw in ("", "x", "0"):
        return Cell("x")
    match = _CELL.fullmatch(raw)
    if not match:
        raise SystemExit(
            f"show.md: bad section cell '{text}'"
            + (f" in {where}" if where else "")
            + " (use u, u<k>, s<k>, i<k>, m<w> or x)"
        )
    operand = match.group("k").strip()
    if operand and not re.fullmatch(r"[A-Za-z0-9_+*/(). ]+", operand):
        raise SystemExit(
            f"show.md: bad cell operand '{operand}' in '{text}'"
            + (f" ({where})" if where else "")
        )
    return Cell(match.group("op"), operand)


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
    effects: list[str] = field(default_factory=list)
    effect_params: dict[str, dict[str, str]] = field(default_factory=dict)
    dialogue: list[Line] = field(default_factory=list)
    sprites: list[Sprite] = field(default_factory=list)
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

    dialogue = dialog.parse(text)
    bars_text = scalar["bars"].strip().lower()
    if bars_text in ("auto", "dialogue"):
        # The show ends where its speech ends. This makes "stop after the dialogue" a
        # property of the markdown instead of a number kept in step by hand.
        if not dialogue:
            raise SystemExit("show.md: bars: auto needs a ## Dialogue table to measure")
        bars = math.ceil(max(line.hi for line in dialogue))
    else:
        try:
            bars = int(float(bars_text))
        except ValueError:
            raise SystemExit(
                f"show.md: 'bars' must be a number or 'auto' (got '{scalar['bars']}')"
            ) from None

    clock = Clock(
        bpm=float(scalar["bpm"]),
        bars=bars,
        fps=int(float(scalar["fps"])),
        width=width,
        height=height,
    )
    if clock.bpm <= 0 or clock.bars <= 0 or clock.fps <= 0:
        raise SystemExit("show.md: bpm, bars and fps must be positive")

    for line in dialogue:
        if line.hi > clock.bars:
            raise SystemExit(
                f"show.md: dialogue '{line.text[:24]}...' ends at bar {line.hi}, "
                f"past the last bar ({clock.bars}); raise 'bars' or use 'auto'"
            )

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
        dialogue=dialogue,
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
            rim = 1.0
            if len(row) > 4 and row[4]:
                try:
                    rim = float(row[4])
                except ValueError as exc:
                    raise SystemExit(
                        f"show.md: material '{row[0]}' rim is not a number"
                    ) from exc
            show.materials[row[0]] = Material(color, pattern, scale, rim)  # type: ignore[arg-type]

    for name, effect_params in _effects(text).items():
        show.effects.append(name)
        show.effect_params[name] = effect_params

    fold = show.stage_value("fold").strip().lower()
    if fold not in ("none", "mirror", "kaleido"):
        raise SystemExit(
            f"show.md: stage 'fold' must be none/mirror/kaleido (got '{fold}')"
        )

    if not show.sections:
        # No arrangement: every field is unioned for the whole show.
        show.sections = [Section(0, clock.bars, {name: Cell("u") for name in order})]

    show.sprites = _sprites(text, path.parent)

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


def _effects(text: str) -> dict[str, dict[str, str]]:
    """Ordered ``{effect: {key: value}}`` from the ``## Effects`` table.

    The first appearance of an effect sets its position in the pass chain. A row
    with an empty key still registers the effect.
    """
    found = table_after(text, "Effects")
    out: dict[str, dict[str, str]] = {}
    if found is None:
        return out
    _header, body = found
    for row in body:
        if not row or not row[0]:
            continue
        name = row[0].strip().lower()
        if name not in C.EFFECTS:
            raise SystemExit(
                f"show.md: unknown effect '{name}' (use {'/'.join(C.EFFECTS)})"
            )
        params = out.setdefault(name, {})
        key = row[1].strip() if len(row) > 1 else ""
        value = row[2].strip() if len(row) > 2 else ""
        if key:
            params[key] = value
    return out


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


def _sprites(text: str, base: Path) -> list[Sprite]:
    """Read the optional ``## Sprites`` table.

    ``| id | sheet | cell | bars | frame | x | y | height |``. Rows for one id may repeat
    over bar windows; later rows win inside their window, so an idle row over the whole
    show followed by a talking row over a line is enough.
    """
    found = table_after(text, "Sprites")
    if found is None:
        return []
    _header, body = found
    out: list[Sprite] = []
    for row in body:
        if not row or not row[0]:
            continue
        if len(row) < 8:
            raise SystemExit(
                "show.md: a Sprites row needs id | sheet | cell | bars | frame | x | y | height"
            )
        ident = row[0].strip()
        sheet = Path(row[1].strip())
        if not sheet.is_absolute():
            local = base / sheet
            sheet = local if local.exists() else C.ROOT / sheet
        if not sheet.exists():
            raise SystemExit(f"show.md: sprite '{ident}' sheet not found: {sheet}")
        match = re.fullmatch(r"(\d+)[xX](\d+)", row[2].strip())
        if not match:
            raise SystemExit(f"show.md: sprite '{ident}' cell must be WxH")
        cell = (int(match.group(1)), int(match.group(2)))
        match = re.fullmatch(r"([\d.]+)-([\d.]+)", row[3].strip())
        if not match:
            raise SystemExit(f"show.md: sprite '{ident}' bars must be A-B")
        lo, hi = float(match.group(1)), float(match.group(2))
        if hi <= lo:
            raise SystemExit(f"show.md: sprite '{ident}' has an empty bar range")
        try:
            frame = int(row[4])
            x = float(row[5])
            y = float(row[6])
            height = float(row[7])
        except ValueError as exc:
            raise SystemExit(
                f"show.md: sprite '{ident}' frame/x/y/height must be numbers"
            ) from exc
        if frame < 0 or height <= 0:
            raise SystemExit(f"show.md: sprite '{ident}' frame/height out of range")
        out.append(Sprite(ident, sheet, cell, lo, hi, frame, x, y, height))
    return out
