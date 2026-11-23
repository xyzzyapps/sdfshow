"""Global paths and constants shared by every show.

Anything show-specific lives under ``shows/<name>/``. Nothing in this module names
a particular show.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOWS = ROOT / "shows"
FIELDS = ROOT / "fields"
GEN = ROOT / "gen"
OUTPUT = ROOT / "output"
DEFAULT_SHOW = "first"

VSPIPE = ROOT / ".venv" / "Scripts" / "vspipe.exe"

# Shader defaults used when show.md's Stage table does not override a key.
STAGE_DEFAULTS: dict[str, str] = {
    "distance": "4.2",
    "yaw": "0.6",
    "pitch": "-0.18",
    "fov": "1.9",
    "target": "0|0|0",
    "fog": "0.03",
    "exposure": "1.1",
    "background": "0.02|0.025|0.04",
    "light": "0.6|0.8|0.5",
    "scanlines": "0",
    "plasma": "0",
    "grain": "0.012",
    "vignette": "0.22",
    "hue": "0",
    "fold": "none",
    "fold_count": "6",
    # 2D mode: draw flat layers instead of raymarching. `pixel` > 1 snaps the picture to
    # a pixel grid, and `outline` draws a dark rim around every layer (SVG-like cutouts).
    "mode": "3d",
    "pixel": "1",
    "outline": "0",
    "outline_color": "0.06|0.05|0.08",
}

# Allowed `## Effects` pass names, in no particular order.
EFFECTS: tuple[str, ...] = ("bloom", "chroma", "crt", "glitch")

# Raymarch and shading effort. Deliberately fixed for now (not a per-show knob) so
# the generated shader stays comparable between builds.
MARCH_STEPS = 160
AO_STEPS = 5
SHADOW_STEPS = 24
SURFACE_EPS = 0.0012

# Encode defaults (ffmpeg encodes; it never filters the picture).
VIDEO_CRF = 18
VIDEO_PRESET = "slow"
VIDEO_PIX_FMT = "yuv420p"
AUDIO_BITRATE = "192k"

# Speech synthesis runs at the master rate so it never needs resampling.
MASTER_SR = 48000
VOICES = ("awb", "kal", "kal16", "rms", "slt")


def unique_path(path: Path) -> Path:
    """Return *path*, or ``name_v2.ext`` / ``_v3`` ... if it already exists.

    Existing renders are never overwritten; a fresh name is chosen instead.
    """
    if not path.exists():
        return path
    version = 2
    while True:
        candidate = path.with_name(f"{path.stem}_v{version}{path.suffix}")
        if not candidate.exists():
            return candidate
        version += 1
