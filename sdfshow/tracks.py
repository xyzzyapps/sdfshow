"""Animation tracks: the Markdown-facing way to move a value over time.

A track is a named scalar function of time, generated as GLSL:

``steps``   a list of values on a repeating grid of 16th-note steps (or ``span`` bars)
``bars``    one value per bar, interpolated to the next, looping
``keys``    explicit ``bar:value`` keys, piecewise interpolated, clamped outside
``expr``    a raw GLSL expression over ``t``, ``bar``, ``beat``, ``step``, ``dur``

Everything else is a number. A field parameter may therefore be a literal, a track
name, or a small arithmetic expression over track names and ``t``, e.g.
``radius=0.55*pulse``. That expression surface is deliberately tiny: identifiers are
validated against the tracks and a GLSL function whitelist, so a typo fails loudly
instead of emitting a shader that does not compile.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Identifiers a parameter expression may use besides track names.
GLSL_WORDS = frozenset(
    {
        "t",
        "PI",
        "TAU",
        "abs",
        "sin",
        "cos",
        "tan",
        "asin",
        "acos",
        "atan",
        "exp",
        "log",
        "sqrt",
        "pow",
        "floor",
        "ceil",
        "fract",
        "mod",
        "min",
        "max",
        "clamp",
        "mix",
        "step",
        "smoothstep",
        "sign",
    }
)

_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d*\.?\d+|[+\-*/(),]")
_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_NUMBER = re.compile(r"^-?\d*\.?\d+$")

KINDS = ("steps", "bars", "keys", "expr")


def num(value: float) -> str:
    """A float literal GLSL cannot mistake for an int (``1`` becomes ``1.0``)."""
    text = f"{value:.12g}"
    return text if ("." in text or "e" in text or "E" in text) else text + ".0"


@dataclass(frozen=True)
class Track:
    """One named animation track."""

    name: str
    kind: str
    values: tuple[float, ...] = ()
    keys: tuple[tuple[float, float], ...] = ()
    expr: str = ""
    span: float = 1.0
    ease: str = "none"

    @property
    def function(self) -> str:
        """The generated GLSL function name."""
        return f"track_{self.name}"


def parse_tracks(text: str, tables) -> dict[str, Track]:
    """Read the ``## Tracks`` table (``name | kind | values | options``)."""
    out: dict[str, Track] = {}
    for header, body in tables:
        head = [h.lower() for h in header]
        if head[:3] != ["name", "kind", "values"]:
            continue
        for row in body:
            if not row or not row[0]:
                continue
            name = row[0]
            if not _NAME.match(name):
                raise SystemExit(f"fields.md: bad track name '{name}'")
            if name in out:
                raise SystemExit(f"fields.md: duplicate track '{name}'")
            kind = row[1].strip().lower()
            if kind not in KINDS:
                raise SystemExit(
                    f"fields.md: track '{name}' has unknown kind '{kind}' "
                    f"(use {'/'.join(KINDS)})"
                )
            values_text = row[2] if len(row) > 2 else ""
            options = _options(row[3] if len(row) > 3 else "")
            out[name] = _make(name, kind, values_text, options)
    return out


def _options(cell: str) -> dict[str, str]:
    """Parse a ``key=value, key=value`` option cell."""
    out: dict[str, str] = {}
    for part in cell.split(","):
        if "=" in part:
            key, value = part.split("=", 1)
            out[key.strip().lower()] = value.strip()
    return out


def _numbers(name: str, text: str) -> tuple[float, ...]:
    """Parse a ``|``-separated numeric list."""
    items = [p.strip() for p in text.split("|") if p.strip()]
    if not items:
        raise SystemExit(f"fields.md: track '{name}' has no values")
    try:
        return tuple(float(v) for v in items)
    except ValueError as exc:
        raise SystemExit(f"fields.md: track '{name}' has a non-numeric value") from exc


def _key_list(name: str, text: str) -> tuple[tuple[float, float], ...]:
    """Parse ``bar:value|bar:value`` keys, sorted by bar."""
    out: list[tuple[float, float]] = []
    for part in text.split("|"):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise SystemExit(f"fields.md: track '{name}' key '{part}' is not bar:value")
        bar_text, value_text = part.split(":", 1)
        try:
            out.append((float(bar_text), float(value_text)))
        except ValueError as exc:
            raise SystemExit(
                f"fields.md: track '{name}' key '{part}' is not numeric"
            ) from exc
    if not out:
        raise SystemExit(f"fields.md: track '{name}' has no keys")
    out.sort()
    if len({k for k, _ in out}) != len(out):
        raise SystemExit(f"fields.md: track '{name}' has two keys on the same bar")
    return tuple(out)


