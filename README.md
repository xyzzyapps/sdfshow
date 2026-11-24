# sdfshow

**Signed-distance-field shows rendered from Markdown.**

A show is a folder of two Markdown files. One carries the clock (`bpm`, `bars`,
`fps`), the stage and the arrangement; the other instantiates SDF templates and
animation tracks. `compile` turns them into a single GLSL shader. VapourSynth shades
every frame with it; ffmpeg only encodes the frames.

There are two renderers behind the same Markdown: a raymarched 3D scene, and a flat
flat 2D cutout scene where the `Fields` table is a z-stack of shapes (`mode: 2d`).
Speech bubbles are drawn from an SDF stroke font and composited by VapourSynth, with
optional synthesized dialogue.

There is no scene graph editor and no keyframe timeline. There is a clock, a text
file, and a shader you can read.

**New here?** Read [TUTORIAL.md](TUTORIAL.md) - it explains SDFs, VapourSynth and
the whole Markdown format from first principles. The formal contract is in
[SPEC.md](SPEC.md).

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
and a column hall). `shows/reel` is the long one: 30 seconds, five scenes, morphs,
an animated kaleido fold and a shifting effect chain.

The two animations are `shows/diner` (3D, the first one: two people in a booth and a
cut-track camera) and `shows/pixel` (flat 2D cutouts: a diner that cuts to a living
room, four characters, close-ups and spoken dialogue).

`shows/island` is a second 2D demo in the grammar of a 1990s adventure game: an SDF
night cliff, stone arch and campfire, with two raster sprite actors and the spoken line
as a caption at the top of the frame.

```powershell
.venv\Scripts\python -m sdfshow frame  --show demo --at 2
.venv\Scripts\python -m sdfshow render --show demo
.venv\Scripts\python -m sdfshow render --show reel
.venv\Scripts\python -m sdfshow render --show diner
.venv\Scripts\python -m sdfshow frame  --show pixel --at 4
.venv\Scripts\python -m sdfshow render --show pixel
.venv\Scripts\python -m sdfshow render --show island
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
  show.md        clock, stage, field order, arrangement, materials, dialogue
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

`bars` may be a number or `auto`. `auto` measures the `## Dialogue` table and ends the
show on the last line's final bar, so the animation stops when the talking does.

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

The Stage table also carries the screen-space pass and the space fold:

| key | meaning | default |
|-----|---------|---------|
| `scanlines` | darken alternate pixel rows | `0` |
| `plasma` | add a slow screen-space colour wash | `0` |
| `grain` | per-pixel noise | `0.012` |
| `vignette` | radial darkening | `0.22` |
| `hue` | rotate every material colour around grey (colour cycling) | `0` |
| `fold` | repeat space before every field: `none`, `mirror`, `kaleido` | `none` |
| `fold_count` | sectors for `fold: kaleido` | `6` |

In `mode: 2d` the camera keys are ignored and these apply instead:

| key | meaning | default |
|-----|---------|---------|
| `mode` | `3d` (raymarch) or `2d` (flat layers) | `3d` |
| `pixel` | snap the picture to a grid of `pixel` device pixels | `1` |
| `outline` | dark rim around every layer; `0` turns it off | `0` |
| `outline_color` | rim colour | `0.06\|0.05\|0.08` |
| `font` | bubble cap height as a fraction of frame height | `0.042` |
| `panel` | bubble padding as a multiple of the type size | `1.0` |
| `bubble` | speech presentation: `panel` or `caption` | `panel` |

`font` and `panel` are independent: small letters, comfortable panel. Both work in
3D shows too, since bubbles are an overlay.

### Effect passes

`## Effects` adds post passes. Each one is a generated libplacebo shader over the
previous pass, so nothing leaves GLSL and nothing is re-marched.

```markdown
## Effects
| effect | key       | value |
|--------|-----------|-------|
| bloom  | strength  | 0.7   |
| chroma | amount    | 0.05  |
| crt    | curvature | 0.12  |
| glitch | chance    | 0.05  |
```

