"""sdfshow - signed-distance-field shows rendered from Markdown.

A show is a folder under ``shows/``: ``show.md`` carries the clock, the stage and
the arrangement; ``fields.md`` carries the field instances (templates + parameters)
and the animation tracks. The build renders ``gen/<show>/scene.glsl`` - a single
libplacebo/GLSL raymarcher - and VapourSynth shades every frame with it. ffmpeg only
encodes the resulting frames.
"""

from __future__ import annotations

__version__ = "0.1.0"
