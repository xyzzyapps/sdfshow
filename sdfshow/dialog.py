"""Dialogue: bubble lines for the screen, and the same lines as speech audio.

One table drives both. A ``## Dialogue`` row is

    | speaker | bars      | text                          | voice |

``speaker`` is the name of a character field, ``bars`` is a bar range so a line can
hold the screen while it is spoken, ``text`` is what the bubble shows *and* what the
synthesizer says, and ``voice`` names a TTS voice.

Keeping one source means the bubble and the audio cannot drift apart: the bubble's
visibility window and the audio's placement both come from ``bars``, and the string the
renderer draws is the string that was spoken.
"""

from __future__ import annotations

import wave
from dataclasses import dataclass
from pathlib import Path

from . import config as C
from .md import table_after

# Longest bubble line that still fits inside a panel at the default size. A longer
# line is a data error rather than a silently cramped bubble.
MAX_CHARS = 34


@dataclass(frozen=True)
class Line:
    """One spoken line, and the bubble that shows it."""

    speaker: str
    lo: int
    hi: int
    text: str
    voice: str = "kal"

    @property
    def glsl(self) -> str:
        """The line as upper-case GLSL string data."""
        return self.text.upper()


def parse(text: str) -> list[Line]:
    """Read the ``## Dialogue`` table, validating each row."""
    found = table_after(text, "Dialogue")
    if found is None:
        return []
    _header, body = found
    lines: list[Line] = []
    for row in body:
        if not row or not row[0]:
            continue
        if len(row) < 3:
            raise SystemExit(
                "show.md: a Dialogue row needs speaker | bars | text (got "
                + " | ".join(row)
                + ")"
            )
        speaker = row[0].strip()
        span = row[1].strip()
        phrase = row[2].strip()
        voice = row[3].strip() if len(row) > 3 and row[3] else "kal"
        if "-" not in span:
            raise SystemExit(f"show.md: dialogue '{speaker}' bars must be A-B")
        lo_text, hi_text = span.split("-", 1)
        try:
            lo, hi = int(lo_text), int(hi_text)
        except ValueError as exc:
            raise SystemExit(
                f"show.md: dialogue '{speaker}' bars must be numbers"
            ) from exc
        if hi <= lo:
            raise SystemExit(f"show.md: dialogue '{speaker}' has an empty bar range")
        if not phrase:
            raise SystemExit(f"show.md: dialogue '{speaker}' has no text")
        if len(phrase) > MAX_CHARS:
            raise SystemExit(
                f"show.md: dialogue line is {len(phrase)} characters, "
                f"the limit is {MAX_CHARS}: '{phrase}'"
            )
        lines.append(Line(speaker, lo, hi, phrase, voice))
    return lines


def character(lines: list[Line], name: str) -> list[Line]:
    """The lines spoken by *name*, in table order."""
    return [line for line in lines if line.speaker == name]


def _say(text: str, voice: str, out: Path) -> float:
    """Synthesize *text* with ffmpeg's flite filter. Returns the duration."""
    import subprocess

    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            f"flite=text='{text}':voice={voice}",
            "-ar",
            str(C.MASTER_SR),
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(out),
        ],
        check=True,
        capture_output=True,
    )
    with wave.open(str(out), "rb") as wf:
        return wf.getnframes() / wf.getframerate()


def synth(show) -> Path | None:
    """Build the show's dialogue track, or return ``None`` if there is no dialogue.

    Each line is synthesized separately, then placed at its bar and summed. The result
    is one mono WAV at the master rate, ready to mux.
    """
    lines = getattr(show, "dialogue", [])
    if not lines:
        return None
    work = show.logs / "vox"
    work.mkdir(parents=True, exist_ok=True)
    bar = show.clock.bar
    duration = show.clock.duration

    parts: list[str] = []
    for index, line in enumerate(lines):
        wav = work / f"{index:02d}.wav"
        length = _say(line.text, line.voice, wav)
        start = line.lo * bar
        if start + length > duration:
            raise SystemExit(
                f"show.md: dialogue '{line.text[:24]}...' starts at bar {line.lo} "
                f"and runs {length:.2f}s, past the end of the show"
            )
        parts.append(
            f"[{index}:a]adelay={round(start * 1000)}:all=1,"
            f"aformat=sample_fmts=fltp:channel_layouts=mono[a{index}]"
        )

    inputs: list[str] = []
    for index in range(len(lines)):
        inputs += ["-i", str(work / f"{index:02d}.wav")]
    mix = "".join(f"[a{i}]" for i in range(len(lines)))
    graph = ";".join(parts) + f";{mix}amix=inputs={len(lines)}:normalize=0[mixed]"

    out = show.logs / "dialogue.wav"
    import subprocess

    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-v",
            "error",
            *inputs,
            "-filter_complex",
            graph,
            "-map",
            "[mixed]",
            "-t",
            f"{duration:g}",
            "-ar",
            str(C.MASTER_SR),
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            str(out),
        ],
        check=True,
        capture_output=True,
    )
    return out