def _make(name: str, kind: str, values: str, options: dict[str, str]) -> Track:
    """Build and validate one track from its table row."""
    span = float(options.get("span", "1"))
    ease = options.get("ease", "none").lower()
    if span <= 0:
        raise SystemExit(f"fields.md: track '{name}' span must be positive")
    if ease not in ("none", "smooth"):
        raise SystemExit(f"fields.md: track '{name}' ease must be none or smooth")

    if kind in ("steps", "bars"):
        return Track(name, kind, values=_numbers(name, values), span=span, ease=ease)
    if kind == "keys":
        return Track(name, kind, keys=_key_list(name, values), ease=ease)
    expr = values.strip()
    if not expr:
        raise SystemExit(f"fields.md: track '{name}' has an empty expression")
    return Track(name, kind, expr=expr)


def expression(value: str, tracks: dict[str, Track]) -> str:
    """Validate a parameter expression and expand track names into calls.

    ``0.55*pulse + 0.1`` becomes ``0.55*track_pulse(t) + 0.1``. Unknown identifiers
    raise: the shader is never emitted with a name that cannot resolve.
    """
    if _NUMBER.match(value.strip()):
        return num(float(value.strip()))
    allowed = set(tracks) | GLSL_WORDS
    for match in _TOKEN.finditer(value):
        token = match.group(0)
        if not (token[0].isalpha() or token[0] == "_"):
            continue
        if token not in allowed:
            raise SystemExit(
                f"fields.md: unknown identifier '{token}' in '{value}' "
                "(add a track, or use a literal number)"
            )
    leftover = _TOKEN.sub(" ", value)
    if leftover.strip():
        raise SystemExit(f"fields.md: bad character in expression '{value}'")

    def repl(match: re.Match[str]) -> str:
        token = match.group(0)
        return f"{tracks[token].function}(t)" if token in tracks else token

    return _TOKEN.sub(repl, value)


def glsl(track: Track) -> str:
    """Generate the track's GLSL function definition."""
    if track.kind == "expr":
        return (
            f"float {track.function}(float t) {{\n"
            f"    return ({track.expr});\n"
            f"}}\n"
        )
    if track.kind in ("steps", "bars"):
        return _glsl_list(track)
    return _glsl_keys(track)


def _glsl_list(track: Track) -> str:
    """Steps/bars: a looping list sampled with linear or smooth interpolation."""
    count = len(track.values)
    span = track.span if track.kind == "steps" else float(count)
    values = ", ".join(num(v) for v in track.values)
    smooth = "    f = smoothstep(0.0, 1.0, f);\n" if track.ease == "smooth" else ""
    return (
        f"float {track.function}(float t) {{\n"
        f"    const int N = {count};\n"
        f"    float v[N] = float[N]({values});\n"
        f"    float span = BAR * {num(span)};\n"
        f"    float u = mod(t, span) / span * float(N);\n"
        f"    int i = int(floor(u)) % N;\n"
        f"    int j = (i + 1) % N;\n"
        f"    float f = fract(u);\n"
        f"{smooth}"
        f"    return mix(v[i], v[j], f);\n"
        f"}}\n"
    )


def _glsl_keys(track: Track) -> str:
    """Keys: piecewise interpolation between explicit bar:value points."""
    lines = [
        f"float {track.function}(float t) {{",
        "    float x = t / BAR;",
        f"    float v = {num(track.keys[0][1])};",
    ]
    for index in range(1, len(track.keys)):
        prev_bar = track.keys[index - 1][0]
        bar, value = track.keys[index]
        if track.ease == "smooth":
            factor = f"smoothstep({num(prev_bar)}, {num(bar)}, x)"
        else:
            factor = f"clamp((x - {num(prev_bar)}) / {num(bar - prev_bar)}, 0.0, 1.0)"
        lines.append(f"    v = mix(v, {num(value)}, {factor});")
    lines.append("    return v;")
    lines.append("}")
    return "\n".join(lines) + "\n"