| effect | knobs (default) | what it does |
|--------|-----------------|--------------|
| `bloom` | `threshold` 0.55, `strength` 0.8, `radius` 2.0 | bright-pass blur added back |
| `chroma` | `amount` 0.05 | radial red/blue split |
| `crt` | `curvature` 0.12 | barrel curvature, black outside |
| `glitch` | `amount` 0.06, `rate` 9.0, `chance` 0.08 | band-wise horizontal offsets |

Order is first appearance in the table. Every pass is seekable because `TIME0` is
injected into each one.

A knob may be a **track name** as well as a number, so the treatment can follow the
music: `| glitch | chance | glitch_amt |` with `glitch_amt` a `keys` track. The
track functions are emitted into the pass that needs them.

### Composition cells

A distance field does not mix by addition the way audio does, so a section cell is
an operator, not a gain:

| cell | meaning |
|------|---------|
| `u` | union (`min`) |
| `u0.3` | smooth union, blend radius `0.3` |
| `s0.2` | smooth subtraction |
| `i0.1` | smooth intersection |
| `m0.5` | morph: `mix` the accumulated field towards this one |
| `x` | absent |

The operand may be a **number or a track name**, so a blend radius or a morph
weight can be animated: `mwg` blends by `track_wg(t)`, clamped to 0..1.

`m` is a cross-fade between two distance values, and the average of two distances is
not a distance, so a morph looks right only when both fields occupy the same space
(concentric solids). Use it for a shape change in place, not for a scene change.

Row order is semantic: cells are applied left to right, and the first *active* cell
in a row must be a union (a morph has nothing to blend from otherwise - the build
rejects it).

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

A `## Tracks` table may live in **either** file. Put camera and effect tracks in
`show.md` next to the Stage table, and field tracks in `fields.md`; a name defined in
both is an error.

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

In `mode: 2d` the same template contract applies, but `p` is screen space and only
`p.xy` is meaningful; the `*2d.glsl` templates are written for that.

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
| `cylinder.glsl` | capped cylinder along Y | exact |
| `cone.glsl` | capped cone, `r1` to `r2` | exact |
| `hexprism.glsl` | hexagonal prism along Z | exact |
| `helix.glsl` | helical tube | approximate; `shrink` < 1 |
| `terrain.glsl` | noise ground plane (`fbm`) | approximate; `shrink` < 1 |
| `mandelbulb.glsl` | mandelbulb distance estimate | expensive: six iterations per sample |
| `box.glsl` | rounded box | exact |
| `capsule.glsl` | capsule between two points | exact |
| `torus.glsl` | torus, spin and tilt | exact |

The prelude also provides `vnoise`, `fbm`, `hash13`, `smin`, `smax`, `rot2`/`rotX`/
`rotY`/`rotZ`, `apply_pattern` and `hue_rotate`, so a new template can be a few
lines long.

`shows/demo` uses all of them across four bar-clocked scenes. The screen pass adds
scanlines, plasma, hue cycling and grain, so the CRT feel comes from the Stage
table, not from ffmpeg.

## 2D mode

`mode: 2d` swaps the renderer for the same Markdown. There is no march, no shading and
no 3D camera: every field is a flat shape evaluated in **screen space**, and the frame
is painted back-to-front. The `Fields` table becomes a z-stack, exactly like the
document order of an SVG:

```
col = background
for each layer, in Fields order:
    if the current section draws it:
        d = layer(p)
        if d < -outline:  col = colour        # inside
        elif d < 0:       col = mix(outline, colour)
```

Screen space is the frame offset divided by frame height: `y = 0` is the centre,
`-0.5` the bottom and `0.5` the top; `x` runs about `-0.89..0.89` at 16:9. A 2D
template returns a distance in those units, so `ellipse2d` with `ry=0.1` is a shape a
fifth of the frame tall.

The shipped 2D templates:

