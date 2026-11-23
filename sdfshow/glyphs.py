"""A stroke font, so text can be geometry instead of an overlay.

Every glyph is a list of polylines inside a 0..1 tall cell. A polyline becomes a
chain of capsules, which is a distance field: text therefore composes, shadows and
camera-moves like any other SDF, and needs no texture, no font file and no overlay
pass.

The cell is ``WIDTH`` wide and 1.0 tall, with y pointing up. Glyphs are drawn with
integer-ish coordinates and scaled at emission time.

Coverage is deliberately small: the capital letters, digits and the punctuation a
speech bubble needs. Adding a glyph means adding one entry to ``GLYPHS``.
"""

from __future__ import annotations

WIDTH = 0.58
SPACE = 0.34

# Each entry is a tuple of polylines; a polyline is a tuple of (x, y) points.
G = {}


def _glyph(name: str, *polylines: str) -> None:
    """Register one glyph from ``"x,y x,y ..."`` polylines."""
    parsed = []
    for line in polylines:
        points = []
        for pair in line.split():
            x, y = pair.split(",")
            points.append((float(x), float(y)))
        parsed.append(tuple(points))
    G[name] = tuple(parsed)


_glyph("A", "0,0 0.29,1 0.58,0", "0.12,0.38 0.46,0.38")
_glyph(
    "B",
    "0.02,0 0.02,1",
    "0.02,1 0.34,1 0.46,0.88 0.46,0.62 0.34,0.5 0.02,0.5",
    "0.02,0.5 0.38,0.5 0.52,0.38 0.52,0.12 0.38,0 0.02,0",
)
_glyph("C", "0.56,0.86 0.44,1 0.14,1 0,0.86 0,0.14 0.14,0 0.44,0 0.56,0.14")
_glyph("D", "0.02,0 0.02,1", "0.02,1 0.32,1 0.56,0.76 0.56,0.24 0.32,0 0.02,0")
_glyph("E", "0.54,1 0.02,1 0.02,0 0.54,0", "0.02,0.5 0.44,0.5")
_glyph("F", "0.54,1 0.02,1 0.02,0", "0.02,0.5 0.44,0.5")
_glyph(
    "G",
    "0.56,0.86 0.44,1 0.14,1 0,0.86 0,0.14 0.14,0 0.44,0 0.56,0.12 0.56,0.46 0.3,0.46",
)
_glyph("H", "0.02,0 0.02,1", "0.54,0 0.54,1", "0.02,0.5 0.54,0.5")
_glyph("I", "0.28,0 0.28,1", "0.1,1 0.46,1", "0.1,0 0.46,0")
_glyph("J", "0.48,1 0.48,0.16 0.36,0 0.14,0 0.02,0.16")
_glyph("K", "0.02,0 0.02,1", "0.54,1 0.02,0.42", "0.2,0.56 0.54,0")
_glyph("L", "0.02,1 0.02,0 0.52,0")
_glyph("M", "0.02,0 0.02,1 0.29,0.42 0.56,1 0.56,0")
_glyph("N", "0.02,0 0.02,1 0.54,0 0.54,1")
_glyph("O", "0.14,0 0.44,0 0.58,0.16 0.58,0.84 0.44,1 0.14,1 0,0.84 0,0.16 0.14,0")
_glyph("P", "0.02,0 0.02,1", "0.02,1 0.38,1 0.52,0.86 0.52,0.62 0.38,0.48 0.02,0.48")
_glyph(
    "Q",
    "0.14,0 0.44,0 0.58,0.16 0.58,0.84 0.44,1 0.14,1 0,0.84 0,0.16 0.14,0",
    "0.36,0.28 0.58,0",
)
_glyph(
    "R",
    "0.02,0 0.02,1",
    "0.02,1 0.38,1 0.52,0.86 0.52,0.62 0.38,0.48 0.02,0.48",
    "0.3,0.48 0.56,0",
)
_glyph(
    "S",
    "0.54,0.86 0.4,1 0.14,1 0.02,0.86 0.02,0.62 0.14,0.5 0.42,0.5 0.54,0.38 "
    "0.54,0.14 0.42,0 0.14,0 0.02,0.14",
)
_glyph("T", "0,1 0.58,1", "0.29,1 0.29,0")
_glyph("U", "0.02,1 0.02,0.16 0.16,0 0.42,0 0.56,0.16 0.56,1")
_glyph("V", "0,1 0.29,0 0.58,1")
_glyph("W", "0,1 0.14,0 0.29,0.62 0.44,0 0.58,1")
_glyph("X", "0,1 0.58,0", "0.58,1 0,0")
_glyph("Y", "0,1 0.29,0.5 0.58,1", "0.29,0.5 0.29,0")
_glyph("Z", "0,1 0.56,1 0.02,0 0.56,0")

