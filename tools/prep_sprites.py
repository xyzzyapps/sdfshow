"""Turn a sheet with a baked checkerboard into transparent sprite strips.

The source sheets have no alpha: the "transparency" is a drawn checkerboard, and the
pirate sheet also has a card border, a column title and a row number. Keying every light
pixel removes the checker, but it also removes the white stripes inside a sprite, so the
sprite is taken as the largest non-light component and its enclosed light regions are
filled back in as holes. The card border and the labels fall outside that component.

Run once, from the repo root:

    .venv\\Scripts\\python -m tools.prep_sprites

Reads ``p1.png`` (the boy) and ``p2.png`` (the pirate) and writes
``assets/sprites/{boy,pirate}.png``, each a horizontal strip of equally sized RGBA frames
with the feet on the bottom edge.
"""

from __future__ import annotations

import subprocess
from collections import deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "sprites"


def decode(path: Path) -> np.ndarray:
    """Decode a PNG to an ``(h, w, 3)`` int16 array."""
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    width, height = (int(v) for v in probe.stdout.strip().split(","))
    raw = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-v",
            "error",
            "-i",
            str(path),
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ],
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(raw, np.uint8).reshape(height, width, 3).astype(np.int16)


def encode(path: Path, frames: np.ndarray) -> None:
    """Write ``(n, h, w, 4)`` uint8 frames as one horizontal strip PNG."""
    path.parent.mkdir(parents=True, exist_ok=True)
    strip = np.concatenate(list(frames), axis=1)
    height, width, _ = strip.shape
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-v",
            "error",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgba",
            "-s",
            f"{width}x{height}",
            "-i",
            "-",
            str(path),
        ],
        input=strip.tobytes(),
        check=True,
    )


def _components(mask: np.ndarray):
    """Largest 4-connected component of *mask*, as ``(label, count, bbox)``."""
    height, width = mask.shape
    label = np.zeros((height, width), np.int32)
    best = (0, None, 0)
    current = 0
    for y in range(height):
        for x in range(width):
            if not mask[y, x] or label[y, x]:
                continue
            current += 1
            queue = deque([(y, x)])
            label[y, x] = current
            count = 0
            xs = []
            ys = []
            while queue:
                cy, cx = queue.popleft()
                count += 1
                xs.append(cx)
                ys.append(cy)
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if (
                        0 <= ny < height
                        and 0 <= nx < width
                        and mask[ny, nx]
                        and not label[ny, nx]
                    ):
                        label[ny, nx] = current
                        queue.append((ny, nx))
            if count > best[0]:
                best = (
                    count,
                    (min(xs), min(ys), max(xs), max(ys)),
                    current,
                )
    return label, best


def cut(cell: np.ndarray) -> np.ndarray:
    """Key the light background out of one cell and return RGBA cropped to the sprite."""
    low = cell.min(axis=2)
    high = cell.max(axis=2)
    light = (low > 188) & ((high - low) < 24)
    label, (_count, bbox, ident) = _components(~light)
    if bbox is None:
        raise SystemExit("no sprite found in a cell")
    x0, y0, x1, y1 = bbox
    mask = label[y0 : y1 + 1, x0 : x1 + 1] == ident

    # Fill holes: light regions enclosed by the sprite (shirt stripes, eye whites).
    height, width = mask.shape
    outside = ~mask
    seen = np.zeros_like(outside)
    queue: deque[tuple[int, int]] = deque()
    for x in range(width):
        for y in (0, height - 1):
            if outside[y, x] and not seen[y, x]:
                seen[y, x] = True
                queue.append((y, x))
    for y in range(height):
        for x in (0, width - 1):
            if outside[y, x] and not seen[y, x]:
                seen[y, x] = True
                queue.append((y, x))
    while queue:
        y, x = queue.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if (
                0 <= ny < height
                and 0 <= nx < width
                and outside[ny, nx]
                and not seen[ny, nx]
            ):
                seen[ny, nx] = True
                queue.append((ny, nx))
    holes = outside & ~seen
    mask = mask | holes

    # The source has no alpha, so the anti-aliased rim blends into the light checker and
    # survives as a pale halo. One 4-neighbour erosion takes that rim off the silhouette.
    padded = np.pad(mask, 1)
    mask = (
        padded[1:-1, 1:-1]
        & padded[:-2, 1:-1]
        & padded[2:, 1:-1]
        & padded[1:-1, :-2]
        & padded[1:-1, 2:]
    )

    rgba = np.zeros((height, width, 4), np.uint8)
    rgba[:, :, :3] = cell[y0 : y1 + 1, x0 : x1 + 1]
    rgba[:, :, 3] = np.where(mask, 255, 0)
    return rgba


def pad(frames: list[np.ndarray]) -> list[np.ndarray]:
    """Pad frames to one size, feet on the bottom edge and centred."""
    height = max(f.shape[0] for f in frames) + 2
    width = max(f.shape[1] for f in frames) + 4
    out = []
    for frame in frames:
        canvas = np.zeros((height, width, 4), np.uint8)
        h, w, _ = frame.shape
        x = (width - w) // 2
        canvas[height - h - 1 : height - 1, x : x + w] = frame
        out.append(canvas)
    return out


def pirate_frames(sheet: np.ndarray) -> list[np.ndarray]:
    """Idle, talking and pointing from the pirate sheet's first row."""
    rows, cols = 6, 6
    height, width, _ = sheet.shape
    ch, cw = height / rows, width / cols
    frames = []
    for col in (0, 2, 4):
        y0, x0 = 0, int(col * cw)
        frames.append(cut(sheet[y0 : int(ch), x0 : int((col + 1) * cw)]))
    return pad(frames)


def boy_frames(sheet: np.ndarray) -> list[np.ndarray]:
    """Idle, talking and pointing from the boy sheet's second row."""
    boxes = [(90, 252, 199, 481), (342, 252, 465, 482), (589, 254, 784, 485)]
    frames = []
    for x0, y0, x1, y1 in boxes:
        frames.append(cut(sheet[y0 : y1 + 1, x0 : x1 + 1]))
    return pad(frames)


def main() -> int:
    """Slice both sheets and write the two strips."""
    pirate = pirate_frames(decode(ROOT / "p2.png"))
    boy = boy_frames(decode(ROOT / "p1.png"))
    encode(OUT / "pirate.png", pirate)
    encode(OUT / "boy.png", boy)
    print(f"pirate {pirate[0].shape[1]}x{pirate[0].shape[0]} x{len(pirate)}")
    print(f"boy    {boy[0].shape[1]}x{boy[0].shape[0]} x{len(boy)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