| template | what it makes |
|----------|---------------|
| `ellipse2d.glsl` | ellipse (`rx`, `ry`) |
| `box2d.glsl` | rounded box (`hx`, `hy`, `round`) |
| `capsule2d.glsl` | capsule |
| `head2d.glsl` | one big oval skull (`wide`) |
| `neck2d.glsl` | a short neck, drawn behind the shirt (`shoulders`) |
| `body2d.glsl` | the shirt: one rounded block (`shoulders`) |
| `arms2d.glsl` | two arms with round hands, mirrored (`shoulders`) |
| `legs2d.glsl` | two trouser legs, mirrored |
| `hair2d.glsl` | one of four hair silhouettes (`style`, `fringe`) |
| `face2d.glsl` | sclera, brows, mouth or pupils as separate layers (`kind`) |
| `seat2d.glsl` | a booth bench (`hw`, `hh`) |
| `table2d.glsl` | a table top (`hw`) |
| `sofa2d.glsl` | sofa: seat, short back, arms (`hw`, `back`) |
| `lamp2d.glsl` | floor lamp: shade, stand, base (`glow`) |
| `window2d.glsl` | pane plus frame |
| `stars2d.glsl` | a hash-grid star field (`size`) |
| `arch2d.glsl` | a stone arch: pillars and a ring (`hw`, `thick`, `drop`) |
| `fire2d.glsl` | a wobbling flame (`wide`, `tall`, `speed`) |

```markdown
## Stage
| key     | value            |
|---------|------------------|
| mode    | 2d               |
| pixel   | 1                |
| outline | 0.005            |
| zoom    | zoom             |
| focus_x | focus_x          |
| focus_y | focus_y          |
| font    | 0.020            |
| panel   | 2.60             |
```

Three consequences worth knowing before writing a 2D show:

- **A layer is one flat fill.** A figure cannot be one shape with painted features, so
  it is ten rows - trousers, neck, shirt, arms and hands, head, hair, white sclera,
  pupils, mouth - each with its own colour. The whole cast shares one paper-white skin; shirts,
  hair and trousers carry the difference. Furniture splits the same way (a window is a
  pane plus a frame).
- **Cells are visibility, not operators.** `x` means the layer is absent; `u` and `u<k>`
  both mean "draw it"; `m<w>` is a fade gate at `w > 0.5`. min/max of two flat fills
  has no meaning.
- **Table order is depth.** There is no per-pixel depth test, so a character behind a
  table must be listed before it.

`Sections` is how a 2D show changes **setting**, not just cast: both sets of furniture
live in the `Fields` table and only the active section draws its set. `shows/pixel`
does this with a diner (bars 0-8) and a living room (8-20):

```markdown
| bars  | sky | floor_diner | booth | table | cup | wall_house | sofa | ... |
|-------|-----|-------------|-------|-------|-----|------------|------|-----|
| 0-4   | u   | u           | u     | u     | u   | x          | x    | ... |
| 4-8   | u   | u           | u     | u     | u   | x          | x    | ... |
| 8-14  | x   | x           | x     | x     | x   | u          | u    | ... |
| 14-20 | x   | x           | x     | x     | x   | u          | u    | ... |
```

### Cuts and close-ups

There is no 3D camera in this mode, but the picture can still be pushed in. `zoom`
magnifies around a focus point given by `focus_x`/`focus_y` in screen units; all
three may be `cuts` tracks, so a shot change lands on a bar boundary:

```markdown
| name    | kind | values |
|---------|------|--------|
| zoom    | cuts | 0:1.0\|1:2.3\|3:1.0\|5:2.1 |
| focus_x | cuts | 0:0.0\|1:-0.44\|3:0.0\|5:0.58 |
| focus_y | cuts | 0:-0.12\|1:-0.08\|3:-0.12 |
```

`shows/pixel` cuts wide, close, close, wide on the speaker's bar. The outline is
divided back out by the zoom, so the rim keeps a constant width on screen.

`pixel` quantises the whole frame to a device grid before any layer is evaluated -
the old pixel-art look, off (`1`) in this show. `outline` rims every layer and is
antialiased with a `smoothstep`. Both may be tracks.

The 3D sibling is `shows/diner`: the same `## Dialogue` format and the same booth, but
raymarched, with a `cuts` track driving the camera.

## Dialogue

An optional `## Dialogue` table drives the bubbles and the audio from one source:

```markdown
## Dialogue
| speaker | bars | text                          | voice |
|---------|------|-------------------------------|-------|
| AINA    | 1-2  | So we are just going to sit here? | slt |
| BORIS   | 2-3  | That was the plan.            | rms   |
```

