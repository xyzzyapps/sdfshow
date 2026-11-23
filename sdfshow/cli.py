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
