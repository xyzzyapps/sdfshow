# sdfshow

**Signed-distance-field shows rendered from Markdown.**

A show is a folder of two Markdown files. One carries the clock (`bpm`, `bars`,
`fps`), the camera and the arrangement; the other instantiates SDF templates and
animation tracks. `compile` turns them into a single GLSL raymarcher. VapourSynth
shades every frame with it; ffmpeg only encodes the frames.

There is no scene graph editor and no keyframe timeline. There is a clock, a text
file, and a shader you can read.

---

## Requirements

- Python 3.10+
- VapourSynth (R82 tested) with the `vs-placebo` plugin
- a Vulkan GPU (libplacebo)
- ffmpeg 9+ with the `yuv4mpegpipe` demuxer

One-time setup on Windows:

```powershell
python -m venv .venv
.venv\Scripts\pip install -e .
.venv\Scripts\python -m vapoursynth config
```

`vapoursynth config` writes the interpreter path VapourSynth needs; `vspipe`
fails without it. Development extras (pytest, ruff, black):
`.venv\Scripts\pip install -e ".[dev]"`.

## Quick start

```powershell
.venv\Scripts\python -m sdfshow compile --show first
.venv\Scripts\python -m sdfshow frame   --show first --at 5
.venv\Scripts\python -m sdfshow render  --show first
```

`shows/demo` is the demoscene set (ring tunnel, Menger sponge, gyroid, striped sun
and a column hall):

```powershell
.venv\Scripts\python -m sdfshow frame  --show demo --at 2
.venv\Scripts\python -m sdfshow render --show demo
```

- `compile` writes `gen/first/scene.glsl` and `gen/first/score.json`.
- `frame` renders one PNG (useful while tuning).
- `render` writes `output/first/show.mp4`; a second render writes `show_v2.mp4`,
  and so on. Existing renders are never overwritten.

`Taskfile.yml` wraps the same commands (`task compile`, `task frame at=5`,
`task render`).

---

## How a show works

```
shows/<name>/
  show.md        clock, stage, field order, arrangement, materials
  fields.md      globals, field instances (template + parameters), tracks
fields/          the SDF template library (GLSL function bodies)
gen/<name>/      generated scene.glsl + score.json (gitignored)
output/<name>/   renders and logs (gitignored)
```

The build is three steps, and each one is inspectable:

```
show.md + fields.md + fields/*.glsl
        |
        |  fields.py / tracks.py   text substitution, no defaults
        v
gen/<name>/scene.glsl             one libplacebo //!HOOK MAIN shader
        |
        |  render.py  ->  gen/<name>/render.vpy
        v
vspipe -c y4m  ->  ffmpeg (encode only)  ->  output/<name>/show.mp4
```

### The clock

`bpm`, `bars`, `fps` and `size` produce one timing truth:

| name | meaning |
|------|---------|
| `beat` | `60 / bpm` seconds |
| `bar` | four beats |
| `step` | a 16th note (`beat / 4`) |
| `dur` | `bars * bar` |
| `frames` | `dur * fps` |

Those durations are available in every template as `{{beat}}`, `{{bar}}`,
`{{step}}`, `{{dur}}`. Index arithmetic is written where it belongs:
`floor(t / {{bar}})`. The shader's clock is `t = (frame + TIME0) / FPS`, so frame
*n* is always the same picture and a still is the exact frame the video contains.

### `show.md`

```markdown
bpm: 120
bars: 8
fps: 30
size: 960x540

## Stage
| key      | value   |
|----------|---------|
| distance | dolly   |
| yaw      | spin    |
| pitch    | -0.12   |
| fov      | 1.75    |
| target   | 0\|0.05\|0 |
| fog      | 0.075   |
| exposure | 1.35    |
| background | 0.015\|0.018\|0.028 |
| light    | 0.55\|0.8\|0.35 |

## Fields
| field |
|-------|
| core  |
| ring  |
| floor |

## Materials
| field | color | pattern | scale |
|-------|-------|---------|-------|
| core  | 1.0\|0.42\|0.16 | stripes | 3.0 |

## Sections
| bars | core | ring  | floor |
|------|------|-------|-------|
| 0-2  | u    | x     | u     |
| 2-4  | u    | u0.30 | u     |
| 4-8  | u    | u0.18 | u0.4  |
```

