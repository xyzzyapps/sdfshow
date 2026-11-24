"""Compile a show into a shader, and render it with VapourSynth.

The split is deliberate: VapourSynth shades every frame with the generated
libplacebo hook, and ffmpeg only encodes the frames it receives (plus the optional
audio track). No ffmpeg filter ever touches the picture.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

from . import config as C
from . import dialog, glsl
from . import fields as fields_mod
from .show import Show


def compile_show(show: Show) -> Path:
    """Generate ``gen/<show>/scene.glsl`` and ``gen/<show>/score.json``."""
    # Bubbles are structural per speaker, so their templates are generated first and
    # land in fields/ next to the hand-written ones. They are disposable.
    from . import dialog

    dialog.emit_bubble_templates(show, show.gen, C.FIELDS)
    fields = fields_mod.load(
        show.fields_md,
        show.clock,
        show.show_md.read_text(encoding="utf-8"),
        gen_dir=show.gen,
    )
    defined = {f.name for f in fields.fields}
    wanted = set(show.fields_order)
    if defined != wanted:
        missing = sorted(wanted - defined)
        extra = sorted(defined - wanted)
        detail = []
        if missing:
            detail.append("missing from fields.md: " + ", ".join(missing))
        if extra:
            detail.append("not in show.md's Fields table: " + ", ".join(extra))
        raise SystemExit("fields.md: " + "; ".join(detail))

    text = glsl.assemble(show, fields)
    show.gen.mkdir(parents=True, exist_ok=True)
    show.scene.write_text(text, encoding="utf-8")
    if show.effects:
        for index, name in enumerate(show.effects, start=1):
            effect = glsl.assemble_effect(
                name, show.effect_params.get(name, {}), show.clock, fields.tracks
            )
            (show.gen / f"fx_{index}_{name}.glsl").write_text(effect, encoding="utf-8")

    score = {
        "show": show.name,
        "bpm": show.clock.bpm,
        "bars": show.clock.bars,
        "fps": show.clock.fps,
        "size": [show.clock.width, show.clock.height],
        "frames": show.clock.frames,
        "duration": show.clock.duration,
        "fields": show.fields_order,
        "effects": show.effects,
        "sections": [
            {
                "bars": [section.lo, section.hi],
                "cells": {
                    name: {"op": cell.op, "k": cell.k}
                    for name, cell in section.cells.items()
                },
            }
            for section in show.sections
        ],
    }
    (show.gen / "score.json").write_text(json.dumps(score, indent=1), encoding="utf-8")
    return show.scene


def write_script(
    show: Show,
    script: Path | None = None,
    time_offset: int = 0,
    bubbles: list[dict] | None = None,
    sprites: list[dict] | None = None,
) -> Path:
    """Write the VapourSynth script that shades the show.

    Pass 0 is the generated SDF shader; each effect adds one more
    ``core.placebo.Shader`` over the previous clip. Bubbles, if any, are then composited
    as 2D overlays from pre-rendered numpy masks, so text is never part of the
    raymarch. ``frame`` in a libplacebo hook counts output frames from zero, not source
    frame indices, so a render starting at frame *N* bakes ``TIME0 = N`` into every pass.
    """
    if not show.scene.exists():
        raise SystemExit(f"{show.scene} is missing; run compile first")
    script = script or show.script
    clock = show.clock
    passes = [show.scene]
    for index, name in enumerate(show.effects, start=1):
        path = show.gen / f"fx_{index}_{name}.glsl"
        if not path.exists():
            raise SystemExit(f"{path} is missing; run compile first")
        passes.append(path)
    scene_list = ", ".join(f'r"{p.as_posix()}"' for p in passes)
    plans = bubbles or []
    sprite_plans = sprites or []
    sprite_text = (
        "[\n"
        + "".join(
            "    {{'id': '{id}', 'first': {first}, 'last': {last}, 'cycle': {cycle}, "
            "'rgb': r'{rgb}', 'a': r'{a}', 'alt_rgb': r'{alt_rgb}', "
            "'alt_a': r'{alt_a}'}},\n".format(
                id=item["id"],
                first=item["first"],
                last=item["last"],
                cycle=item["cycle"],
                rgb=item["rgb"].as_posix(),
                a=item["a"].as_posix(),
                alt_rgb=item["alt_rgb"].as_posix() if item["alt_rgb"].name else "",
                alt_a=item["alt_a"].as_posix() if item["alt_a"].name else "",
            )
            for item in sprite_plans
        )
        + "]"
    )
    plan_text = (
        "[\n"
        + "".join(
            "    {{'x': {x}, 'y': {y}, 'w': {w}, 'h': {h}, 'first': {first}, "
            "'last': {last}, 'style': '{style}', "
            "'panel': r'{panel}', 'ink': r'{ink}'}},\n".format(
                x=item["x"],
                y=item["y"],
                w=item["w"],
                h=item["h"],
                first=item["first"],
                last=item["last"],
                style=item["style"],
                panel=item["panel"].as_posix(),
                ink=item["ink"].as_posix(),
            )
            for item in plans
        )
        + "]"
    )
    text = f'''"""Generated by sdfshow. Do not edit."""

import numpy as np
import vapoursynth as vs

core = vs.core
W, H, FPS, NF = {clock.width}, {clock.height}, {clock.fps}, {clock.frames}
PASSES = [{scene_list}]
BUBBLES = {plan_text}
SPRITES = {sprite_text}

def shade(clip, path):
    """Run one generated libplacebo pass over *clip*."""
    with open(path, encoding="utf-8") as fh:
        src = fh.read().replace("// @TIME0@", "#define TIME0 {time_offset}")
    return core.placebo.Shader(
        clip,
        shader_s=src,
        width=W,
        height=H,
        sigmoidize=False,
        linearize=False,
        matrix=5,
    )

def put(n, f, array):
    """Copy one full-frame float array into an RGBS frame."""
    out = f.copy()
    for plane in range(3):
        np.copyto(np.asarray(out[plane]), array[..., plane].astype(np.float32))
    return out

def put_mask(n, f, array):
    """Copy one full-frame float array into a GRAYS frame."""
    out = f.copy()
    np.copyto(np.asarray(out[0]), array.astype(np.float32))
    return out

clip = core.std.BlankClip(
    width=W, height=H, format=vs.YUV444P16, length=NF, fpsnum=FPS, fpsden=1
)
for path in PASSES:
    clip = shade(clip, path)

# Text is composited here, after the SDF passes, so it is never sampled by a raymarch.
# std.MaskedMerge is the compositing primitive in this build (there is no Overlay):
# it takes an RGB clip, a second RGB clip and a per-pixel mask, and returns RGB.
clip = core.resize.Bicubic(
    clip, width=W, height=H, format=vs.RGBS,
    matrix_in_s="470bg", range_in_s="limited",
)

# Sprites are composited after the SDF passes, in table order, before the captions.
def pick(items, n):
    """The last sprite row whose window contains frame *n*."""
    chosen = None
    for item in items:
        if item["first"] <= n < item["last"]:
            chosen = item
    return chosen

def chose(item, n, key):
    """Flip between the main and alternate plate every ``cycle`` frames."""
    if item["cycle"] and ((n - item["first"]) // item["cycle"]) % 2 == 1:
        return item["alt_" + key]
    return item[key]

def make_rgb(items):
    """A callback that paints the chosen plate, or nothing."""
    def apply(n, f):
        item = pick(items, n)
        if item is None:
            return put(n, f, np.zeros((H, W, 3), np.float32))
        return put(n, f, chose(item, n, "rgb_arr"))
    return apply

def make_alpha(items):
    """A callback that paints the chosen alpha plate, or nothing."""
    def apply(n, f):
        item = pick(items, n)
        if item is None:
            return put_mask(n, f, np.zeros((H, W), np.float32))
        return put_mask(n, f, chose(item, n, "a_arr"))
    return apply

_GROUPS = []
for _item in SPRITES:
    if not _GROUPS or _GROUPS[-1][0] != _item["id"]:
        _GROUPS.append((_item["id"], []))
    _GROUPS[-1][1].append(_item)
for _sid, _items in _GROUPS:
    for _it in _items:
        _it["rgb_arr"] = np.load(_it["rgb"])
        _it["a_arr"] = np.load(_it["a"])
        if _it["cycle"]:
            _it["alt_rgb_arr"] = np.load(_it["alt_rgb"])
            _it["alt_a_arr"] = np.load(_it["alt_a"])
    _sprite_rgb = core.std.BlankClip(
        width=W, height=H, format=vs.RGBS, length=NF, fpsnum=FPS, fpsden=1,
        color=[0.0, 0.0, 0.0],
    )
    _sprite_rgb = core.std.ModifyFrame(_sprite_rgb, _sprite_rgb, make_rgb(_items))
    _sprite_a = core.std.BlankClip(
        width=W, height=H, format=vs.GRAYS, length=NF, fpsnum=FPS, fpsden=1, color=[0.0],
    )
    _sprite_a = core.std.ModifyFrame(_sprite_a, _sprite_a, make_alpha(_items))
    clip = core.std.MaskedMerge(clip, _sprite_rgb, _sprite_a)

for item in BUBBLES:
    panel = np.load(item["panel"])
    ink = np.load(item["ink"])
    if item["style"] == "caption":
        # SCUMM caption: white ink over a black outline, no panel.
        rgb = 0.02 + 0.96 * ink[..., None]
    else:
        rgb = panel[..., None] * (0.97 - 0.90 * ink[..., None])
    h, w = panel.shape
    color = np.zeros((H, W, 3), np.float32)
    color[item["y"]:item["y"] + h, item["x"]:item["x"] + w] = rgb
    alpha = np.zeros((H, W), np.float32)
    alpha[item["y"]:item["y"] + h, item["x"]:item["x"] + w] = panel

    color_clip = core.std.BlankClip(
        width=W, height=H, format=vs.RGBS, length=NF, fpsnum=FPS, fpsden=1,
        color=[0.0, 0.0, 0.0],
    )
    color_clip = core.std.ModifyFrame(
        color_clip, color_clip, lambda n, f, c=color: put(n, f, c)
    )
    alpha_clip = core.std.BlankClip(
        width=W, height=H, format=vs.GRAYS, length=NF, fpsnum=FPS, fpsden=1,
        color=[0.0],
    )
    # One mask per frame: the bubble's own coverage inside its bar window, zero outside.
    def make_alpha(lo, hi, a):
        """Build a callback with the values bound now, not when the loop moves on."""
        def apply_alpha(n, f):
            return put_mask(n, f, a if lo <= n < hi else np.zeros_like(a))
        return apply_alpha

    alpha_clip = core.std.ModifyFrame(
        alpha_clip, alpha_clip, make_alpha(item["first"], item["last"], alpha)
    )
    clip = core.std.MaskedMerge(clip, color_clip, alpha_clip)

clip = core.resize.Bicubic(
    clip,
    format=vs.YUV420P8,
    matrix_s="470bg",
    range_s="limited",
)
clip.set_output()
'''
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(text, encoding="utf-8")
    return script


def _encode(
    show: Show,
    script: Path,
    out: Path,
    *,
    start: int,
    end: int,
    time_offset: int,
    audio: Path | None,
    still: bool,
) -> Path:
    """Run vspipe -> ffmpeg, writing *out* (a PNG when *still*)."""
    show.logs.mkdir(parents=True, exist_ok=True)
    vsp_cmd = [
        str(C.VSPIPE),
        "-c",
        "y4m",
        # One frame request in flight. With the default parallel requests, the
        # first one or two frames of a run can differ from a repeat run (a GPU
        # dispatch ordering effect), which breaks byte-identical renders. The
        # cost is negligible next to the raymarch.
        "-r",
        "1",
        "-s",
        str(start),
        "-e",
        str(end),
        str(script),
        "-",
    ]
    ff_cmd = ["ffmpeg", "-hide_banner", "-y", "-v", "error", "-f", "yuv4mpegpipe"]
    ff_cmd += ["-i", "-"]
    if audio is not None:
        ff_cmd += ["-i", str(audio)]
    if still:
        ff_cmd += ["-frames:v", "1", "-update", "1", str(out)]
    else:
        ff_cmd += [
            "-c:v",
            "libx264",
            "-preset",
            C.VIDEO_PRESET,
            "-crf",
            str(C.VIDEO_CRF),
            "-pix_fmt",
            C.VIDEO_PIX_FMT,
            # Deterministic encoded bytes: x264's threaded rate control can
            # otherwise pick different decisions on identical input.
            "-threads",
            "1",
        ]
        if audio is not None:
            ff_cmd += ["-c:a", "aac", "-b:a", C.AUDIO_BITRATE, "-shortest"]
        ff_cmd += ["-movflags", "+faststart", str(out)]

    with (
        open(show.logs / "vspipe.log", "wb") as vlog,
        open(show.logs / "ffmpeg.log", "wb") as flog,
    ):
        vsp = subprocess.Popen(vsp_cmd, stdout=subprocess.PIPE, stderr=vlog)
        enc = subprocess.Popen(ff_cmd, stdin=vsp.stdout, stderr=flog)
        assert vsp.stdout is not None
        vsp.stdout.close()
        enc.wait()
        vsp.wait()
    if enc.returncode != 0:
        raise SystemExit(
            f"ffmpeg failed ({enc.returncode}); see {show.logs / 'ffmpeg.log'}"
        )
    if vsp.returncode != 0:
        raise SystemExit(
            f"vspipe failed ({vsp.returncode}); see {show.logs / 'vspipe.log'}"
        )
    return out


def _audio(show: Show) -> Path | None:
    """The show's audio track: a declared file, or synthesized dialogue.

    ``audio:`` names an existing file; ``## Dialogue`` synthesizes speech from the same
    table the bubbles read. A show can have either, and a declared file wins.
    """
    if show.audio:
        path = Path(show.audio)
        path = path if path.is_absolute() else C.ROOT / path
        if not path.exists():
            raise SystemExit(f"show.md: audio file not found: {path}")
        return path
    if getattr(show, "dialogue", None):
        from . import dialog

        track = dialog.synth(show)
        if track is not None:
            print(f"dialogue: {track}")
        return track
    return None


def _sheet(path: Path) -> np.ndarray:
    """Decode a sprite sheet to an ``(h, w, 4)`` uint8 array."""
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
            "rgba",
            "-",
        ],
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(raw, np.uint8).reshape(height, width, 4)


def _sprite_plans(show: Show) -> list[dict]:
    """Rasterise every sprite row into full-frame plates.

    Each row becomes an RGB plate and an alpha plate (``.npy`` under ``gen/<show>/sprites``).
    A row with ``cycle`` also gets an alternate plate, and the generated script flips
    between them every *cycle* frames - that is the lip flap and the walk-in. The last
    row whose window contains the frame wins.
    """
    if not show.sprites:
        return []
    out_dir = show.gen / "sprites"
    out_dir.mkdir(parents=True, exist_ok=True)
    width, height = show.clock.width, show.clock.height
    sheets: dict[Path, np.ndarray] = {}
    plans: list[dict] = []

    def plate(sprite, sheet, frame, index, tag):
        """Scale one cell to the placement and save its RGB and alpha plates."""
        cell_w, cell_h = sprite.cell
        columns = sheet.shape[1] // cell_w
        if frame >= columns:
            raise SystemExit(
                f"show.md: sprite '{sprite.id}' frame {frame} is past {columns} cells"
            )
        cell = sheet[:cell_h, frame * cell_w : (frame + 1) * cell_w]
        if sprite.flip:
            cell = cell[:, ::-1]
        target_h = max(1, round(sprite.height * height))
        scale = target_h / cell_h
        target_w = max(1, round(cell_w * scale))
        rows = np.minimum((np.arange(target_h) / scale).astype(int), cell_h - 1)
        cols = np.minimum((np.arange(target_w) / scale).astype(int), cell_w - 1)
        small = cell[rows][:, cols]
        left = round(width * 0.5 + sprite.x * height - target_w / 2)
        top = round((0.5 - sprite.y) * height) - target_h
        sy0, sy1 = max(0, top), min(height, top + target_h)
        sx0, sx1 = max(0, left), min(width, left + target_w)
        rgb = np.zeros((height, width, 3), np.float32)
        alpha = np.zeros((height, width), np.float32)
        if sy1 > sy0 and sx1 > sx0:
            patch = small[sy0 - top : sy1 - top, sx0 - left : sx1 - left]
            rgb[sy0:sy1, sx0:sx1] = patch[..., :3].astype(np.float32) / 255.0
            alpha[sy0:sy1, sx0:sx1] = patch[..., 3].astype(np.float32) / 255.0
        rgb_path = out_dir / f"{index:02d}_{tag}_rgb.npy"
        alpha_path = out_dir / f"{index:02d}_{tag}_a.npy"
        np.save(rgb_path, rgb)
        np.save(alpha_path, alpha)
        return rgb_path, alpha_path

    for index, sprite in enumerate(show.sprites):
        sheet = sheets.get(sprite.sheet)
        if sheet is None:
            sheet = _sheet(sprite.sheet)
            sheets[sprite.sheet] = sheet
        cell_w, cell_h = sprite.cell
        if sheet.shape[1] % cell_w or sheet.shape[0] < cell_h:
            raise SystemExit(
                f"show.md: sprite '{sprite.id}' sheet does not match cell {cell_w}x{cell_h}"
            )
        rgb_path, alpha_path = plate(sprite, sheet, sprite.frame, index, "a")
        alt_rgb = alt_a = Path()
        if sprite.cycle:
            alt_rgb, alt_a = plate(sprite, sheet, sprite.alt, index, "b")
        first = show.clock.frame_at(sprite.lo * show.clock.bar)
        plans.append(
            {
                "id": sprite.id,
                "first": first,
                "last": max(first + 1, show.clock.frame_at(sprite.hi * show.clock.bar)),
                "rgb": rgb_path,
                "a": alpha_path,
                "cycle": sprite.cycle,
                "alt_rgb": alt_rgb,
                "alt_a": alt_a,
            }
        )
    return plans


def render(
    show: Show,
    *,
    static: bool = False,
    at: float = 0.0,
    out: Path | None = None,
    start: float | None = None,
    end: float | None = None,
) -> Path:
    """Render a still, a range, or the whole show. Returns the path written."""
    if not C.VSPIPE.exists():
        raise SystemExit(f"vspipe not found at {C.VSPIPE} (create the venv first)")
    compile_show(show)
    audio = None if static else _audio(show)
    clock = show.clock
    # Bubbles are rasterised once, then composited by VapourSynth. Frame numbers are
    # absolute, so a range render shows the right lines.
    bubbles: list[dict] = []
    for index, item in enumerate(dialog.overlay_plan(show, show.gen)):
        bubbles.append(
            {
                **item,
                "first": clock.frame_at(item["from"]),
                "last": max(
                    clock.frame_at(item["from"]) + 1, clock.frame_at(item["to"])
                ),
                "panel": show.gen / "bubbles" / f"{index:02d}_panel.npy",
                "ink": show.gen / "bubbles" / f"{index:02d}_ink.npy",
            }
        )

    sprite_plans = _sprite_plans(show)

    if static:
        frame = show.clock.frame_at(at)
        script = write_script(
            show,
            show.gen / "still.vpy",
            time_offset=frame,
            bubbles=bubbles,
            sprites=sprite_plans,
        )
        target = out or C.unique_path(show.output / f"frame_{frame:05d}.png")
        target.parent.mkdir(parents=True, exist_ok=True)
        return _encode(
            show,
            script,
            target,
            start=frame,
            end=frame,
            time_offset=frame,
            audio=None,
            still=True,
        )

    first = show.clock.frame_at(start) if start is not None else 0
    last = show.clock.frame_limit(end) - 1 if end is not None else show.clock.frames - 1
    if last < first:
        raise SystemExit("render: --to is before --from")
    script = write_script(
        show, time_offset=first, bubbles=bubbles, sprites=sprite_plans
    )
    target = out or C.unique_path(show.video)
    target.parent.mkdir(parents=True, exist_ok=True)
    return _encode(
        show,
        script,
        target,
        start=first,
        end=last,
        time_offset=first,
        audio=audio,
        still=False,
    )
