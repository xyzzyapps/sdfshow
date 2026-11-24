# TUTORIAL - sdfshow from first principles

This tutorial explains the whole machine: what a signed distance field is, how
VapourSynth turns one into frames, and how a show's Markdown becomes a shader. It is
written so that you can start from an empty folder and finish with a rendered show,
without reading the source first.

- [0. The one-paragraph version](#0-the-one-paragraph-version)
- [1. Install and render something](#1-install-and-render-something)
- [2. The pipeline, end to end](#2-the-pipeline-end-to-end)
- [3. Signed distance fields](#3-signed-distance-fields)
- [4. The clock](#4-the-clock)
- [5. `show.md`](#5-showmd)
- [6. `fields.md`](#6-fieldsmd)
- [7. Templates in `fields/`](#7-templates-in-fields)
- [8. VapourSynth and libplacebo](#8-vapoursynth-and-libplacebo)
- [9. Effect passes](#9-effect-passes)
- [10. Reading the generated shader](#10-reading-the-generated-shader)
- [11. Walkthrough: `shows/first`](#11-walkthrough-showsfirst)
- [12. Walkthrough: `shows/demo`](#12-walkthrough-showsdemo)
- [13. Walkthrough: `shows/ops`](#13-walkthrough-showsops)
- [14. Walkthrough: `shows/pixel`](#14-walkthrough-showspixel)
- [15. Recipes](#15-recipes)
- [16. Debugging](#16-debugging)
- [17. How the pieces fit together](#17-how-the-pieces-fit-together)
- [18. Limits and pitfalls](#18-limits-and-pitfalls)
- [19. Glossary](#19-glossary)

---

## 0. The one-paragraph version

A **show** is a folder with two Markdown files. `show.md` carries the clock
(`bpm`, `bars`, `fps`), the camera, the order of the fields and an arrangement of bar
ranges. `fields.md` defines the fields (one SDF template each, plus parameters) and
the animation **tracks**. `sdfshow compile` substitutes the values into GLSL
function bodies, generates one complete libplacebo shader and writes it to
`gen/<show>/scene.glsl`. VapourSynth shades a blank clip with that shader, frame by
frame, and pipes Y4M to ffmpeg, which only encodes. Nothing is animated by a
timeline editor: every number lives in Markdown, and time comes from the frame index.

---

## 1. Install and render something

Requirements: Python 3.10+, VapourSynth with **vs-placebo**, a Vulkan GPU, and
ffmpeg 9+.

```powershell
python -m venv .venv
.venv\Scripts\pip install -e .
.venv\Scripts\python -m vapoursynth config
```

`vapoursynth config` writes the interpreter path into
`%APPDATA%\vapoursynth\vapoursynth.toml`. `vspipe` needs it; without it you get
`Failed to initialize VSScript`.

Verified from a clean clone: clone, create the venv, `pip install -e .`,
`python -m vapoursynth config`, then `compile`, `frame`, `render` and
`tests/gpu_parity.py` all succeed with no extra steps.

Render the worked example:

```powershell
.venv\Scripts\python -m sdfshow compile --show first
.venv\Scripts\python -m sdfshow frame   --show first --at 5
.venv\Scripts\python -m sdfshow render  --show first
```

- `compile` writes `gen/first/scene.glsl` and `gen/first/score.json`.
- `frame` writes a PNG you can open immediately.
- `render` writes `output/first/show.mp4` (or `_v2` if that exists).

Render the demoscene set:

```powershell
.venv\Scripts\python -m sdfshow render --show demo
```

A 960x540, 16-second show takes a few seconds here; 480 frames of the `first` show
encode in about 15-18 seconds with the deterministic encoder settings.

---

## 2. The pipeline, end to end

```
shows/<show>/show.md      shows/<show>/fields.md      fields/*.glsl
        |                         |                         |
        |  clock, stage,          |  globals, fields,       |  GLSL
        |  arrangement            |  tracks                 |  function bodies
        +-----------+-------------+-------------------------+
                    |
                    |  sdfshow compile
                    v
        gen/<show>/scene.glsl          one //!HOOK MAIN shader
                    |
                    |  sdfshow render  (writes gen/<show>/render.vpy)
                    v
        gen/<show>/render.vpy          VapourSynth: BlankClip -> placebo.Shader
                    |
                    |  vspipe -c y4m -s A -e B
                    v
        ffmpeg -f yuv4mpegpipe -i -   (encode only)
                    v
        output/<show>/show.mp4
```

Three properties fall out of this design:

1. **The shader is the artifact.** Everything the GPU runs is in `scene.glsl`. You
   can read it, diff it, and debug a compile error against it.
2. **ffmpeg is not a filter.** It receives finished frames and writes H.264. No
   `geq`, no `frei0r`, no ffmpeg filter touches the picture.
3. **Time is a frame index.** `t = (frame + TIME0) / fps`. There is no accumulated
   state, so frame *n* is reproducible and a range render equals the same range of a
   full render.

---

## 3. Signed distance fields

### 3.1 What a distance function is

A signed distance field (SDF) is a function of a point in space that returns the
distance to the nearest surface. The sign says which side you are on:

```
d(p) < 0   inside
d(p) = 0   on the surface
d(p) > 0   outside, at distance d(p)
```

The simplest field is a sphere of radius `r`:

```
d(p) = length(p) - r
```

You never store triangles. You store a formula, and a renderer evaluates it.

### 3.2 How a raymarcher uses it

For each pixel, build a ray from the camera (`ro`) in a direction (`rd`) and walk:

```
t = 0
repeat N times:
    p = ro + rd * t
    d = map(p)
    if d < epsilon: hit
    t += d
    if t > far: miss
```

The key property is that, outside the surface, `d` is a lower bound on how far you
can travel without hitting something, because the nearest surface is at least that
far away everywhere. If the function *overestimates* the distance, the ray can step
through a surface. Every template in this project must either be an exact distance
or a deliberate underestimate.

### 3.3 Composition

A distance field composes with `min` and `max`, not with `+`:

| operation | formula |
|-----------|---------|
| union | `min(a, b)` |
| intersection | `max(a, b)` |
| subtraction `a - b` | `max(a, -b)` |

A smooth union replaces `min` with a blend that rounds the join:

```
h = clamp(0.5 + 0.5*(b - a)/k, 0, 1)
smin(a, b, k) = mix(b, a, h) - k*h*(1-h)
```

`smax(a, b, k) = -smin(-a, -b, k)` gives smooth intersection and subtraction.

This is why a show's arrangement is an **operator table** and not a gain matrix:
composition is order-dependent and non-linear. `smin` also does not return an exact
distance, so a large blend radius can distort shading and slow the march.

### 3.4 Normals and shading

The normal is the gradient of the field. The shader uses the tetrahedron trick:

```
n = normalize(
    h.xyy * map(p + h.xyy*e) +
    h.yyx * map(p + h.yyx*e) +
    h.yxy * map(p + h.yxy*e) +
    h.xxx * map(p + h.xxx*e)
)
```

with `h = (1, -1)`. Ambient occlusion samples the field along the normal; soft
shadows march towards the light and accumulate the minimum of `8*d/step`. Both are
in the generated shader and cost extra field evaluations.

### 3.5 Domain repetition

An object can repeat infinitely by folding space with `mod`:

```
q = mod(p + 0.5*spacing, spacing) - 0.5*spacing
d = shape(q)
```

This is how the tunnel and the colonnade get many copies for the price of one. The
catch: `shape(q)` is the distance to the copy in the *current* cell, which can
overestimate the distance to the nearest copy in an adjacent cell. Near a cell
boundary that lets the ray overshoot.

`fields/tunnel.glsl` avoids the problem by evaluating the two nearest ring planes
explicitly, and taking the smaller result. That is exact for a 1D repetition.

### 3.6 Approximate distances

Some shapes have no simple exact distance. The wavy floor and the gyroid are
approximations. Both multiply the estimate down with a `shrink` parameter below 1,
so the marcher is conservative:

```
approx = abs(g) / scale * shrink - thickness
```

If you write a new template, ask: "is this always at most the true distance?" If
not, scale it down.

### 3.7 What the renderer adds

The generated shader is deliberately simple: one key light, Lambert diffuse,
Blinn-Phong specular, a rim term, 5-tap AO, 24-step soft shadow, exponential fog,
Reinhard tonemapping, gamma 2.2. There is no path tracing and no global illumination.
The look comes from geometry, colour and the screen pass.

---

## 4. The clock

`bpm`, `bars`, `fps` and `size` produce one timing truth:

| name | formula | at 120 BPM |
|------|---------|------------|
| `beat` | `60 / bpm` | 0.5 s |
| `bar` | `4 * beat` | 2.0 s |
| `step` | `beat / 4` | 0.125 s |
| `dur` | `bars * bar` | 16 s for 8 bars |
| `frames` | `round(dur * fps)` | 480 at 30 fps |

These are substituted into templates as **durations in seconds**, not indices:

```glsl
mod(t, {{bar}})            // position inside the current bar
floor(t / {{bar}})         // bar index
{{step}}                   // one 16th note in seconds
```

The shader's clock is:

```
t = (frame + TIME0) / FPS
```

`TIME0` is the absolute first frame of the render. A libplacebo hook's `frame`
counter starts at zero for every render session, even when VapourSynth is asked to
start at frame *N*. Without `TIME0`, `--from 24.8` would replay the show from zero.
`render.py` fills the `// @TIME0@` sentinel in the shader with the first frame.

---

## 5. `show.md`

### 5.1 Scalars

```markdown
bpm: 120
bars: 16
fps: 30
size: 960x540
```

`bpm`, `bars` and `fps` are required. `size` defaults to `1280x720`. A scalar value
is a single token: no spaces. `audio:` is parsed but not yet used.

### 5.2 Stage

The first table in `show.md` whose header is exactly `| key | value |` is the Stage
table. Values are numbers, `r|g|b` triples, track names, or arithmetic over tracks
and `t`.

| key | meaning | default |
|-----|---------|---------|
| `distance` | camera distance from the target | `4.2` |
| `yaw` | orbit angle, radians | `0.6` |
| `pitch` | elevation, radians | `-0.18` |
| `fov` | focal length multiplier; larger is narrower | `1.9` |
| `target` | look-at point, `x\|y\|z` | `0\|0\|0` |
| `fog` | exponential fog density | `0.03` |
| `exposure` | gain before tonemapping | `1.1` |
| `background` | `r\|g\|b`, also the fog colour | `0.02\|0.025\|0.04` |
| `light` | key light direction, `x\|y\|z` | `0.6\|0.8\|0.5` |
| `scanlines` | darken alternate pixel rows | `0` |
| `plasma` | slow screen-space colour wash | `0` |
| `grain` | per-pixel noise | `0.012` |
| `vignette` | radial darkening | `0.22` |
| `hue` | rotate every material colour around grey | `0` |
| `fold` | repeat space before every field: `none`, `mirror`, `kaleido` | `none` |
| `fold_count` | number of sectors for `fold: kaleido` | `6` |

`fold` is applied inside `fold_space(p)`, which the scene and the material pass both
call. It is the cheapest way to get a signature demoscene look:

```
none     p unchanged
mirror   p.x = abs(p.x); p.z = abs(p.z)      four copies, seamless
kaleido  fold the XZ angle into a sector, then take abs(a)
```

Because the fold happens before every field, a single sphere becomes eight, or a
sculpture becomes a kaleidoscope, without touching a template.

Camera construction:

```
ro    = target + distance * (cos(pitch)*sin(yaw), sin(pitch), cos(pitch)*cos(yaw))
ta    = normalize(target - ro)
right = normalize(cross(ta, worldUp))
up    = cross(right, ta)
rd    = normalize(uv.x*right + uv.y*up + fov*ta)
```

A larger `fov` value means a longer focal length, so the view is narrower.

The last five rows are the screen pass. They run per pixel after the 3D render:

```
col *= clamp(1 - vignette * dot(uv, uv), 0, 1)
sl   = 0.5 + 0.5*sin(pixel.y * PI)
col *= 1 - scanlines * sl
pl   = sin(uv.x*7 + t*1.7) + sin(uv.y*8 - t*1.3) + sin((uv.x+uv.y)*5 + t*0.9)
col += plasma * (0.5 + 0.5*sin(pl*1.5 + t)) * vec3(0.15, 0.35, 0.6)
col += (hash(pixel + frame) - 0.5) * grain
```

`hue` is applied to each material colour inside `mat_color`, before lighting. It is
a rotation around the grey axis, so whites stay white and greys stay grey.

### 5.3 Fields

```markdown
## Fields

| field |
|-------|
| core  |
| ring  |
| floor |
```

This is the **composition order**. The first active field in a section is the base
surface. The table is found as the first table in `show.md` with a single `field`
column. The set of names must exactly equal the set defined in `fields.md`; a
mismatch fails and names the missing or extra fields.

### 5.4 Materials

```markdown
## Materials

| field | color           | pattern | scale |
|-------|-----------------|---------|-------|
| core  | 1.0\|0.42\|0.16 | stripes | 3.0   |
| floor | 0.08\|0.10\|0.22 | checker | 1.6   |
```

- `color` is `r|g|b` in linear space.
- `pattern` is `none`, `checker`, `grid` or `stripes`.
- `scale` is the pattern frequency (default `1`).

The table is found by its `## Materials` heading, so a prose table elsewhere cannot
be mistaken for it. Patterns are evaluated per hit in world space:

```
checker  mod(floor(p.x*scale) + floor(p.z*scale), 2)
grid     abs(fract(p.xz*scale) - 0.5), lines near 0.5
stripes  step(0.5, fract(p.y*scale))
```

A pattern modulates the base colour; it does not change the distance. A field with
no Materials row gets a deterministic golden-angle hue at 55% saturation.

### 5.5 Sections

```markdown
## Sections

| bars  | core | ring   | floor |
|-------|------|--------|-------|
| 0-2   | u    | x      | u     |
| 2-4   | u    | u0.30  | u     |
| 4-8   | u    | u0.18  | u0.4  |
```

Rows are bar ranges; columns are fields; cells are composition operators. The table
is found by its `## Sections` heading, so prose tables cannot be mistaken for data.

| cell | meaning |
|------|---------|
| `u` | union |
| `u0.3` | smooth union, blend radius 0.3 |
| `s0.2` | smooth subtraction |
| `i0.1` | smooth intersection |
| `m0.5` | morph: cross-fade the accumulator towards this field |
| `x` or blank | absent |

The operand after any operator may be a number **or a track name**, so a blend radius
or a morph weight animates: `u0.3`, `mkick`, `m0.5`.

A morph is a cross-fade between two distances, and the average of two distances is not
a distance. It looks right when both fields occupy the same space (concentric solids);
use a section boundary for a scene change. `shows/ops` and `shows/reel` both rely on
that rule.

Rules, all enforced:

1. The first section starts at bar 0.
2. Each section starts where the previous ended.
3. The last section ends at `bars`.
4. Every field has a cell in every section.
5. Every column names a field.
6. The first active cell of a section must be a union.

Row order is semantic: cells apply left to right. A section can be empty (`x`
everywhere); it renders the background.

### 5.6 A complete annotated example

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
| pitch    | -0.16   |
| fog      | 0.055   |
| exposure | 1.15    |

## Fields
| field |
|-------|
| core  |
| ring  |
| floor |

## Materials
| field | color           | pattern | scale |
|-------|-----------------|---------|-------|
| core  | 1.0\|0.42\|0.16 | stripes | 3.0   |
| ring  | 0.2\|0.72\|1.0  | none    | 1.0   |
| floor | 0.08\|0.10\|0.22 | checker | 1.6   |

## Sections
| bars | core | ring  | floor |
|------|------|-------|-------|
| 0-2  | u    | x     | u     |
| 2-4  | u    | u0.3  | u     |
| 4-8  | u    | u0.18 | u0.4  |
```

`dolly`, `spin` and the rest are tracks defined in `fields.md`. The Stage table can
refer to them because both files are parsed before the shader is generated.

---

## 6. `fields.md`

### 6.1 Globals

Top-level `key: value` scalars are shared by every field:

```markdown
scale: 2.4
spin: 0.3
```

They may reference the clock or one another:

```markdown
pulse_len: 0.5*{{beat}}
```

Clock names are injected (`bar`, `beat`, `step`, `dur`, `frames`, `fps`, `w`, `h`)
and **may not be redefined**. Redefining them fails, because the clock has one
source of truth.

### 6.2 Fields

```markdown
## Fields

| name  | template        | parameters |
|-------|-----------------|------------|
| core  | sphere.glsl     | radius=0.62*pulse, cx=0, cy=0.10*sin(t*0.7), cz=0 |
| floor | plane_wave.glsl | amp=0, freq=1, speed=0, level=-1.3, shrink=1 |
```

- `name` must be unique and match `[A-Za-z_][A-Za-z0-9_]*`.
- `template` is a file in `fields/`.
- `parameters` is `key=value, key=value`. Commas inside parentheses do not split,
  so `b=min(1, 2)` is one value.

### 6.3 The parameter expression language

A parameter value is resolved in two steps:

1. `{{key}}` references are expanded from globals and clock tokens.
2. The result is validated and tracks are expanded.

The second step accepts numbers, track names, `t`, `PI`, `TAU`, and this function
list:

```
abs sin cos tan asin acos atan exp log sqrt pow floor ceil fract mod
min max clamp mix step smoothstep sign
```

An unknown identifier is an error naming the identifier and the value. This is why
`0.62*pulse` works and `0.62*puls` fails before a broken shader is written.

Scientific notation is not part of the number token; write `0.0001`, not `1e-4`.

Precedence is plain GLSL. Arithmetic is left to right as you would expect. There is
no statement syntax; if you need conditionals or loops, put them in a template or an
`expr` track.

### 6.4 Tracks

```markdown
## Tracks

| name  | kind  | values            | options     |
|-------|-------|-------------------|-------------|
| pulse | steps | 1.05\|0.92\|0.86  | ease=smooth |
| dolly | keys  | 0:4.8\|3:4.1      | ease=smooth |
| spin  | expr  | 0.45+0.12*t       |             |
```

A `## Tracks` table may live in `fields.md` **or** `show.md`; both are read and merged.
Put camera and effect tracks next to the Stage table in `show.md`, and field tracks
next to the fields in `fields.md`. A name defined in both files is an error. The table
is recognised by its first three headers; the fourth column is optional.

| kind | values | options |
|------|--------|---------|
| `steps` | `a\|b\|c` | `span=<bars>` (default 1), `ease=none\|smooth` |
| `bars` | `a\|b\|c` | `ease=none\|smooth` |
| `keys` | `bar:value\|bar:value` | `ease=none\|smooth` |
| `expr` | one GLSL expression over `t` | none |

Generated behaviour:

- **steps**: one value per 16th step within `span` bars, looping. Values are
  interpolated linearly from one step to the next; `ease=smooth` replaces the linear
  blend with `smoothstep`, so each change eases in and out.
- **bars**: one value per bar, looping over the length of the list, interpolated the
  same way.
- **keys**: piecewise interpolation between explicit bars, clamped before the first
  and after the last. Keys are absolute bars, not relative.
- **expr**: raw GLSL. This is the escape hatch; unlike parameters it is not
  token-validated, so it must be valid GLSL.

Each track becomes `float track_<name>(float t)`.

### 6.5 Loud failure

There are no defaults. A template hole with no value fails, naming the field and
the key. An unknown track/function fails, naming the identifier. A missing template
file fails. A duplicate field fails. A field in `fields.md` that is not in
`show.md`'s Fields table fails.

The purpose is simple: the Markdown is the source of truth, and a typo must never
turn into a plausible-looking render.

---

## 7. Templates in `fields/`

### 7.1 The contract

Each `.glsl` file is the **body** of a function:

```glsl
float field_<name>(vec3 p, float t) {
    <your template>
}
```

`p` is the sample point in world space, `t` is show time in seconds. The body must
return a distance. It must contain `return`; an unresolved placeholder is an error.

### 7.2 Preprocessing

Templates are written for humans:

1. Every `//` comment is removed from each line.
2. Blank lines and lines starting with `#` are removed.
3. The remaining lines are joined with one space.
4. `{{key}}` placeholders are substituted.

So you can write:

```glsl
// A capsule between two points.
vec3 a = vec3({{ax}}, {{ay}}, {{az}});
vec3 b = vec3({{bx}}, {{by}}, {{bz}});
vec3 pa = p - a;
vec3 ba = b - a;
float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
return length(pa - ba * h) - {{radius}};
```

Two consequences:

- `//` comments are removed *before* joining, so a comment can never swallow the
  next line.
- A line cannot start with a GLSL preprocessor directive, because `#` means
  Markdown comment. There is no need for one in a template body.

### 7.3 Helpers available in every template

```
PI, TAU, BAR, BEAT, STEP, DUR, FPS, FRAMES
rot2(vec2, float)  rotX(vec3, float)  rotY(vec3, float)  rotZ(vec3, float)
smin(float, float, float)  smax(float, float, float)
hash11(float)  hash21(vec2)  hash13(vec3)
vnoise(vec3)  fbm(vec3)                    // 4-octave value noise
apply_pattern(int, float, vec3, vec3)
hue_rotate(vec3, float)
```

`vnoise` returns 0..1 and `fbm` sums four octaves, so organic displacement is one
line:

```glsl
float h = fbm(p * 2.5) * 0.4;
return (p.y - h) * 0.6;   // approximate: scaled down to stay a bound
```

### 7.4 The shipped library

| template | what it returns | params | exact? |
|----------|-----------------|--------|--------|
| `sphere.glsl` | sphere at an offset | `radius cx cy cz` | yes |
| `box.glsl` | rounded box | `cx cy cz hx hy hz round` | yes |
| `capsule.glsl` | capsule between two points | `ax ay az bx by bz radius` | yes |
| `torus.glsl` | torus, spin and tilt | `radius thickness spin tilt` | yes |
| `cylinder.glsl` | capped cylinder along Y | `cx cy cz radius half_height` | yes |
| `cone.glsl` | capped cone `r1` to `r2` | `cx cy cz r1 r2 half_height` | yes |
| `hexprism.glsl` | hexagonal prism along Z | `cx cy cz radius half_height` | yes |
| `plane_wave.glsl` | wavy plane; `amp=0` is flat | `amp freq speed level shrink` | no |
| `terrain.glsl` | noise ground plane | `amp freq offset level shrink` | no |
| `helix.glsl` | helical tube | `cx cy cz pitch turn radius tube shrink` | no |
| `tunnel.glsl` | repeating ring tunnel along Z | `spacing offset radius thickness twist` | yes |
| `menger.glsl` | Menger sponge | `cx cy cz half spin iterations` | yes |
| `gyroid.glsl` | gyroid shell in a sphere | `spin scale shrink thickness radius` | no |
| `pillars.glsl` | ring of columns | `ring count radius center_y half_height` | no |
| `spheres.glsl` | ring of `count` spheres | `cx cy cz radius count spin orb` | yes |
| `mandelbulb.glsl` | mandelbulb distance estimate | `cx cy cz power iterations` | no |

"Exact" means the function returns at most the true distance, so the marcher cannot
overshoot. The approximate ones all have a `shrink` knob for that reason.

`mandelbulb.glsl` is the expensive one: six iterations of `pow`, `acos` and `atan`
per sample, inside a 160-step march. Use it in a scene where nothing else is active,
and expect a render several times slower.

Read the library in order; it goes from a one-liner to the demoscene pieces.

### 7.5 Writing your own

Start with a shape you can verify visually. A sphere is a good smoke test:

```glsl
vec3 q = p - vec3({{cx}}, {{cy}}, {{cz}});
return length(q) - {{radius}};
```

Then add motion. There are two places to put it:

- **inside the template**, using `t` (the torus spins and tilts this way), or
- **in a parameter**, using a track (the sphere's radius and height do this).

Rule of thumb: if the motion changes a number, use a track; if it changes the
coordinate system, do it in the template. Rotating the space before evaluating the
shape is cheaper and more stable than animating many parameters.

If your shape is an approximation, multiply the result down with a `shrink`
parameter until the surface is stable. A too-large estimate makes the marcher skip
the surface and produce holes.

---

## 8. VapourSynth and libplacebo

### 8.1 What VapourSynth is

VapourSynth is a frame server: you write a Python script that builds a graph of
filters, and `vspipe` pulls frames out of it. It is the same idea as a video
processing graph, but the frames can live on the GPU.

sdfshow keeps the graph deliberately thin. It uses three filters:

| filter | role |
|--------|------|
| `core.std.BlankClip` | frame carrier and clock |
| `core.placebo.Shader` | one call per generated pass |
| `core.resize.Bicubic` | YUV444P16 to YUV420P8 for the encoder |

Everything else VapourSynth ships (`Expr`, `Convolution`, `AverageFrames`,
`MaskedMerge`, `Trim`, `Loop`, `Deband`, ...) is unused. That is a choice, not an
oversight: the picture is one generated GLSL program plus generated post passes, so
there is exactly one language to read and one place a bug can be.

The generated script is short. With two effect passes it is this shape:

```python
import vapoursynth as vs

core = vs.core
W, H, FPS, NF = 960, 540, 30, 480
PASSES = [r".../scene.glsl", r".../fx_1_bloom.glsl", r".../fx_2_chroma.glsl"]

def shade(clip, path):
    """Run one generated libplacebo pass over *clip*."""
    with open(path, encoding="utf-8") as fh:
        src = fh.read().replace("// @TIME0@", "#define TIME0 0")
    return core.placebo.Shader(
        clip, shader_s=src, width=W, height=H,
        sigmoidize=False, linearize=False, matrix=5,
    )

clip = core.std.BlankClip(
    width=W, height=H, format=vs.YUV444P16, length=NF, fpsnum=FPS, fpsden=1
)
for path in PASSES:
    clip = shade(clip, path)
clip = core.resize.Bicubic(
    clip, format=vs.YUV420P8,
    matrix_in_s="470bg", matrix_s="470bg",
    range_in_s="limited", range_s="limited",
)
clip.set_output()
```

Line by line:

- `BlankClip` creates `NF` empty frames at the show's size and rate. The shader
  ignores the clip's contents entirely; it only uses the frame counter.
- `core.placebo.Shader` compiles the GLSL hook and runs it per frame on the GPU.
  `width`/`height` are the output size.
- Chaining is just calling it again on the previous clip. The format stays
  `YUV444P16` between passes, so no conversion happens mid-chain.
- `YUV444P16` is required. vs-placebo rejects anything else with
  `Input should be YUVxxxP16`. The 16-bit planes also give the shader headroom.
- `matrix=5` selects the colour matrix used around the shader. It is paired with
  `matrix_in_s="470bg"` / `matrix_s="470bg"` in the resize. If you change one,
  change the other or colours will shift.
- `YUV420P8` is what the encoder wants.

### 8.2 The libplacebo hook

libplacebo (the GPU shader engine behind mpv and vs-placebo) accepts a fragment
shader with a small header:

```glsl
//!HOOK MAIN
//!BIND HOOKED
//!DESC first

vec4 hook() {
    ...
    return vec4(col, 1.0);
}
```

Globals the shader uses:

| name | meaning |
|------|---------|
| `HOOKED_pos` | texture coordinate in 0..1, with **y running down** |
| `target_size` | output size in pixels |
| `frame` | frame counter for the current render session, starting at 0 |

Because `HOOKED_pos.y` runs down, the shader flips it:

```
vec2 uv = (HOOKED_pos * target_size - 0.5*target_size) / target_size.y;
uv.y = -uv.y;
```

The generated shader never samples `HOOKED_tex`; it is a pure generator.

### 8.3 The frame counter and `TIME0`

`frame` is not the source frame index. If you ask `vspipe` for frames 300-329, the
hook sees `frame` 0..29. That is fine for a full render but wrong for a range
render. The fix is the `// @TIME0@` sentinel: `render.py` rewrites it to
`#define TIME0 300`, and the shader computes `t = (frame + 300)/FPS`.

This is why a still at 24.8 s and the first frame of a clip starting at 24.8 s match
(verified at 41 dB PSNR after H.264, i.e. compression only).

### 8.4 Output

`vspipe -c y4m` writes YUV4MPEG2: a small text header followed by uncompressed
planar frames. ffmpeg reads it with `-f yuv4mpegpipe -i -` and encodes. That is the
entire contract between the renderer and the encoder.

---

## 9. Effect passes

The 3D pass writes one image. `## Effects` appends post passes. Each is a separate
libplacebo hook that reads the previous pass through `HOOKED_tex`, so it can never
change geometry and never re-marches.

```markdown
## Effects
| effect | key       | value |
|--------|-----------|-------|
| bloom  | strength  | 0.7   |
| bloom  | threshold | 0.6   |
| chroma | amount    | 0.04  |
| crt    | curvature | 0.1   |
| glitch | chance    | 0.03  |
```

- Order is **first appearance** in the table. Rows for one effect merge into one
  parameter set, so you can spread `bloom` over two rows.
- Defaults live in `glsl._EFFECT_DEFAULTS`; a value must be numeric or the build
  fails naming the effect and the key.
- Each pass is written to `gen/<show>/fx_<n>_<name>.glsl`, and `render.vpy` chains
  them in a loop. Inspect them exactly like `scene.glsl`.

| effect | knobs | implementation |
|--------|-------|----------------|
| `bloom` | `threshold`, `strength`, `radius` | 5x5 weighted `HOOKED_texOff` blur, `smoothstep` bright-pass, added back |
| `chroma` | `amount` | radial red/blue offset scaled by `dot(d,d)` |
| `crt` | `curvature` | barrel-warped sample; outside is black |
| `glitch` | `amount`, `rate`, `chance` | per-band `hash11` offsets on a time quantised by `rate`, plus a fixed RGB split |

Cost, measured on this machine at 960x540: adding bloom + chroma + glitch to the
demo took the render from about 21 fps to 13 fps of wall time. The passes are cheap
relative to the raymarch, which dominates.

Determinism holds: `TIME0` is injected into every pass, glitch time is quantised
rather than accumulated, and no pass reads wall-clock.

## 10. Reading the generated shader

Open `gen/<show>/scene.glsl` after a compile. The order is:

1. hook header and the `TIME0` sentinel
2. defines: `FPS`, `BAR`, `BEAT`, `STEP`, `DUR`, `FRAMES`, `PI`, `TAU`
3. helpers: `smin`, `smax`, hashes, rotations, `apply_pattern`, `hue_rotate`
4. generated tracks, then generated fields
5. `map_scene` and `mat_id` (the arrangement)
6. `mat_color`
7. camera functions
8. `calc_normal`, `calc_ao`, `soft_shadow`, `post`, `render`
9. `hook`

A trimmed arrangement looks like this:

```glsl
float map_scene(vec3 p, float t) {
    float d = 1e9;
    if (t < 4.0) {
        d = field_core(p, t);
        d = smin(d, field_floor(p, t), 0.0);
    } else if (t < 8.0) {
        d = field_core(p, t);
        d = smin(d, field_ring(p, t), 0.3);
        d = smin(d, field_floor(p, t), 0.0);
    } else {
        ...
    }
    return d;
}
```

`mat_id` re-evaluates only the union fields at the hit point and returns the nearest
one. That is how each field gets its own colour.

The march loop:

```glsl
for (int i = 0; i < 160; i++) {
    vec3 p = ro + rd * travel;
    float s = map_scene(p, t);
    if (s < 0.0) break;                       // started inside geometry
    if (s < 0.0012 + 0.0006 * travel) { hit = 1.0; break; }
    travel += s;
    if (travel > 48.0) break;
}
```

The negative test matters: if the camera is inside a solid, the distance is
negative and stepping forward would run backwards. The guard turns that into a clean
background instead of a confusing image.

---

## 11. Walkthrough: `shows/first`

Open `shows/first/show.md` and `shows/first/fields.md` side by side.

### The fields

- `core` is a sphere of radius `0.62*pulse`, bobbing on a slow sine.
- `ring` is a torus whose radius is a `bars` track, tilted and spinning.
- `floor` is the wavy plane; its amplitude is a slow sine.

### The arrangement

- 0-2: sphere + floor
- 2-4: sphere + ring (smooth union 0.30) + floor
- 4-6: ring tighter (0.18), floor softer (0.4)
- 6-8: ring wider (0.45), floor tighter (0.25)

The union radius is the interesting knob: a larger `k` melts the ring into the
sphere; a smaller one keeps it a separate object.

### The camera

`dolly` is a `keys` track, `spin` is `expr`, `tilt` is `expr`, and the stage refers
to them by name. Changing `0:4.8|3:4.1|7:4.5` in `dolly` changes the camera path
without touching the shader.

### Exercises

1. Set `ring_radius` values to `1.6|1.9|1.7|1.5` and watch the ring grow.
2. Change `pulse` from `steps` to `bars` and see the sphere breathe per bar.
3. Set the `floor` cell to `s0.6` in the last section and watch it carve the sphere.
4. Set `hue` to `0.3*t` in the Stage table for continuous colour cycling.
5. Add a Materials row for `ring` with `pattern=stripes` and `scale=2`; keep its
   existing colour, or give it a new `r|g|b`.

---

## 12. Walkthrough: `shows/demo`

The demo is four scenes cut on bar lines at 120 BPM. The camera tracks ramp over
0.35 bars at each cut; the scenes themselves do not overlap.

### 11.1 Ring tunnel (bars 0-4)

`fields/tunnel.glsl`:

```glsl
float s = {{spacing}};
float z0 = mod(p.z - {{offset}} + 0.5*s, s) - 0.5*s;
float z1 = z0 > 0.0 ? z0 - s : z0 + s;
vec2 a = rot2(p.xy, z0 * {{twist}});
vec2 b = rot2(p.xy, z1 * {{twist}});
float d0 = length(vec2(length(a) - {{radius}}, z0)) - {{thickness}};
float d1 = length(vec2(length(b) - {{radius}}, z1)) - {{thickness}};
return min(d0, d1);
```

Two nearest ring planes, each rotated by its own twist. The camera sits at
distance 1.7 with yaw 0, inside the mouth, and the rings recede.

### 11.2 Menger sponge (bars 4-8)

`fields/menger.glsl` starts from a cube and subtracts three levels of crosses:

```glsl
float s = 1.0;
for (int i = 0; i < {{iterations}}; i++) {
    vec3 c = mod(q * s, 2.0) - 1.0;
    s *= 3.0;
    vec3 r = abs(1.0 - 3.0 * abs(c));
    float da = max(r.x, r.y);
    float db = max(r.y, r.z);
    float dc = max(r.z, r.x);
    d = max(d, (min(da, min(db, dc)) - 1.0) / s);
}
```

`spin=menger_spin` rotates the space, so the cube turns in place. Pair it with the
checker floor.

### 11.3 Gyroid (bars 8-12)

```glsl
vec3 q = rotY(p, t * {{spin}});
float g = dot(sin(q * {{scale}}), cos(q.yzx * {{scale}}));
float shell = abs(g) / {{scale}} * {{shrink}} - {{thickness}};
return max(shell, length(q) - {{radius}});
```

The gyroid is a periodic implicit surface; `abs(g)` gives a shell around it, and the
sphere clip gives it a silhouette. `shrink` keeps the estimate conservative.

### 11.4 Sun and columns (bars 12-16)

- `sun` is `sphere.glsl` with `pattern=stripes`, which produces the horizontal bands.
- `pillars` uses polar repetition: one column is modelled, and the angle is folded
  into a sector, giving `count` columns around a ring of radius `ring`.
- `floor` is the flat plane with `pattern=checker`.
- `hue` cycles the palette; `scanlines` and `plasma` give the CRT feel.

### Exercises

1. Change `count=12` to `count=6` and watch the colonnade open up.
2. Set `scanlines` to `0.4` and `plasma` to `0.15` for a heavier CRT look.
3. Move a cut: change a `bars` row from `4-8` to `5-9` and move the matching camera
   keys in `dolly`, `yaw`, `pitch`, `fov` and `fog`.
4. Set the `tunnel` cell in 4-8 to `u0.4` and see the tunnel blend into the Menger.

---

## 13. Walkthrough: `shows/ops`

`shows/ops` exists to prove the two operators the demo does not use.

| bars | arrangement | what you should see |
|------|-------------|---------------------|
| 0-1 | `cube: u` | a rounded cube breathing via a `steps` track |
| 1-2 | `cube: u`, `ring: s0.15` | the torus carved out of the cube |
| 2-3 | `shell: u`, `cube: i0.25` | sphere and cube smoothly intersected |
| 3-4 | same, `ring: s0.08` | the torus carving the intersection |

Two things to notice:

- `i0.25` is not "the overlap": a smooth intersection of a sphere and a cube gives a
  rounded lens shape, and the blend radius controls how much each shape survives.
- The subtract row has no visible effect until the object it carves exists, which is
  why the torus only appears from bar 1.

The `chop` track is a `steps` track with `span=2`, so its four values each last half
a bar. That is the smallest useful demonstration that `span` works.

`shows/reel` is the long one: 30 seconds, five scenes, a Menger-to-gyroid morph, an
animated kaleido fold and a shifting effect chain.

| bars  | what happens |
|-------|--------------|
| 0-3   | ring tunnel, camera creeping forward |
| 3-7   | Menger sponge over the floor, camera whipping out |
| 7-8   | the sponge morphs into a gyroid |
| 8-9   | gyroid alone |
| 9-12  | orb cluster (a sphere multiplied by the kaleido fold) |
| 12-13 | orbs plus the colonnade |
| 13-15 | the cluster morphs into the striped sun |

Two lessons are baked into that table:

- The morph is `m<track>`, and a morph cross-fades two *distances*. It only reads
  correctly between concentric solids, so the reel morphs Menger to gyroid and orbs to
  sun, and uses a section boundary everywhere else.
- `fold_count` is a track, so the kaleido ripple is a value in the Stage table, not a
  new template.

## 14. Walkthrough: `shows/pixel`

`shows/pixel` is the flat 2D show. It is the same Markdown format as everything else;
only the Stage says so:

```markdown
| key           | value            |
|---------------|------------------|
| mode          | 2d               |
| pixel         | 1                |
| outline       | 0.005            |
| outline_color | 0.10\|0.06\|0.06 |
| zoom          | zoom             |
| focus_x       | focus_x          |
| focus_y       | focus_y          |
| font          | 0.020            |
| panel         | 2.60             |
```

There is no march and no 3D camera, but there are still shots. `compile` emits a
`render_2d(uv, t)` that scales the whole layer stack around a focus point, and the
frame is painted back-to-front:

```
col = background
for each layer, in Fields order:
    if the current section draws it:
        d = layer(p)
        if d < -outline:  col = colour
        elif d < 0:       col = mix(outline, colour)
```

Three things follow from that loop, and they are the whole of 2D authoring:

1. **Table order is depth.** The first row in `Fields` is furthest back. A character
   behind a table is listed before the table; there is no per-pixel depth test.
2. **A layer is one flat fill.** A figure is ten rows - trousers, neck, shirt, arms
   and hands, head, hair, white sclera, pupils, mouth - because a single row cannot
   carry shading or a second colour. A window is a pane plus a frame for the same reason.
3. **A cell is visibility, not an operator.** `x` means the layer is absent; `u` and
   `u<k>` both mean "draw it". Two flat fills cannot be min/maxed, so `s` and `i` are
   meaningless here and `m<w>` becomes a fade gate at `w > 0.5`.

The show has two **settings**, switched by `Sections`. Both rooms' furniture sits in
one `Fields` table; only the active section's rows are drawn:

| bars  | setting | who |
|-------|---------|-----|
| 0-8   | the diner: blue wall, booth, table, cup | Aina and Boris in the booth; Dora standing |
| 8-20  | the house: beige wall, sofa, rug, lamp | Aina and Boris on the sofa; Dora and Ellis standing |

That is the point of the show: a scene change is a section change, not a second
show. The clock, the dialogue table and the render are shared.

The whole cast is paper-white; the shirts, hair and trousers are the palette. The four
characters are distinguished by **silhouette**: Aina narrow with a bowl cut,
Boris broad with a flat top, Dora long-haired, Ellis round and balding. Colour is a
second cue, not the first, because a cutout has to read at a glance.

The look is construction paper, not pixels. `pixel` is `1` (off); the shapes are big
and simple, the heads are large relative to the bodies, and the eyes are white ovals
with small dark pupils. An early version kept the 9-pixel quantise and dark eye
shapes, which merged the eyes into the hair and turned the faces into masks.

### Shots and mouths

South Park's grammar is wide, close, close, wide. There is no camera, so the show gets
it from three stage keys that a `cuts` track switches on bar boundaries:

```markdown
| zoom    | cuts | 0:1.0\|1:2.3\|3:1.0\|5:2.1 |
| focus_x | cuts | 0:0.0\|1:-0.44\|3:0.0\|5:0.58 |
```

`zoom` magnifies around `focus_x`/`focus_y`; every layer is evaluated at
`focus + uv/zoom`, and the returned distance is multiplied by the zoom so the outline
keeps a constant width. `shows/pixel` cuts to whichever character is speaking.

The mouth is one layer whose half-height is `0.020 + mouth * 0.10` in face units, with
its top edge fixed and the bottom edge dropping - a jaw, not an inflating oval. The
mouth tracks are windows over each speaker's own bar range. Getting those windows
wrong is why an earlier version looked frozen: Aina's mouth moved during Boris's line,
and neither moved during their own second lines.

Dialogue comes from one table:

```markdown
| speaker | bars | text                              | voice |
|---------|------|-----------------------------------|-------|
| AINA    | 1-2  | Why are we standing? | slt |
```

`dialog.py` reads the speaker's `cx` from `fields.md` and applies the camera at that
line's first bar, so the panel is centred over the head even in a close-up and the
tail points at them. The tail is a wide, short triangle; an earlier version was a
spike on the wrong side of the panel. The text is
rasterised by `textmask.py` into a panel mask and an ink mask, and
`render.py` composites them with `std.MaskedMerge` over the line's frame window. The
shader never sees a glyph.

`shows/island` also shows the hybrid the format is good at: the set (sky, stars, arch,
fire, ledge) is SDF, and the two actors are raster sprites from `assets/sprites/`,
placed by a `## Sprites` table with an idle row and a talking row per character. The
sprites are composited after the SDF passes and before the captions.

`bubble: caption` in the Stage table swaps the speech bubble for a caption: white type
with a dark outline, centred at the top of the frame, no panel. That is the grammar of a
point-and-click adventure, and `shows/island` is the worked example.

The show's length is not a number to keep in step: `bars: auto` ends it on the last
Dialogue bar, which is why the render is 50 seconds and the last line is the last thing
said.

`font` and `panel` are separate on purpose. `font` is the cap height as a fraction of
frame height; `panel` is the padding as a multiple of the type size. An early version
derived both from one number, so asking for smaller letters made the bubble tight
enough to clip the first line. `text_mask` now derives its canvas height and its first
baseline from the same numbers, and a test holds that.

Render it:

```powershell
.venv\Scripts\python -m sdfshow frame  --show pixel --at 4
.venv\Scripts\python -m sdfshow frame  --show pixel --at 20
.venv\Scripts\python -m sdfshow render --show pixel
```

The first still is a close-up on Aina mid-line, mouth open, tail on her head; the
second is a wide shot of the living room. The render is 50 seconds, 1500 frames at
30 fps, with a synthesized voice line at each spoken bar range.

## 15. Recipes

### 12.1 Checkerboard floor

```markdown
| floor | plane_wave.glsl | amp=0, freq=1, speed=0, level=-1.3, shrink=1 |
```

```markdown
| field | color           | pattern | scale |
|-------|-----------------|---------|-------|
| floor | 0.08\|0.10\|0.22 | checker | 1.6   |
```

### 12.2 Synthwave sun

```markdown
| sun | sphere.glsl | radius=1.05, cx=0, cy=0.55, cz=0 |
```

```markdown
| field | color           | pattern | scale |
|-------|-----------------|---------|-------|
| sun   | 1.0\|0.35\|0.12 | stripes | 3.0   |
```

### 12.3 A tunnel

```markdown
| tunnel | tunnel.glsl | spacing=1.6, offset=0.8, radius=1.25, thickness=0.055, twist=0.25 |
```

Camera at `distance=1.7`, `yaw=0`, `pitch=-0.02`, `fov=1.55`. To make it feel like
flying through, animate the rings rather than the camera: give `offset` a track
(`| flow | expr | 0.8+0.7*t |`) so the ring planes stream towards the lens while the
camera stays at the mouth.

### 12.4 A colonnade

```markdown
| columns | pillars.glsl | ring=4.2, count=12, radius=0.22, center_y=-0.1, half_height=1.6 |
```

Camera outside the ring (`distance=8.5`) looking in, floor at `-1.3`.

### 12.5 A camera that cuts between scenes

```markdown
| name  | kind | values |
|-------|------|--------|
| dolly | keys | 0:1.7\|4:1.7\|4.35:6.8\|8:6.2\|8.35:6.6\|12:7.2 |
```

Two keys 0.35 bars apart make a quick move. The cut is a fast ramp, not an instant
jump; if you need a hard cut, make the gap smaller (0.1 bar) or end the first key's
value at the boundary.

### 12.6 A breathing object

```markdown
| name   | kind  | values                     | options     |
|--------|-------|----------------------------|-------------|
| breath | steps | 0.55\|0.62\|0.55\|0.62     | ease=smooth |
```

```markdown
| core | sphere.glsl | radius=breath, cx=0, cy=0, cz=0 |
```

### 12.7 Five-second clips

`--from`/`--to` are half-open, so `--to 5` is exactly 150 frames at 30 fps:

```powershell
.venv\Scripts\python -m sdfshow render --show demo --from 0 --to 5 --out output\demo\clips\tunnel_5s.mp4
```

`--out` creates parent directories and is never versioned (you named it yourself).

---

## 16. Debugging

### 16.1 Compile first

`compile` is cheap and catches most mistakes: unknown identifiers, missing
placeholders, bad sections, missing templates. If it succeeds, open
`gen/<show>/scene.glsl` and confirm the function you care about is there.

### 16.2 One frame is a fast loop

```powershell
.venv\Scripts\python -m sdfshow frame --show demo --at 26 --out check.png
```

Frames are versioned by default (`frame_00780.png`, `frame_00780_v2.png`); pass
`--out` to control the name.

### 16.3 Shader compile errors

vs-placebo prints the whole generated shader with line numbers to
`output/<show>/logs/vspipe.log`. The shader begins after roughly 80 lines of
libplacebo prelude. Search the log for `#define FPS` to find where your code starts,
then subtract that offset from the reported line number.

Common causes:

- a missing `;`
- `float` used where a `vec3` is required
- an array size that is not a constant
- a template line that split a token when the lines were joined

### 16.4 An empty frame

If the image is only background, the camera is probably inside a solid. The
march guard turns that into a clean miss instead of garbage. Check
`distance * sin(pitch)` against the floor level: at distance 7.6 and pitch -0.24 the
camera is at y = -1.8, which is below a floor at -1.3. Raise the camera, reduce the
pitch, or lower the floor.

### 16.5 A missing object

Check the `Sections` cell: a field is only present while its row is active. Then
check the distance: an approximate template with a too-large `shrink` can skip the
surface and produce holes or invisibility. Reduce `shrink`.

### 16.6 Comparing a still with a video

```powershell
.venv\Scripts\python -m sdfshow frame --show demo --at 24.8 --out ref.png
ffmpeg -i output\demo\clips\columns_5s.mp4 -frames:v 1 f0.png
ffmpeg -i f0.png -i ref.png -lavfi psnr -f null -
```

A PSNR around 40 dB means the difference is H.264 compression only. A much lower
number means a clock or scene mismatch.

### 16.7 Logs and locks

- `output/<show>/logs/vspipe.log` - shader compile errors and frame counts.
- `output/<show>/logs/ffmpeg.log` - encoder errors.
- `output/<show>/logs/.build.lock` - exists only while a build runs. If a build
  crashed, delete it.

### 16.8 Determinism checks

- `compile` twice: `scene.glsl` must be byte-identical.
- Render twice: with `-threads 1` on x264 and `-r 1` on vspipe, the MP4s are
  byte-identical on the same machine and driver.
- A still at time *T* and the first frame of a clip starting at *T* must match
  (compression aside).

### 16.9 A determinism gotcha worth knowing

Before `-r 1` was added, two renders of the same show differed. The cause was not
the shader: `vspipe` issues several frame requests in parallel, and the first one or
two frames of a run could come back slightly different. Decoding both files showed
the difference confined to frames 1-2, at about 40 dB PSNR. H.264 then carried it
through the rest of the file, so a hash comparison failed.

If a render of yours is ever non-reproducible:

1. compare the two Y4M streams, not just the MP4s:
   `vspipe -c y4m -r 1 gen/<show>/render.vpy out.y4m`
2. use `psnr=stats_file=...` (a relative path, run from the folder) to see which
   frames differ;
3. a difference confined to the first frames is a frame-request ordering effect; a
   difference spread evenly is a shader change.

---

## 17. How the pieces fit together

The earlier chapters each explain one part. This one is the whole machine in one
place, because the parts only make sense together.

### 17.1 The data flow

```
shows/<show>/show.md      shows/<show>/fields.md      fields/*.glsl
   clock, stage,             fields, parameters,        GLSL function
   arrangement,              tracks                     bodies with {{holes}}
   materials, effects
        \                        |                         /
         +-----------+-----------+------------+
                     |
                     |  sdfshow compile
                     v
        gen/<show>/scene.glsl        one //!HOOK MAIN shader
        gen/<show>/fx_<n>_*.glsl     one shader per effect pass
        gen/<show>/score.json        resolved clock + sections (audit)
                     |
                     |  sdfshow render
                     v
        gen/<show>/render.vpy        VapourSynth: BlankClip -> Shader -> Shader
                     |
                     |  vspipe -r 1 -c y4m
                     v
        ffmpeg (encode only)  ->  output/<show>/show.mp4
```

For the reel specifically that is a 482-line, 17.7 KB `scene.glsl` plus four passes
of 0.6-1.4 KB each. Scaled to the whole project: 12 Python modules, about 74 KB,
of which `glsl.py` (19 KB) is the largest because it owns shader assembly.

### 17.2 Why composition is not addition

An SDF is one number per point, so fields combine with `min`/`max`, never with `+`.
That single fact is why the Markdown looks the way it does:

| an audio tool would | sdfshow does |
|---|---|
| multiply stem gains | apply an operator per field |
| `1.00`, `0.60`, `0.00` | `u`, `u0.6`, `x` |
| sum the stems | fold into one accumulator with `smin` / `smax` |

A `## Sections` cell is therefore an **operator**, and row order is semantic. This is
the design decision everything else follows from; `SPEC.md` §8 has the algebra.

### 17.3 Why each pass is generated GLSL

VapourSynth offers `Expr`, `Convolution`, `AverageFrames`, `MaskedMerge`, `Deband`
and more. sdfshow uses only three filters - `BlankClip` as a frame carrier,
`placebo.Shader` per pass, `resize` at the end - and generates every effect as another
libplacebo hook.

The reason is that the alternative is a second effects language, with a second set of
colour-space rules and a picture that is half shader and half filter graph. Keeping
one language means one artifact to read (`gen/`), one place a bug lives, and `TIME0`
injected consistently into every pass. The trade is recorded in `SPEC.md` §17.

### 17.4 Why the clock is a frame index

`t = (frame + TIME0) / fps`, never wall-clock and never accumulated. That is what
makes a still at time *T* identical to the frame at *T* in a video, and a `--from`
clip identical to the same range of the full render. `TIME0` exists because a
libplacebo hook counts frames from zero per session, so a render starting at frame *N*
must be told its absolute offset. Break that and every seek silently replays the show
from zero.

### 17.5 Why determinism took two fixes

Claiming "a render is a pure function of the Markdown" required:

- **`-threads 1` on x264** - threaded rate control makes different decisions on
  identical input, so repeat renders differed by a few hundred bytes;
- **`-r 1` on vspipe** - parallel frame requests let the first frames of a run differ
  (~40 dB PSNR), which H.264 then propagated through the whole file.

The second was invisible from MP4 hashes alone; it was found by comparing Y4M
streams. See `SPEC.md` §11 for why `-r 1` is required and what it costs.

### 17.6 Package layout

| module | responsibility |
|--------|----------------|
| `md.py` | one Markdown reader: scalars, tables, escaped pipes, heading lookup |
| `clock.py` | bpm/bars/fps -> beat, bar, step, duration, frames |
| `show.py` | `show.md`: stage, fields order, materials, effects, folds, cells |
| `fields.py` | `fields.md`: globals, parameters, template substitution |
| `tracks.py` | track parsing, parameter-expression validation, track GLSL |
| `glsl.py` | shader assembly: prelude, scene, materials, camera, shading, effects; `assemble_2d` for `mode: 2d` |
| `textmask.py` | numpy SDF stroke font, wrap, fit, bubble panel and ink masks |
| `dialog.py` | `## Dialogue`, seating, bubble plan, flite speech |
| `render.py` | compile, pass chain, bubble compositing, VapourSynth script, vspipe/ffmpeg |
| `proc.py` | build lock, quiet subprocess execution |
| `config.py` | paths, stage defaults, effort and encode constants |
| `cli.py` | `compile`, `frame`, `render`, `clips`, `shows` |

---

## 18. Limits and pitfalls

- **GPU float is not portable.** Two vendors may produce slightly different pixels
  from the same shader. Within one machine and driver it is stable.
- **SDF composition is order-dependent.** The first active cell must be a union;
  after that, left-to-right order changes the result.
- **`smin` is not a metric.** A large blend radius distorts the field and can slow
  the march. Keep `k` small relative to the objects.
- **Overestimating kills surfaces.** If a template can return more than the true
  distance, the ray skips the surface. Use `shrink`.
- **No anti-aliasing.** Patterns and thin geometry can alias at a distance. The
  scanline pass hides some of it.
- **One camera, one accumulative field.** There is no per-object transform stack and
  no transparency; everything is one distance at a time.
- **Multi-pass is post only.** Effect passes read the finished picture and cannot
  change geometry, lighting or the field. Bloom therefore glows on the rendered
  image, not on emissive surfaces.
- **No reflections or refraction.** Shading is analytic: diffuse, specular, rim, AO,
  soft shadow, fog. There is no ray bounce and no glass.
- **No audio yet.** `audio:` is parsed but not muxed. Audio-reactive control will
  need a data channel into the shader, not new ffmpeg filters.
- **The fold applies to everything.** `fold` wraps every field, so a scene mixing a
  folded sculpture with an unfolded floor is not expressible; put the fold in a
  template if you need it locally.
- **Mandelbulb is expensive.** Six iterations multiply the per-sample cost inside a
  160-step march. It works, but it is not a default.
- **Fold applies to everything, and it interacts with templates.** `fold` wraps every
  field, so a template that repeats space internally (`pillars`, `spheres`, the tunnel)
  and a global kaleido fold multiply each other. A template that also rotates its own
  point out of the fold sector will appear to vanish as time advances; `spheres.glsl`
  documents the correct order.
- **A morph is not a topology change.** `m` cross-fades two distances and only reads
  correctly between concentric solids.
- **`#` at line start in a template is a Markdown comment**, so GLSL preprocessor
  directives cannot be written there. Template bodies do not need them.
- **Scalars are single tokens.** `fps: 30 # comment` is not a scalar line and will
  not be read; keep each value alone on its line.
- **Prose can look like a scalar.** Any line shaped like `word: token` is read as a
  scalar. A documentation line such as `step: 1` in `fields.md` is therefore treated
  as a redefinition of the clock and fails. Keep prose off the `key: value` shape,
  or move it outside the file.

---

## 19. Glossary

- **Bar** - four beats. **Beat** - `60/bpm` seconds. **Step** - a 16th note.
- **Cell** - one arrangement entry: a composition operator and optional blend
  radius.
- **Field** - one SDF instance: a template plus parameters, compiled to
  `float field_<name>(vec3 p, float t)`.
- **Hook** - the libplacebo fragment entry point, declared with `//!HOOK MAIN`.
- **libplacebo** - the GPU shader engine used by mpv and vs-placebo.
- **Material** - a field's base colour plus optional pattern and scale.
- **SDF** - signed distance field/function.
- **Section** - a bar range with one cell per field.
- **Show** - a folder with `show.md` and `fields.md`.
- **Template** - a GLSL function body in `fields/` with `{{placeholder}}` holes.
- **Track** - a named scalar function of time, compiled from a Markdown row.
- **vs-placebo** - the VapourSynth plugin that runs libplacebo shaders.
- **vspipe** - the VapourSynth command-line frame server.
- **Y4M** - YUV4MPEG2, the uncompressed stream vspipe writes to ffmpeg.

---

## Cheat sheet

```
shows/<show>/show.md     bpm, bars, fps, size, Stage, Fields, Materials,
                         Sections, Effects
shows/<show>/fields.md   globals, Fields (name/template/params), Tracks
fields/*.glsl            GLSL function bodies with {{placeholders}}

compile  -> gen/<show>/scene.glsl + fx_<n>_<name>.glsl + score.json
frame    -> output/<show>/frame_NNNNN.png
render   -> output/<show>/show.mp4 (versioned), logs/
clips    -> output/<show>/clips/scene_NN_bars_A-B.mp4 (one per section)

cells:   u   u<k>   s<k>   i<k>   m<w>   x
tracks:  steps (span, ease) | bars (ease) | keys (bar:value) | expr (GLSL over t)
folds:   none | mirror | kaleido (+ fold_count, may be a track)
effects: bloom | chroma | crt | glitch (knobs may be tracks)
clock:   t = (frame + TIME0)/FPS ; BAR, BEAT, STEP, DUR in seconds

checks:  pytest -q ; python tests/gpu_parity.py
```

If you get lost, read `SPEC.md` for the precise contract and `shows/first` for a
small complete example. Then change one number at a time.