- **Stage** values are numbers, track names, or arithmetic over tracks
  (`0.12*t`, `0.55*pulse` gives you a camera move driven by the music).
- **Fields** is the composition order; the first field of a section is its base.
- **Materials** is optional. `pattern` is `none`, `checker`, `grid` or `stripes`;
  `scale` sets its frequency. A field with no row gets a deterministic golden-angle
  colour.
- **Sections** rows are bar ranges and must cover `0..bars` with no gap.

The Stage table also carries the screen-space pass:

| key | meaning | default |
|-----|---------|---------|
| `scanlines` | darken alternate pixel rows | `0` |
| `plasma` | add a slow screen-space colour wash | `0` |
| `grain` | per-pixel noise | `0.012` |
| `vignette` | radial darkening | `0.22` |
| `hue` | rotate every material colour around grey (colour cycling) | `0` |

### Composition cells

A distance field does not mix by addition the way audio does, so a section cell is
an operator, not a gain:

| cell | meaning |
|------|---------|
| `u` | union (`min`) |
| `u0.3` | smooth union, blend radius `0.3` |
| `s0.2` | smooth subtraction |
| `i0.1` | smooth intersection |
| `x` | absent |

Row order is semantic: cells are applied left to right, and the first *active*
cell in a row must be a union (there is nothing to subtract from otherwise - the
build rejects it).

### `fields.md`

```markdown
## Fields
| name  | template        | parameters |
|-------|-----------------|------------|
| core  | sphere.glsl     | radius=0.62*pulse, cx=0, cy=0.10*sin(t*0.7), cz=0 |
| ring  | torus.glsl      | radius=ring_radius, thickness=0.055, spin=0.35, tilt=tilt |
| floor | plane_wave.glsl | amp=wave_amp, freq=2.1, speed=1.2, level=-1.05, shrink=0.55 |

## Tracks
| name        | kind  | values                                     | options     |
|-------------|-------|--------------------------------------------|-------------|
| pulse       | steps | 1.05\|0.92\|0.86\|0.92                      | ease=smooth |
| dolly       | keys  | 0:4.8\|3:4.1\|7:4.5                        | ease=smooth |
| spin        | expr  | 0.45+0.12*t                                |             |
| ring_radius | bars  | 1.15\|1.35\|1.25\|1.15\|1.3\|1.5\|1.4\|1.25 | ease=smooth |
```

There are **no defaults**. A template hole with no value fails the build and names
the field and the key. An identifier in a parameter that is neither a track nor a
whitelisted GLSL function also fails, by name.

### Tracks

A track is a named scalar function of time, compiled to GLSL.

| kind | shape | behaviour |
|------|-------|-----------|
| `steps` | `1\|0.5\|0.2` | one value per 16th step, repeating; `span=<bars>` (default 1) |
| `bars` | `0\|0.5\|1` | one value per bar, interpolated and looping |
| `keys` | `0:4.8\|3:4.1\|7:4.5` | explicit bar:value points, clamped outside, piecewise interpolated |
| `expr` | `0.45+0.12*t` | raw GLSL over `t` |

`ease=smooth` smooths interpolation. A parameter may use a track directly
(`radius=ring_radius`) or inside arithmetic (`radius=0.62*pulse`).

### Field templates

A template in `fields/` is the **body** of `float field_<name>(vec3 p, float t)`.
It must return a distance. Available helpers: `rotX`, `rotY`, `rotZ`, `rot2`,
`smin`, `smax`, `hash11`, `hash21`, and the clock defines. See
`fields/README.md`.

Templates may span several indented lines. Blank lines, lines starting with `#`,
and `//` comments are removed before the lines are joined.

### Demoscene kit