_glyph(
    "0",
    "0.14,0 0.44,0 0.58,0.16 0.58,0.84 0.44,1 0.14,1 0,0.84 0,0.16 0.14,0",
    "0.08,0.18 0.5,0.82",
)
_glyph("1", "0.14,0.8 0.3,1 0.3,0", "0.1,0 0.5,0")
_glyph("2", "0,0.84 0.14,1 0.44,1 0.58,0.84 0.58,0.6 0,0 0.58,0")
_glyph(
    "3",
    "0,0.86 0.14,1 0.42,1 0.56,0.86 0.56,0.62 0.4,0.5 0.16,0.5",
    "0.4,0.5 0.56,0.36 0.56,0.14 0.42,0 0.14,0 0,0.14",
)
_glyph("4", "0.44,0 0.44,1 0,0.3 0.58,0.3")
_glyph(
    "5",
    "0.56,1 0.06,1 0.02,0.56 0.16,0.62 0.42,0.62 0.56,0.48 0.56,0.14 0.42,0 0.14,0 0,0.14",
)
_glyph(
    "6",
    "0.56,0.86 0.42,1 0.16,1 0.02,0.84 0.02,0.16 0.16,0 0.42,0 0.56,0.16 0.56,0.4 "
    "0.42,0.54 0.16,0.54 0.02,0.4",
)
_glyph("7", "0,1 0.58,1 0.2,0")
_glyph(
    "8",
    "0.16,0.5 0.02,0.64 0.02,0.86 0.16,1 0.42,1 0.56,0.86 0.56,0.64 0.42,0.5 0.16,0.5 "
    "0.02,0.36 0.02,0.14 0.16,0 0.42,0 0.56,0.14 0.56,0.36 0.42,0.5",
)
_glyph(
    "9",
    "0.56,0.5 0.42,0.36 0.16,0.36 0.02,0.5 0.02,0.86 0.16,1 0.42,1 0.56,0.86 0.56,0.14 "
    "0.42,0 0.16,0 0.02,0.14",
)

_glyph(".", "0.26,0 0.28,0.06")
_glyph(",", "0.3,0.06 0.24,-0.16")
_glyph(
    "?",
    "0.02,0.84 0.16,1 0.42,1 0.56,0.86 0.56,0.66 0.3,0.48 0.3,0.34",
    "0.3,0.06 0.32,0.12",
)
_glyph("!", "0.29,0.34 0.29,1", "0.29,0.06 0.31,0.12")
_glyph("'", "0.3,1 0.26,0.78")
_glyph("-", "0.06,0.5 0.5,0.5")
_glyph(":", "0.29,0.14 0.31,0.2", "0.29,0.62 0.31,0.68")
_glyph(";", "0.29,0.14 0.31,0.2", "0.32,0.72 0.26,0.5")

# Characters with no strokes but a real advance.
BLANK = {" "}


# Every character advances by the same amount, so a line's width is exactly
# ``len(text) * ADVANCE`` and the ink indexer can divide by it. A variable advance
# (narrow spaces, wide M) would need a per-string offset table; a monospaced stroke
# font is the right trade here.
ADVANCE = 0.72


def advance(char: str) -> float:
    """Horizontal advance for *char*, in cell widths. Uniform by design."""
    return ADVANCE


def supported(text: str) -> list[str]:
    """Characters in *text* this font cannot draw."""
    return sorted({c for c in text.upper() if c not in G and c not in BLANK})


