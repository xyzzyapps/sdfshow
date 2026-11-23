"""Render the numpy bubble masks to a PNG, so text bugs are visible at once.

    .venv\\Scripts\\python.exe tools/bubble_png.py

Writes ``output/fontprobe/bubble.png``: white panel, black ink, on mid grey.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from sdfshow import config as C  # noqa: E402
from sdfshow.textmask import bubble  # noqa: E402


def main() -> int:
    """Compose one bubble and write it as an 8-bit PNG."""
    import subprocess

    item = bubble("So who is she anyway?", cap=54, tail_right=False)
    panel = item.panel
    ink = item.ink
    rgb = np.empty((*panel.shape, 3), np.uint8)
    value = panel * (235.0 - 205.0 * ink) + (1.0 - panel) * 60
    rgb[...] = np.clip(value, 0, 255).astype(np.uint8)[..., None]
    out = C.OUTPUT / "fontprobe"
    out.mkdir(parents=True, exist_ok=True)
    raw = out / "bubble.raw"
    raw.write_bytes(rgb.tobytes())
    png = out / "bubble.png"
    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-v",
            "error",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{panel.shape[1]}x{panel.shape[0]}",
            "-i",
            str(raw),
            str(png),
        ],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr.decode("utf-8", "replace"))
        return 1
    print(png)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