def emit_bubble_templates(show, gen_dir: Path, fields_dir: Path) -> list[str]:
    """Write the per-speaker bubble templates, with the text helper baked in.

    A bubble's speaker is structural, not a number, so it cannot travel through the
    parameter channel (which only carries validated expressions). Each speaker
    therefore gets two generated templates:

    ``bubble_<name>.glsl``      the panel and its tail, plain geometry
    ``bubble_<name>_ink.glsl``  the letters, slightly proud of the panel, so they can
                                carry their own darker material

    Splitting them means the text needs no relief shading to read: it is a second
    field composited by the normal material pass.
    """
    names: list[str] = []
    for line in getattr(show, "dialogue", []):
        if line.speaker not in names:
            names.append(line.speaker)
    if not names:
        return []
    gen_dir.mkdir(parents=True, exist_ok=True)
    panel = (fields_dir / "bubble.glsl").read_text(encoding="utf-8")
    ink = (fields_dir / "bubble_ink.glsl").read_text(encoding="utf-8")
    written = []
    for name in names:
        for source, suffix in ((panel, ""), (ink, "_ink")):
            target = gen_dir / f"bubble_{name.lower()}{suffix}.glsl"
            target.write_text(source.replace("{{speaker}}", name), encoding="utf-8")
            written.append(target.name)
    return written


def glsl_lines(show) -> str:
    """The GLSL string data and per-speaker text helpers, or an empty string.

    For each speaker this emits the line strings, plus ``<name>_ink(vec2, int)`` which
    returns the distance to the ink of one line at a point given in cell units, and
    ``<name>_window(int)`` which returns the line's bar window. A bubble field then
    only has to place a panel and ask for the ink.
    """
    from .glyphs import emit_string

    names: list[str] = []
    for line in getattr(show, "dialogue", []):
        if line.speaker not in names:
            names.append(line.speaker)
    if not names:
        return ""
    bar = show.clock.bar
    out: list[str] = []
    for name in names:
        own = character(show.dialogue, name)
        for index, line in enumerate(own):
            out.append(emit_string(line.text, f"{name}_{index}"))
        out.append(f"const int {name}_LINES = {len(own)};")
        # Which line is on screen at time t, or -1.
        branch = "".join(
            f"    if (t >= {line.lo * bar:.6f} && t < {line.hi * bar:.6f}) "
            f"return {i};\n"
            for i, line in enumerate(own)
        )
        out.append(f"int {name}_live(float t) {{\n{branch}    return -1;\n}}\n")
        # Ink distance for one line, in cell units (1.0 = cap height).
        pick = "".join(
            f"    if (line == {i}) c = {name}_{i}_at(idx);\n" for i in range(len(own))
        )
        count = "".join(
            f"    if (line == {i}) n = {name}_{i}_N;\n" for i in range(len(own))
        )
        # Characters advance by FONT_ADV, so the glyph under a point is the floor of
        # the position divided by the advance. Rounding to nearest shifts every index
        # by one and inks only part of each column - a barcode.
        out.append(
            f"float {name}_ink(vec2 cell, int line) {{\n"
            "    int n = 0;\n"
            f"{count}"
            "    int idx = int(floor(cell.x / FONT_ADV));\n"
            "    if (idx < 0 || idx >= n) return 1e9;\n"
            "    int c = 0;\n"
            f"{pick}"
            "    return glyph_dist(c, cell - vec2(float(idx) * FONT_ADV, 0.0));\n"
            "}\n"
            f"float {name}_width(int line) {{\n"
            "    float n = 0.0;\n"
            + "".join(
                f"    if (line == {i}) n = {name}_{i}_N;\n" for i in range(len(own))
            )
            + "    return n * FONT_ADV;\n"
            "}\n"
        )
    return "\n".join(out)