def _segments(name: str) -> list[tuple[float, float, float, float]]:
    """A glyph's polylines flattened into segments."""
    out = []
    for line in G[name]:
        for (x1, y1), (x2, y2) in zip(line, line[1:], strict=False):
            out.append((x1, y1, x2, y2))
    return out


def emit_glyph_function(used: set[str] | None = None) -> str:
    """GLSL: ``float glyph_dist(int g, vec2 q)`` - distance to one glyph.

    ``q`` is in cell units with the glyph's left edge at x=0 and its baseline at y=0.
    Only *used* glyphs (plus anything absent from ``used``) are emitted, because a
    44-way switch of capsule chains is expensive to compile and to run; restricting it
    to the characters a show actually uses keeps the shader small.
    """
    names = sorted(G) if used is None else sorted(n for n in G if n in used)
    cases = []
    for name in names:
        body = []
        for x1, y1, x2, y2 in _segments(name):
            body.append(
                f"        d = min(d, seg(q, vec2({x1:.4f}, {y1:.4f}), "
                f"vec2({x2:.4f}, {y2:.4f})));"
            )
        index = ord(name)
        cases.append(f"    case {index}:\n" + "\n".join(body) + "\n        break;")
    return (
        "// Stroke font: every glyph is a chain of capsules. `line` is half the\n"
        "// stroke width, so the result is a true distance to the ink.\n"
        f"#define FONT_W {WIDTH:.4f}\n"
        f"#define FONT_ADV {advance('A'):.4f}\n"
        f"#define FONT_SPACE {SPACE:.4f}\n"
        "float seg(vec2 p, vec2 a, vec2 b) {\n"
        "    vec2 pa = p - a, ba = b - a;\n"
        "    float h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-9), 0.0, 1.0);\n"
        "    return length(pa - ba * h);\n"
        "}\n"
        "// Distance to a filled triangle (a, b, c), used for the bubble tail.\n"
        "float seg2(vec2 p, vec2 a, vec2 b, vec2 c) {\n"
        "    float d = min(min(seg(p, a, b), seg(p, b, c)), seg(p, c, a));\n"
        "    vec2 e0 = b - a, e1 = c - b, e2 = a - c;\n"
        "    vec2 v0 = p - a, v1 = p - b, v2 = p - c;\n"
        "    float s = sign(e0.x * e2.y - e0.y * e2.x);\n"
        "    vec2 s0 = vec2(s * (v0.x * e0.y - v0.y * e0.x), s * (v0.y * e0.x - v0.x * e0.y));\n"
        "    vec2 s1 = vec2(s * (v1.x * e1.y - v1.y * e1.x), s * (v1.y * e1.x - v1.x * e1.y));\n"
        "    vec2 s2 = vec2(s * (v2.x * e2.y - v2.y * e2.x), s * (v2.y * e2.x - v2.x * e2.y));\n"
        "    float inside = min(min(s0.x, s1.x), s2.x);\n"
        "    return inside > 0.0 ? -sqrt(d * d) : sqrt(d * d);\n"
        "}\n"
        "float glyph_dist(int g, vec2 q) {\n"
        "    float d = 1e9;\n"
        "    if (q.x < -0.08 || q.x > FONT_W + 0.08 || q.y < -0.12 || q.y > 1.12)\n"
        "        return d;\n"
        "    switch (g) {\n" + "\n".join(cases) + "\n    }\n"
        "    return d;\n"
        "}\n"
    )


def emit_string(line: str, name: str) -> str:
    """GLSL helpers for one bubble line, unique to *name*.

    A line becomes a ``const int`` array plus two accessors, so a shader can index one
    character per sample instead of testing every glyph.
    """
    text = line.upper()
    codes = ", ".join(str(ord(c)) for c in text) or "0"
    return (
        f"const int {name}_N = {len(text)};\n"
        f"const int {name}[{max(1, len(text))}] = int[{max(1, len(text))}]({codes});\n"
        f"int {name}_at(int i) {{ return (i >= 0 && i < {name}_N) ? {name}[i] : 0; }}\n"
    )
