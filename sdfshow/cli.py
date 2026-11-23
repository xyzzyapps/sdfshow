"""Command line entry point for sdfshow."""

from __future__ import annotations

import argparse
from pathlib import Path

from . import config
from . import render as render_mod
from . import show as shows
from .proc import build_lock


def _add_show(parser: argparse.ArgumentParser) -> None:
    """Add the shared ``--show`` option."""
    available = shows.names()
    default = (
        config.DEFAULT_SHOW
        if config.DEFAULT_SHOW in available
        else (available[0] if available else "")
    )
    parser.add_argument(
        "--show",
        default=default,
        help="which show under shows/ (default: %(default)s)",
    )


def _clips(show, seconds: float, lead: float, out: Path | None) -> None:
    """Render one short clip per section, skipping the cut-in ramp."""
    bar = show.clock.bar
    out_dir = out or (show.output / "clips")
    for index, section in enumerate(show.sections):
        span = section.hi * bar - section.lo * bar
        start = section.lo * bar + min(lead, 0.25 * span)
        end = min(start + seconds, section.hi * bar)
        if end - start < 0.5:
            continue
        target = config.unique_path(
            out_dir / f"scene_{index:02d}_bars_{section.lo}-{section.hi}.mp4"
        )
        path = render_mod.render(show, start=start, end=end, out=target)
        print(f"clip: {path}")


def main(argv: list[str] | None = None) -> None:
    """Parse the command line and run the selected command."""
    parser = argparse.ArgumentParser(
        prog="sdfshow",
        description="Render SDF shows from Markdown with VapourSynth.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    comp = sub.add_parser(
        "compile", help="generate gen/<show>/scene.glsl from the Markdown"
    )
    _add_show(comp)

    frame = sub.add_parser("frame", help="render one PNG for debugging")
    _add_show(frame)
    frame.add_argument(
        "--at", type=float, default=0.0, help="time in seconds (default: 0)"
    )
    frame.add_argument("--out", type=Path, default=None, help="output PNG path")

    rend = sub.add_parser("render", help="render the show to H.264 MP4")
    _add_show(rend)
    rend.add_argument(
        "--from", dest="start", type=float, default=None, help="start time (s)"
    )
    rend.add_argument("--to", dest="end", type=float, default=None, help="end time (s)")
    rend.add_argument("--out", type=Path, default=None, help="output MP4 path")

    clips = sub.add_parser("clips", help="render one short clip per section")
    _add_show(clips)
    clips.add_argument(
        "--seconds", type=float, default=5.0, help="clip length (default: 5)"
    )
    clips.add_argument(
        "--lead",
        type=float,
        default=0.8,
        help="seconds to skip after the section starts (default: 0.8)",
    )
    clips.add_argument("--out", type=Path, default=None, help="output directory")

    ls = sub.add_parser("shows", help="list the shows under shows/")
    ls.set_defaults(command="shows")

    args = parser.parse_args(argv)

    if args.command == "shows":
        for name in shows.names():
            print(name)
        return

    show = shows.load(args.show)
    with build_lock(show.lock):
        if args.command == "compile":
            path = render_mod.compile_show(show)
            print(f"scene: {path}")
        elif args.command == "frame":
            path = render_mod.render(show, static=True, at=args.at, out=args.out)
            print(f"frame: {path}")
        elif args.command == "render":
            path = render_mod.render(show, start=args.start, end=args.end, out=args.out)
            print(f"video: {path}")
        elif args.command == "clips":
            _clips(show, args.seconds, args.lead, args.out)