- `speaker` names a field in `fields.md`; the bubble is seated above that field's `cx`,
  and its tail points at them.
- `text` becomes a rounded panel plus a tail, rasterised as SDF coverage masks by
  `sdfshow/textmask.py` at compile time.
- `voice` is an ffmpeg `flite` voice; each line is synthesized at its bar and mixed
  into the show's audio track. A stock flite build has one female voice (`slt`),
  so `voice` also accepts a pitch factor: `slt*0.92` is the same speaker, pitched
  down with rubberband so two women in one show do not sound identical.

Set `bubble: caption` in the Stage table for SCUMM-style captions: white type with a
dark outline, centred at the top of the frame, no panel and no tail.

The masks are composited by VapourSynth after the SDF passes (`std.MaskedMerge`, one
per line, over the line's frame window), so text is never part of the shader. Type
size and panel size are separate stage keys: `font` is the cap height as a fraction of
frame height, `panel` pads the bubble relative to the type. Lines longer than 48
characters fail the build rather than shrink below legibility.

## Sprites

Backgrounds stay SDF; actors can be raster sprites, which is how an adventure scene was
actually built. A sheet is a PNG strip of equally sized RGBA frames, and a `## Sprites`
table places them:

```markdown
## Sprites
| id | sheet | cell | bars | frame | x | y | height | flip | cycle | alt |
|----|-------|------|------|-------|-----|-----|--------|------|-------|-----|
| pirate | assets/sprites/pirate.png | 126x88 | 0-11 | 0 | -0.50 | -0.295 | 0.34 | 0 | 0 | 0 |
| pirate | assets/sprites/pirate.png | 126x88 | 4.4-6 | 1 | -0.50 | -0.295 | 0.34 | 0 | 4 | 0 |
| boy | assets/sprites/boy.png | 200x234 | 1-3 | 1 | 0.40 | -0.295 | 0.38 | 1 | 4 | 0 |
```

- `cell` is one frame in the sheet; `frame` counts cells left to right.
- `x`/`y` is the feet anchor in screen units; `height` is the sprite height.
- Rows for one id may repeat over bar windows. Later rows win inside their window, so an
  idle row for the whole show plus a talking row over a line is enough. Bar ranges may be
  fractional (`4.4-6`).
- `cycle` and `alt` flip between the row's frame and frame `alt` every `cycle` frames:
  the lip flap, the walk-in and the laugh. `cycle 0` is static.
- `flip 1` mirrors the sprite in place, which is how the boy faces the pirate.
- Sheets are composited after the SDF passes and before the captions, in table order.
- The camera is static for sprites in this version: `zoom`/`focus_*` move the SDF
  background but not the actors.

The source sheets here had no alpha (a baked checkerboard, a card border and labels), so
`tools/prep_sprites.py` keys the light background, keeps the largest component, refills
its enclosed light regions and erodes the anti-aliased rim. It writes
`assets/sprites/{boy,pirate}.png`; run it with `.venv\Scripts\python -m tools.prep_sprites`.

## Commands

| Command | What it does | Writes |
|---------|--------------|--------|
| `compile --show S` | Markdown -> shader | `gen/S/scene.glsl`, `gen/S/score.json` |
| `frame --show S [--at SEC] [--out PNG]` | one still | `output/S/frame_NNNNN.png` |
| `render --show S [--from SEC] [--to SEC] [--out MP4]` | encode the show | `output/S/show.mp4` |
| `clips --show S [--seconds N] [--lead SEC]` | one short clip per section | `output/S/clips/scene_NN_bars_A-B.mp4` |
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
- `vspipe` is run with `-r 1` (one frame request in flight). With the default
  parallel requests, the first frame or two of a run can differ from a repeat run,
  and every downstream frame inherits the difference through H.264. Serialising
  requests removes it; the cost is negligible next to the raymarch.
- GPU float behaviour is not bit-identical across vendors. Within one machine and
  driver a render is stable; across machines, compare with a tolerance.
- Noise is seeded from the frame index and the pixel position, not from
  uninitialised state.
- Effect passes are shaders too, so a chain of passes stays reproducible; `TIME0`
  is injected into every pass.

## Checks

```powershell
.venv\Scripts\python -m pytest -q        # 71 unit tests, no GPU needed
.venv\Scripts\python tests\gpu_parity.py # GPU: generated field vs a Python reference
```

`gpu_parity.py` renders the real generated GLSL of `shows/ring` on 256 sample points
at 16-bit precision and compares each decoded distance against an independent
analytic torus. It currently reports a maximum absolute error of 0.0076 against a
tolerance of 0.01. Exit code 0 means the generated shader matches the mathematics.

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
| two renders differ by a few hundred bytes | check `-r 1` is still passed to vspipe; without it the first frames can vary |
| an effect pass has no visible change | check the `## Effects` table: rows merge per effect, and order is first appearance |
| the whole frame is black with `crt` | `curvature` is pushing the corners off-screen; lower it |
| a kaleido fold hides the scene | the fold repeats the field, so raise `distance` or move `target` |
| a 2D layer is missing | its `Sections` cell is `x`; a 2D layer is drawn only when its row is active |
| a 2D character's face floats | trousers, neck, shirt, arms, head, hair, sclera, pupils and mouth are separate rows; check their `cx`/`cy` agree |
| the 2D picture has no shading | by design: a layer is one flat fill, and `outline` draws the rim |
| text is clipped at the top of the bubble | the mask's baseline and canvas must derive from the same numbers; see `SPEC.md` §10.3 |
| letters are too big but the bubble is right | lower `font` only; `panel` is the padding, independent of type size |
| every bubble shows the same line | a `ModifyFrame` closure captured the loop variable; bind the mask through a factory |
| a bubble does not appear at the bar it should | `overlay_plan` windows are half-open in frames; sample inside `bars * bar` |
| a bubble tail points at nobody | the bubble is placed from the speaker's `cx` and the camera track at that bar; check both |
| a close-up shows the wrong character | `focus_x` at that bar is another speaker's `cx`; the shots are `cuts` keys |
| faces look flat and mouthless | a mouth is one layer over the head; check its `kind=2` row is active and its track moves |
| a hair cap covers the eyes | raise `fringe`; it is the lowest q.y the cap reaches |
| the show runs past the last line | `bars: auto` ends it on the final Dialogue bar |
| two legs render as one wide column | mirror with `abs` on the local point inside the box formula |

## Project layout

```
sdfshow/        the Python package (parser, clock, codegen, renderer, CLI)
fields/         GLSL SDF template library
shows/first/    the worked example (8 bars, 120 BPM)
shows/reel/     the 30-second reel: tunnel, Menger, gyroid, orbs, sun (morphs, folds, effects)
shows/demo/     the demoscene set (tunnel, Menger, gyroid, sun and columns)
shows/ops/      subtract and intersect operators, plus a span=2 steps track
shows/post/     a one-bar probe of the effect chain
shows/pixel/    flat 2D cutouts: diner, then living room, close-ups, dialogue
shows/diner/    the 3D animation: two people in a booth, cut-track camera, dialogue
shows/island/   the second 2D demo: night cliff, stone arch, campfire, caption text
assets/sprites/ cleaned sprite strips used by shows/island (Pip and the pirate)
shows/ring/     a one-field probe
tests/          pytest suite + tests/gpu_parity.py (manual GPU check)
gen/            generated shaders and scores (gitignored)
output/         renders, stills and logs (gitignored)
SPEC.md         the SRS: architecture, control surfaces, acceptance checks
TUTORIAL.md     the long-form guide: SDF, VapourSynth, Markdown, walkthroughs
TODO.md         open work
```

## Licence

PolyForm Noncommercial 1.0.0 - see [LICENSE.md](LICENSE.md). Required notice:
Copyright Xyzzy Apps (xyzzyapps@gmail.com).

## Lineage

The project is shaped like `fftechno` (songs as Markdown folders, templates with
`{{placeholders}}`, no defaults, versioned renders), but it shares no code and no
dependency with it. Where audio mixes by addition, an SDF composes by
`min`/`max`, so the arrangement became an operator table and the instruments became
GLSL function bodies. Prior art in the same space: Shader Park, ISF, glslViewer,
Hydra, Punctual, sdfx/sdfray, and the `libplacebo` hook system itself.