The shipped library already covers the useful demo pieces:

| template | what it makes | notes |
|----------|---------------|-------|
| `tunnel.glsl` | repeating ring tunnel along Z | two nearest rings are evaluated, so the distance stays a valid bound |
| `menger.glsl` | Menger sponge | three fold iterations, spins in place |
| `gyroid.glsl` | gyroid shell clipped to a sphere | `shrink` keeps the approximate distance safe |
| `pillars.glsl` | a ring of `count` columns | polar repetition, no column at the centre |
| `plane_wave.glsl` | wavy plane; with `amp=0` a flat floor | pair with `pattern=checker` or `grid` |
| `sphere.glsl` | sphere | pair with `pattern=stripes` for a synthwave sun |

`shows/demo` uses all of them across four bar-clocked scenes. The screen pass adds
scanlines, plasma, hue cycling and grain, so the CRT feel comes from the Stage
table, not from ffmpeg.

## Commands

| Command | What it does | Writes |
|---------|--------------|--------|
| `compile --show S` | Markdown -> shader | `gen/S/scene.glsl`, `gen/S/score.json` |
| `frame --show S [--at SEC] [--out PNG]` | one still | `output/S/frame_NNNNN.png` |
| `render --show S [--from SEC] [--to SEC] [--out MP4]` | encode the show | `output/S/show.mp4` |
| `shows` | list the shows | |

`--out` accepts a path. `--from` and `--to` are half-open: `--to 5` ends at frame
150 on a 30 fps show, so the clip is exactly five seconds. A build lock
(`output/S/logs/.build.lock`) stops two builds from writing the same show at once.

## Determinism

- The shader is a pure function of the Markdown: compiling twice gives the same
  bytes.
- Time comes only from the frame index, never from wall-clock or accumulated state.
  Frame *n* is reproducible, and `--from`/`--to` renders line up with the full one.
- x264 is run with `-threads 1`, so two renders of the same show on the same machine
  produce **byte-identical MP4s** (verified by hash).
- GPU float behaviour is not bit-identical across vendors. Within one machine and
  driver a render is stable; across machines, compare with a tolerance.
- Noise is seeded from the frame index and the pixel position, not from
  uninitialised state.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Failed to initialize VSScript` | run `.venv\Scripts\python -m vapoursynth config` |
| `placebo.Shader: Input should be YUVxxxP16` | the generated script already uses `YUV444P16`; do not edit it |
| a shader compile error names a line | read `gen/S/scene.glsl` at that line; the prelude shifts line numbers by about 80 |
| `unknown identifier 'puls'` | fix the parameter, or add the track |
| `field 'x' needs value 'y'` | add the parameter, or add a default to the template (there are none) |
| the ring/square is missing | check the `Sections` cell; a visual is only present when its row is active |
| a frame is empty background | the camera starts inside a solid (a floor, a column); raise the camera or move the geometry |
| `another sdfshow build is running` | wait, or delete the stale lock file |

## Project layout

```
sdfshow/        the Python package (parser, clock, codegen, renderer, CLI)
fields/         GLSL SDF template library
shows/first/    the worked example (8 bars, 120 BPM)
shows/demo/     the demoscene set (tunnel, Menger, gyroid, sun and columns)
shows/ring/     a one-field probe
tests/          pytest suite (clock, markdown, tracks, fields, arrangement)
gen/            generated shaders and scores (gitignored)
output/         renders, stills and logs (gitignored)
SPEC.md         the SRS: architecture, control surfaces, acceptance checks
TODO.md         open work
```

## Lineage

The project is shaped like `fftechno` (songs as Markdown folders, templates with
`{{placeholders}}`, no defaults, versioned renders), but it shares no code and no
dependency with it. Where audio mixes by addition, an SDF composes by
`min`/`max`, so the arrangement became an operator table and the instruments became
GLSL function bodies. Prior art in the same space: Shader Park, ISF, glslViewer,
Hydra, Punctual, sdfx/sdfray, and the `libplacebo` hook system itself.