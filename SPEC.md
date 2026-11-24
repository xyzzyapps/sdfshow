# SPEC.md - sdfshow (SRS)

Software requirements and architecture for **sdfshow**: signed-distance-field shows
authored as Markdown, compiled to a single GLSL shader, and rendered frame-exact
through VapourSynth. Two renderers share the same Markdown and clock: a raymarcher
(`mode: 3d`, the default) and a flat layer painter (`mode: 2d`, see section 10).
Version 0.1.0.

---

## 1. Purpose and scope

Produce a fixed-length, beat-clocked SDF animation from two Markdown files. The
author writes a tempo, a bar count, a camera, a set of distance-field templates and
an arrangement of bar ranges. The build compiles that into one shader and renders it.

In scope:

- a tempo/bar/step clock derived from `show.md`;
- a template language with mandatory placeholders (no defaults);
- a small, validated parameter-expression language over animation tracks;
- an order-dependent arrangement language for composing distance fields;
- a raymarched renderer with normals, ambient occlusion, soft shadows and fog;
- a flat 2D renderer that paints SDF layers back-to-front in screen space, with a
  screen-space camera (cuts to close-ups), optional pixel quantise and per-layer
  outlines (`mode: 2d`), and a show length that can be measured from the dialogue;
- speech bubbles drawn from a numpy SDF stroke font and composited as an overlay,
  with synthesized dialogue audio (`## Dialogue`);
- deterministic, seekable frames; versioned outputs; a build lock.

Out of scope for 0.1.0:

- audio-reactive control and music generation (a later milestone; see `TODO.md`);
  `## Dialogue` speech synthesis is in scope;
- a GUI, a real-time preview, mesh export, or PBR/pathtracing;
- arbitrary GLSL supplied by the user outside `fields/` (templates are function
  bodies, by design);
- shadow/reflection/refraction passes and path tracing;
- image-based post effects that need a temporal history (feedback, motion trails).

In scope for post-processing: a chain of generated pass shaders selected by a show's
`## Effects` table.

---

## 2. Glossary

- **Show** - a folder under `shows/<name>/` with `show.md` and `fields.md`.
- **Field** - one instance of an SDF template: a GLSL function
  `float field_<name>(vec3 p, float t)`.
- **Template** - a GLSL function body in `fields/<file>.glsl` with `{{key}}` holes.
- **Track** - a named scalar function of time, generated as `float track_<name>(t)`.
- **Section** - a bar range with one composition cell per field.
- **Cell** - a composition operator (`u`, `u<k>`, `s<k>`, `i<k>`, `x`).
- **Clock** - `beat`, `bar`, `step`, `dur` and `frames` derived from `bpm`, `bars`,
  `fps` and `size`.
- **Hook** - a libplacebo GLSL fragment stage, declared with `//!HOOK MAIN`.
- **Frame counter** - the `frame` value libplacebo supplies to a hook; it counts
  output frames from zero for each render session, not source frame indices.
- **Pass** - one libplacebo hook over the clip. Pass 0 is `scene.glsl`; each effect
  adds one more.
- **Fold** - `fold_space(p)`, a whole-scene repetition applied before every field.
- **Effect** - a generated post pass (`bloom`, `chroma`, `crt`, `glitch`).
- **2D mode** - `mode: 2d`, a second renderer: every field is a flat shape evaluated
  in screen space and the frame is painted back-to-front, like an SVG document.
- **Layer** - one field drawn in 2D mode. A layer is a single flat fill, so a face or
  a piece of furniture is several layers.
- **Bubble** - one dialogue line's text and panel, rasterised by `textmask.py` into
  two coverage masks and composited by VapourSynth after the SDF passes.

---

## 3. Clock model

From `show.md`. `bars` is a number, or `auto` to end the show on the last `## Dialogue`
bar (`ceil(max(line.hi))`):


```
beat  = 60 / bpm
bar   = 4 * beat
step  = beat / 4
dur   = bars * bar
frames = round(dur * fps)
```

The shader derives time only from the frame index:

```
t = (frame + TIME0) / FPS
```

`TIME0` is the absolute first frame of the render. It exists because a libplacebo
hook's `frame` counter starts at zero for every render session, even when
VapourSynth is asked to start at frame *N*. Without `TIME0`, a `--from 10` render
would replay the show from zero. With it, frame *N* is byte-identical whether it
comes from a full render or a range render.

Durations (seconds) are injected into templates as `{{beat}}`, `{{bar}}`,
`{{step}}`, `{{dur}}`, `{{frames}}`, `{{fps}}`, `{{w}}`, `{{h}}`. Index arithmetic
is written explicitly in the template or track: `floor(t / {{bar}})`.

---

## 4. Architecture and data flow

```
  shows/<s>/show.md            shows/<s>/fields.md            fields/*.glsl
      |                              |                              |
      |  show.py                     |  fields.py + tracks.py       |
      |  (clock, stage, order,       |  (globals, params, tracks,   |
      |   sections, materials)       |   template bodies)           |
      +--------------+---------------+------------------------------+
                     v
              glsl.py  assemble()
                     v
        gen/<s>/scene.glsl   +   gen/<s>/score.json
                     |
                     |  render.py  write_script()
                     v
        gen/<s>/render.vpy  (VapourSynth + core.placebo.Shader)
                     |
                     |  vspipe -c y4m -s A -e B
                     v
        ffmpeg -f yuv4mpegpipe -i - -c:v libx264 ...
                     v
        output/<s>/show.mp4  (versioned)  +  logs/{vspipe,ffmpeg}.log
```

There is no hidden state between stages. `scene.glsl` is a complete, standalone
artifact; you can read it, diff it, and reason about a shader compile error against
it.

With `## Dialogue`, two more stages sit between the shader chain and the encoder:
`dialog.overlay_plan` rasterises each line with `textmask.py` into `gen/<s>/bubbles/`,
and the generated script composites them with `std.MaskedMerge` (section 10.3). The
SDF shader never sees the type.

Module responsibilities:

| module | responsibility |
|--------|----------------|
| `config.py` | paths, stage defaults, encode constants, `unique_path` |
| `md.py` | one Markdown reader: scalars, tables, escaped pipes, `key/value` tables |
| `clock.py` | the clock and its tokens |
| `show.py` | `show.md` parsing, cells, sections, materials, effects, folds, validation |
| `tracks.py` | track parsing, parameter-expression validation, track GLSL |
| `fields.py` | `fields.md` parsing, template preprocessing and substitution, field GLSL |
| `glsl.py` | shader assembly: prelude, scene, materials, camera, shading, hook, effect passes; `assemble_2d` for `mode: 2d` |
| `textmask.py` | numpy SDF stroke font, word wrap, fit-to-width, bubble panel + tail + ink masks |
| `dialog.py` | `## Dialogue` parsing, per-speaker seating, bubble placement plan, flite TTS |
| `render.py` | compile, pass chain, bubble compositing, VapourSynth script generation, vspipe/ffmpeg |
| `proc.py` | exclusive build lock, quiet subprocess execution |
| `cli.py` | argument parsing and command dispatch (`compile`, `frame`, `render`, `clips`) |

---

## 5. Control surface A - `show.md`

Required scalars: `bpm`, `bars`, `fps`. `bars` is a number or `auto`; with `auto` it is
derived from the `## Dialogue` table as `ceil(max(line.hi))`, so the show stops where
the last line stops. Optional: `size` (`WxH`, default 1280x720), `audio` (a path,
reserved; not yet muxed into the render).

### 5.1 Stage

A `| key | value |` table. Values are numbers, `r|g|b` triples, track names, or
arithmetic over tracks and `t`.

| key | meaning | default |
|-----|---------|---------|
| `distance` | camera distance from target | `4.2` |
| `yaw` | orbit angle, radians | `0.6` |
| `pitch` | elevation, radians | `-0.18` |
| `fov` | focal length in the ray construction (larger = narrower) | `1.9` |
| `target` | look-at point, `x\|y\|z` | `0\|0\|0` |
| `fog` | exponential fog density | `0.03` |
| `exposure` | pre-tonemap gain | `1.1` |
| `background` | `r\|g\|b`, also the fog colour | `0.02\|0.025\|0.04` |
| `light` | key light direction, `x\|y\|z` | `0.6\|0.8\|0.5` |
| `scanlines` | screen pass: darken alternate pixel rows | `0` |
| `plasma` | screen pass: slow colour wash | `0` |
| `grain` | screen pass: per-pixel noise | `0.012` |
| `vignette` | screen pass: radial darkening | `0.22` |
| `hue` | rotate every material colour around grey | `0` |
| `fold` | space fold before every field: `none`, `mirror`, `kaleido` | `none` |
| `fold_count` | sectors for `fold: kaleido` (>= 2); may be a track | `6` |

`fold` is implemented as `vec3 fold_space(vec3 p, float t)`, called by `map_scene` and
by the material pass. `mirror` takes `abs` on x and z; `kaleido` folds the XZ angle
into one sector of `TAU/fold_count` and reflects it. `fold_count` is a GLSL
expression, so it may be a track (the ripple in `shows/reel`). An unknown mode fails
at parse time.

#### Stage keys for `mode: 2d`

These are read only by the 2D renderer; the camera, `light`, `fog` and `fold` keys are
ignored there because there is no march and no world space.

| key | meaning | default |
|-----|---------|---------|
| `mode` | renderer: `3d` (raymarch) or `2d` (flat layers) | `3d` |
| `pixel` | snap the sample to a grid of `pixel` device pixels; `1` disables it | `1` |
| `outline` | rim width around every layer, screen units; `0` disables it | `0` |
| `outline_color` | rim colour, `r\|g\|b` | `0.06\|0.05\|0.08` |
| `zoom` | screen-space camera: `1` is wide, `> 1` is a close-up | `1` |
| `focus_x` | scene x at the centre of the frame when zoomed | `0` |
| `focus_y` | scene y at the centre of the frame when zoomed | `0` |
| `font` | speech-bubble cap height as a fraction of frame height | `0.042` |
| `panel` | bubble padding as a multiple of the type size | `1.0` |
| `bubble` | speech presentation: `panel` (speech bubble) or `caption` (white type with a dark outline) | `panel` |

`pixel` and `outline` are ordinary stage values and may be tracks, so the pixel size
or the rim can animate. `font` and `panel` are deliberately independent: shrinking the
letters must not shrink the panel, or the bubble stops being readable. `background` is
the 2D clear colour and `vignette`, `scanlines`, `plasma`, `grain` and `hue` still run
in `post()`.

Camera basis:

```
ro     = target + distance * (cos(pitch)*sin(yaw), sin(pitch), cos(pitch)*cos(yaw))
ta     = normalize(target - ro)
right  = normalize(cross(ta, worldUp))
up     = cross(right, ta)
rd     = normalize(uv.x*right + uv.y*up + fov*ta)
```

### 5.2 Fields

`| field |` lists the composition order. It must equal the set of fields defined in
`fields.md`; a mismatch fails the build and names the missing/extra fields.

### 5.3 Materials

Optional `| field | color | pattern | scale |` table.

- `color` is `r|g|b` in linear space.
- `pattern` is `none`, `checker`, `grid` or `stripes` (default `none`).
- `scale` is the pattern frequency in world units (default `1`).
- Patterns are evaluated at the hit point: `checker` and `grid` use `p.xz`,
  `stripes` uses `p.y`. A pattern modulates the base colour; it does not change the
  distance.
- A field with no row receives a golden-angle hue at 55% saturation.

The Materials table is found by its `## Materials` heading, so an introductory
documentation table cannot be mistaken for data.

### 5.4 Sections

`| bars | <field> | ... |`. Rules (all enforced):

1. The first section starts at bar 0.
2. Each section starts where the previous one ended.
3. The last section ends at `bars`.
4. Every Fields entry has a cell in every section.
5. Every Sections column names a field in the Fields table.
6. The first active cell of a section is a union (`u` or `u<k>`); a morph cannot
   start a section because there is nothing to blend from.

Cells: `u`, `u<k>`, `s<k>`, `i<k>`, `m<w>`, `x`. A blank cell is `x`. `0` is
accepted as `x` for readability. The operand may be a number **or a track name**,
resolved through the same expression validator as field parameters, so a blend radius
or a morph weight can be animated. Generated code: `smin(d, f, k)`,
`smax(d, -f, k)`, `smax(d, f, k)`, `mix(d, f, clamp(w, 0.0, 1.0))`.

In `mode: 2d` a cell is a **visibility gate**, not an operator: a layer either paints
or it does not, because two flat fills cannot be min/maxed. `m<w>` degenerates to a
visibility test at `w > 0.5`. This is what lets one show hold two settings: both
furniture sets sit in the `Fields` table and only the active section's set is drawn.

`m` is a cross-fade between two distances, and the average of two distances is not a
distance, so it is only meaningful when both fields occupy the same space
(concentric solids). Documented as a limitation, not hidden.

### 5.5 Effects

An optional `## Effects` table (`| effect | key | value |`). Each distinct effect
name becomes one post pass, in **first-appearance order**; rows for the same effect
merge into one parameter set. A row with an empty `key` registers the effect with its
defaults.

| effect | parameters (defaults) |
|--------|-----------------------|
| `bloom` | `threshold` 0.55, `strength` 0.8, `radius` 2.0 |
| `chroma` | `amount` 0.05 |
| `crt` | `curvature` 0.12 |
| `glitch` | `amount` 0.06, `rate` 9.0, `chance` 0.08 |

Generated per pass: `gen/<show>/fx_<n>_<name>.glsl`, a complete `//!HOOK MAIN`
shader that samples the previous pass through `HOOKED_tex`. Each carries the
`// @TIME0@` sentinel and the clock defines, so animated effects stay seekable. A
parameter value may be a **track name**; the pass emits the track functions it needs.
An unknown effect name or an unknown identifier fails at parse time.

---

## 6. Control surface B - `fields.md`

### 6.1 Globals

Top-level `key: value` scalars. They may reference the injected clock tokens and one
another via `{{key}}`. Redefining `bar`, `beat`, `step`, `dur`, `frames`, `fps`, `w`
or `h` is an error: those come from `show.md`.

### 6.2 Fields

`| name | template | parameters |`.

- `name` must match `[A-Za-z_][A-Za-z0-9_]*` and be unique.
- `template` names a file in `fields/`.
- `parameters` is `key=value, key=value`. Commas inside parentheses do not split
  (`b=min(1, 2)` is one value).
- Each value is resolved in this order: `{{key}}` expansion against globals and
  clock tokens, then parameter-expression validation and track substitution.
- A value that is not a number must tokenise entirely into numbers, track names,
  `t`, `PI`, `TAU`, and a whitelist of GLSL math functions. Anything else raises,
  naming the identifier and the value.

### 6.3 Tracks

`| name | kind | values | options |` (the fourth column is optional).

| kind | values | options |
|------|--------|---------|
| `steps` | `\|`-separated numbers | `span=<bars>` (default 1), `ease=none\|smooth` |
| `bars` | `\|`-separated numbers | `ease=none\|smooth` |
| `keys` | `bar:value\|bar:value` | `ease=none\|smooth` |
| `expr` | one GLSL expression over `t` | none |

Track names are unique and become `track_<name>`. `expr` is the escape hatch: its
contents are not token-validated (it may use any GLSL expression).

A `## Tracks` table may live in **either** `show.md` or `fields.md`; both are read and
merged, and a name defined in both is an error. Camera and effect tracks therefore sit
next to the Stage table they feed, and field tracks next to the fields they drive.
Tracks are emitted after the prelude and before `fold_space`, because a fold count or
a camera value may reference one.

---

## 7. Template language

A template is a GLSL **function body**:

```
float field_<name>(vec3 p, float t) {
    <template>
}
```

Preprocessing, in order:

1. Read the file as UTF-8.
2. Remove `//` comments from each line (so a comment can never swallow the next
   line once lines are joined).
3. Drop blank lines and lines whose first non-space character is `#`.
4. Join the remaining lines with a single space.
5. Substitute `{{key}}` from the resolved value map.

Constraints:

- Must contain `return`.
- Must not leave a `{{...}}` placeholder after substitution.
- A line must not split a token.
- Use `//` for GLSL comments; `#` at line start is a Markdown comment (so a GLSL
  preprocessor directive cannot be written at line start).

Available helpers (prepended by the assembler): `PI`, `TAU`, `BAR`, `BEAT`, `STEP`,
`DUR`, `FPS`, `FRAMES`, `rot2`, `rotX`, `rotY`, `rotZ`, `smin`, `smax`, `hash11`,
`hash21`, `apply_pattern`, `hue_rotate`.

Each field's parameter set is exactly the placeholders it uses; unused parameters
are allowed but not reported.

---

## 8. Arrangement semantics

Audio mixing is linear; distance-field composition is not. The arrangement is
therefore a sequence of operations on one accumulator `d`:

```
u<k>   d = smin(d, f, k)
s<k>   d = smax(d, -f, k)
i<k>   d = smax(d, f, k)
x      skip
```

`smin` is the polynomial smooth minimum; `smax(a,b,k) = -smin(-a,-b,k)`.
`k = 0` degenerates to `min`/`max`.

Each section is emitted as a nested `if`/`else if` over `t`, with the last section
as `else`. Time is uniform across the frame, so this branch is coherent.

The material pass (`mat_id`) re-evaluates only the **union** fields at the hit point
and returns the index of the nearest one. This doubles the field cost at the hit
point only, not during marching. It receives the folded point
(`fold_space(p)`), so a folded scene keeps consistent material boundaries.

### 8.1 Space folds

`fold_space(p)` is called at the top of `map_scene` and in the material pass:

```
none      p
mirror    (abs(p.x), p.y, abs(p.z))
kaleido   angle folded into TAU/fold_count, reflected, radius preserved
```

A fold is geometry-agnostic: it multiplies every field, so it must be applied in
both passes or the material ids would disagree with the distance.

---

## 9. Generated shader

Structure, in order:

1. `//!HOOK MAIN`, `//!BIND HOOKED`, `//!DESC <show>`, and the `// @TIME0@` sentinel.
2. Defines: `FPS`, `BAR`, `BEAT`, `STEP`, `DUR`, `FRAMES`, `PI`, `TAU`, and
   `TIME0` (0 unless the render starts later).
3. Helpers: `smin`, `smax`, hashes, rotations, `apply_pattern`, `hue_rotate`,
   `hash13`, `vnoise`, `fbm`, and the generated `fold_space`.
4. Generated track functions and field functions.
5. `map_scene` (which begins with `p = fold_space(p)`), `mat_id`, `mat_color`.
6. `camera_target`, `camera_position`, `camera_ray`.
7. `calc_normal` (tetrahedron), `calc_ao`, `soft_shadow`, `post`, `render`.
8. `hook()`.

`mat_color(int id, vec3 p, float t)` looks up the base colour, applies the field's
pattern, then applies the hue rotation. `post(col, uv, screen, t)` applies vignette,
scanlines, plasma and returns the screen-space result; grain is added in `hook()`.

`hook()`:

```
vec2 uv = (HOOKED_pos * target_size - 0.5*target_size) / target_size.y;
uv.y = -uv.y;              // texture rows are top-down
float t = (float(frame) + TIME0) / FPS;
```

The `uv.y` flip is required: libplacebo's texture coordinates run top-down, so
without it the world's up axis renders down.

Shading: one key light, Lambert diffuse, 24-step soft shadow, 5-tap AO, rim term,
Blinn-Phong specular, exponential fog, Reinhard tonemap and gamma 2.2.

The march loop refuses to start inside geometry: if `map_scene` returns a negative
distance at the ray origin it breaks and leaves the background. Starting inside a
solid would otherwise step backwards and produce an unexplained empty frame.

Hard-coded effort constants live in `config.py`: `MARCH_STEPS=160`, `AO_STEPS=5`,
`SHADOW_STEPS=24`, `SURFACE_EPS=0.0012`.

With `mode: 2d`, items 4 and 6-7 of that list are replaced: there is no `map_scene`
march, no camera, no normal and no shadow. The 2D scene is `render_2d(uv, t)`; see
section 10.

---

## 10. The 2D renderer (`mode: 2d`)

### 10.1 Layer model

`mode: 2d` is a second renderer behind the same Markdown. Every field is evaluated in
**screen space**, not world space: `cx`/`cy` are frame offsets divided by frame
height, so `y = 0` is the vertical centre, `y = -0.5` the bottom edge, `y = 0.5` the
top, and `x` runs about `-0.89..0.89` at 16:9. A 2D template returns a signed
distance in those units and nothing else - no solid, no material point.

The frame is painted back-to-front with the painter's algorithm:

```
col = background
for each layer, in Fields order:
    if the current section draws it:
        d = layer(p)
        if d < -outline:  col = colour              # inside
        elif d < 0:       col = mix(outline, colour) # rim, antialiased by smoothstep
```

So the `Fields` table reads top-to-bottom as a **z-stack**, exactly like the document
order of an SVG. The first row is furthest back. `Sections` decides which rows are
drawn; a cell of `x` means the layer is absent.

A layer is one flat fill, which is the central constraint of this mode: a figure cannot
be drawn as one shape with painted features, because there is no shading and no
texture. A figure is therefore **several layers** - trousers, shirt, arms and hands,
head, hair, sclera, pupils, mouth - each with its own colour and its own row in the
table. The same applies to furniture
(a window is a pane plus a frame). It is also how a cutout face is actually drawn:
white sclera, dark pupils, a dark mouth, each a shape rather than a shade.

Each layer is a single distance evaluation, so the picture costs one shape test per
layer per pixel. `pixel` can snap the sample coordinate to a device grid before any
layer is evaluated (the earlier pixel-art look); the shipped show leaves it at `1`.
`outline` rims every layer. Both are stage values and may be tracks.

### 10.2 Generated 2D shader

`glsl.assemble_2d` emits one `render_2d(vec2 uv, float t)`:

- a `vec3 c[N]` array of resolved material colours, one per field, in `Fields` order;
- one `if`/`else if` branch per section, keyed on `t < <hi * bar>`, so the section
  chain is a compile-time ladder over bar ranges;
- inside each branch, one guarded paint block per field, in order, using the same
  `_cell_gate` visibility rule as the rest of the build;
- a screen-space camera applied before any layer is evaluated.

The camera has no march to move, so a shot is a uniform scale of the same stack:

```
z     = max(zoom, 0.2)
focus = (focus_x, focus_y)
p2    = focus + uv / z
```

`p2` is the scene point sampled at output pixel `uv`, so `focus` sits at the centre
of the frame and `z > 1` magnifies. Each layer returns a distance in pushed-in units,
so the emitted code multiplies it by `z` before comparing with `outline`; the rim then
keeps a constant width on screen at any zoom. `zoom`, `focus_x` and `focus_y` may be
`cuts` tracks, which is how a show cuts wide -> close -> close -> wide on bar
boundaries.

The section chain opens one branch per section and closes once at the end. Emitting
the close per block leaves the last branch dangling and the shader does not compile;
that is why the closing brace is written by the wrapper, not by the block loop.

`post()` and `hook()` are shared with 3D mode: the pixel grid is applied to `uv`
before `render_2d`, then vignette, scanlines, plasma and grain run as usual.

### 10.3 Text, dialogue and audio

Text is never part of the shader. `textmask.py` evaluates a stroke font as SDF capsule
chains in numpy, producing two coverage masks per line: the **panel** (rounded
rectangle plus a tail) and the **ink** (the letters, slightly proud of the panel so
they can be composited separately).

Sizing has two independent knobs, both stage keys:

- `font` - cap height as a fraction of frame height. The line's pixel cap height is
  `round(height * font)`, clamped to at least 8 px.
- `panel` - padding as a multiple of the type size, passed to `bubble(panel_scale=...)`.

`text_mask` sizes its canvas and places its first baseline from the same numbers
(`baseline0 = cap * (1 + pad)`, canvas height `baseline0 + row*(lines-1) + cap*pad`),
so the top row of the first line can never be clipped. A canvas sized from
`row * lines + cap * 2 * pad` while placing the baseline at `(1 - pad) * cap` is the
bug this replaced: it reserved the padding once at the bottom and then moved the text
*up* into it.

`## Dialogue` drives bubbles and speech from one table. Each line names a speaker,
a bar range, the text and a flite voice. `dialog.py`:

1. reads the speaker's `cx` from `fields.md`, so the panel is centred over the person
   who is talking, even with four of them;
2. applies the same camera the shader uses at the line's first bar: the speaker's
   screen x is `(cx - focus_x) * zoom`, so a close-up moves the panel with the head;
3. points the tail at that screen x by passing it as a fraction of the panel width,
   clamped away from the corners; the tail is a wide, short triangle, not a spike;
4. seats the panel high in the frame, inside the frame width;
5. synthesizes the line with ffmpeg's `flite` filter and mixes it at its bar. The
   voice cell may carry a pitch factor (`slt*0.92`), applied with rubberband, so
   two characters can share the single female voice a stock flite build ships
   without sounding identical.

Lines longer than `MAX_CHARS` (48) fail at parse time, because a bubble that has to
shrink below the font budget stops being readable.

Compositing happens after the SDF passes and after the first `RGBS` conversion.
`std.MaskedMerge` is the primitive in this build (there is no `std.Overlay`). For each
line the script builds a constant RGB frame for the panel and ink, a `GRAYS` mask that
equals the panel's coverage inside the line's frame window and zero outside, and merges
it. Loop closures bind the mask through a factory (`make_alpha`), not by late binding,
or every bubble would show the last line's mask.

With `bubble: caption`, the panel is replaced by a SCUMM-style caption. The ink mask is
dilated by two pixels to make a dark outline mask; the renderer paints white inside the
ink and near-black inside the ring, and the caption is centred at the top of the frame
with no tail. `shows/island` uses it.

Fonts and bubbles are orthogonal to the renderer: bubbles work the same way over a
raymarched 3D show.

### 10.5 Raster actors

Sets stay SDF; actors may be raster. A `## Sprites` table names a sheet, a cell, a bar
window, a frame and a feet anchor. At render time each row is rasterised into a full-frame
RGB plate and an alpha plate (`gen/<show>/sprites/*.npy`); the generated script picks the
last plate whose window contains the frame and composites it with `MaskedMerge` after the
SDF passes and before the captions. Rows for one id repeat over windows, so an idle row plus a talking row is an animation.
A row may also carry `flip` and `cycle`/`alt`: flip mirrors the plate, and cycle flips
between the row's frame and the alternate every N frames - the lip flap and the walk-in.
The camera is static for sprites in this version.

### 10.4 What 2D mode does not do

- No 3D camera: `zoom`/`focus_*` are a uniform scale, not perspective. Normals, fog,
  shadows and `fold` are likewise ignored.
- No smooth union (`u<k>` behaves as `u`), subtraction or intersection: a layer is
  either drawn or not.
- No depth sorting within one section beyond table order; overlapping layers are
  resolved only by the z-stack.
- No tonemap and no gamma: material colours are the literal output colours, so a
  palette can be specified exactly. `exposure` is therefore ignored in 2D.
- No textures or sprites; every visual is an SDF shape.

---

## 11. Renderer

`render.py` generates a VapourSynth script that chains every pass:

```python
PASSES = [scene, fx_1_bloom, fx_2_chroma, ...]

def shade(clip, path):
    with open(path, encoding="utf-8") as fh:
        src = fh.read().replace("// @TIME0@", "#define TIME0 {offset}")
    return core.placebo.Shader(clip, shader_s=src, width=W, height=H,
                              sigmoidize=False, linearize=False, matrix=5)

clip = core.std.BlankClip(W, H, format=vs.YUV444P16, length=NF, fpsnum=FPS)
for path in PASSES:
    clip = shade(clip, path)
clip = core.resize.Bicubic(clip, format=vs.YUV420P8, matrix_in_s="470bg",
                           matrix_s="470bg", range_in_s="limited", range_s="limited")
```

Pass 0 is `scene.glsl`; each effect adds one call over the previous clip. Nothing is
converted between passes: the chain stays `YUV444P16` until the final resize.

If the show has `## Dialogue`, the chain then converts once to `RGBS` and composites
one `std.MaskedMerge` per line (section 10.3), before the final `YUV420P8` resize. A
3D show gets the same treatment, so text never enters the raymarch.

`vs-placebo` requires `YUVxxxP16` input; the blank clip is only a frame carrier,
because the scene shader ignores `HOOKED_tex` entirely (effect passes read it).

The script rewrites the `// @TIME0@` sentinel in **every** pass with the render's
first frame, so the scene clock and animated effects agree. The shader sources stay
identical across renders.

Encoding:

```
vspipe -r 1 -c y4m -s A -e B gen/<s>/render.vpy -
  | ffmpeg -f yuv4mpegpipe -i - [-i audio] -c:v libx264 -preset slow -crf 18
           -pix_fmt yuv420p -threads 1 -movflags +faststart output/<s>/show.mp4
```

`-threads 1` is deliberate. With threaded rate control, x264 can make different
decisions on identical input, so two renders of the same show would differ by a few
hundred bytes. Single-threaded x264 makes the encoded file byte-identical.

`-r 1` is the second half of the same guarantee. With the default parallel frame
requests, the first one or two frames of a run could differ from a repeat run: a GPU
dispatch ordering effect, visible as a ~40 dB PSNR difference on frames 0-1 and then
propagated through H.264. Serialising requests makes the Y4M stream byte-identical;
measured cost on this machine is under 5% for the demo.

ffmpeg is used only as an encoder/muxer. No ffmpeg filter touches the picture: all
geometry and shading are the generated GLSL.

Stills use the same path with `-s F -e F -frames:v 1 -update 1` to write a PNG.
Ranges are half-open: `--from A --to B` encodes frames
`frame_at(A) .. frame_limit(B) - 1`, so `--to 5` is exactly five seconds.

---

## 12. Outputs, versioning, locking

- `gen/<show>/scene.glsl` is generated; `fields/` is the source of truth.
- `gen/<show>/fx_<n>_<name>.glsl` - one file per effect pass, in order.
- `gen/<show>/score.json` records the resolved clock, effects, sections and cells for
  audits.
- `gen/<show>/render.vpy` and `still.vpy` - the generated VapourSynth scripts.
- `gen/<show>/bubbles/NN_panel.npy`, `NN_ink.npy` - one pair of coverage masks per
  dialogue line.
- `output/<show>/show.mp4`, `frame_NNNNN.png`, `clips/scene_NN_bars_A-B.mp4`; if a
  target exists, `_v2`, `_v3`, ...
- `output/<show>/logs/{vspipe,ffmpeg}.log` capture stderr; `logs/dialogue.wav` is the
  synthesized speech track when `## Dialogue` is present.
- `output/<show>/logs/.build.lock` (created with `O_EXCL`) prevents concurrent
  builds of the same show.

---

## 13. Verification and acceptance

Automated (`pytest`):

- clock arithmetic and clamping;
- Markdown tables, escaped pipes and `key/value` tables;
- every composition cell form, section coverage, the first-active-union rule, and
  materials;
- track parsing and codegen for all four kinds;
- parameter expansion, unknown-identifier failure, and missing-placeholder failure;
- `split_params` ignoring commas inside calls;
- `table_after` ignoring a documentation table before a heading;
- material colour, pattern and scale parsing, and an unknown pattern failing;
- the demo show assembling all six fields into one balanced shader;
- the pattern array, `post()` pass and scanline constant reaching the generated
  source;
- effect parsing: first-appearance order, parameter merging, unknown effect failing;
- fold parsing and generated `fold_space` for `mirror` and `kaleido`;
- every effect pass being a valid `//!HOOK MAIN` shader with its knobs baked in;
- the generated script chaining passes over `YUV444P16` with one `TIME0`;
- 2D mode: `render_2d` is emitted instead of a march, layer order follows `Fields`,
  and a section cell of `x` removes the layer's paint block;
- duration: `bars: auto` equals the last dialogue bar, fails without a Dialogue table,
  and a numeric `bars` shorter than a line fails by name;
- sprites: a `## Sprites` row parses into a placement, a missing sheet fails by name, and
  a sheet resolves relative to the show folder or the repo root;
- bubble masks: `wrap`/`fit` never exceed the line budget, `text_mask` places its
  first baseline inside the canvas (the clipping regression), `panel` scales the
  padding without changing the ink, and a tail lands on the requested side;
- captions: the outline mask contains the ink and stays close to it, i.e. it is a rim
  rather than a panel.

Manual / GPU (`tests/gpu_parity.py`, run via `task parity`):

- the generated torus body of `shows/ring` is evaluated on 256 sample points at
  16-bit precision and compared against an independent Python torus; the maximum
  absolute error must stay under 0.01 (currently 0.0076).

Manual / visual:

- `python -m sdfshow frame --show first --at 5` shows the sphere, the ring and the
  wavy floor;
- `python -m sdfshow frame --show demo --at 2` shows the ring tunnel;
- `shows/ring` is the single-field probe;
- `shows/ops` shows `s` and `i` (bars 1-2 subtract, 2-4 intersect) and a `span=2`
  steps track;
- `shows/post` shows all four effect passes at once;
- `python -m sdfshow frame --show pixel --at 4` shows the diner with two people and
  the cup clear of them; `--at 20` shows the living room with the sofa, lamp and four
  characters, i.e. the same show in two settings;
- `python -m sdfshow frame --show diner --at 3` shows the raymarched booth, and a
  frame after a `cuts` key shows the camera has moved to another shot;
- `shows/pixel` alternates a wide shot and a close-up on the speaker at every line
  boundary; the mouth is visibly open mid-line and a closed line between lines, and
  each tail points at the head of the character who is speaking;
- the 50 s `shows/pixel` render has dialogue audio at every spoken bar range and no
  bubble clipped at the top of its panel;
- a still rendered via `--at` must equal the corresponding frame of the full video
  when both are decoded to the same colour space (verified at 44 dB PSNR after
  H.264, i.e. compression-only difference);
- a `--from`/`--to` render must equal the same frame range of the full render;
- two full renders must be byte-identical (verified by file hash, with `-threads 1`
  on x264 and `-r 1` on vspipe). This was found to be false before `-r 1`: the first
  one or two Y4M frames could differ between runs (about 40 dB PSNR on frames 0-1),
  which H.264 then propagated. Both plain and effect-pass shows are now verified
  byte-identical.
- a repeat `compile` must be byte-identical.

---

## 14. Extension guide

### Add a field template

1. Create `fields/<name>.glsl` returning a distance.
2. Add a `{{placeholder}}` for every knob.
3. Add a row to a show's `## Fields` table with values for each placeholder.
4. `compile`, then `frame` at a time where the field is active.

### Add a 2D template

1. Create `fields/<name>2d.glsl` returning a distance in **screen units** (frame
   height = 1), with `{{cx}}`, `{{cy}}` and a `{{s}}` scale.
2. Remember the layer is one flat fill: a shape that needs two colours is two
   templates, or two rows in the same table.
3. Keep the body free of `time`-named locals - a template local called `t` shadows the
   shader's `t` and the shader will not compile.
4. Add the row to a show's `## Fields` table, and a cell in every `Sections` row.
5. `compile`, then `frame` at a bar where the row is active.

### Add a track kind

1. Add the kind to `KINDS` in `tracks.py`.
2. Parse its values in `_make`.
3. Emit `float track_<name>(float t)` in `glsl()` / a `_glsl_*` helper.
4. Add a codegen test.

### Add a stage knob

1. Add a default to `config.STAGE_DEFAULTS`.
2. Consume it in `glsl.assemble` (with `_motion` if it may be a track).
3. Document it in this file and the README.

### Add a surface pattern

1. Add the name to `PATTERNS` in `show.py` (its index is the shader's id).
2. Add the modulation branch in `glsl._PATTERN`.
3. Test the parse and the generated branch.

### Add an arrangement operator

1. Extend `_CELL` and `Cell` in `show.py`.
2. Add the emission branch in `glsl._section_chain`.
3. Decide whether it is legal as a first active cell.
4. Add a test for the codegen.

### Add an effect pass

1. Add the name to `config.EFFECTS` and its defaults to `glsl._EFFECT_DEFAULTS`.
2. Add a branch in `glsl.assemble_effect` returning the `hook()` body.
3. Use `_effect_num(name, params, key)` for every knob, so values are validated.
4. Add it to a show's `## Effects` table and check the generated
   `gen/<show>/fx_<n>_<name>.glsl`.
5. Test that the pass is a `//!HOOK MAIN` shader with its knobs baked in.

### Add a fold

1. Add the mode to the validation list in `show.parse`.
2. Add a branch in `glsl._fold` returning a `vec3 fold_space(vec3 p)`.
3. Remember the fold must remain valid in the material pass too.

---

## 15. Risks and limitations

- **No bit-exactness across GPUs.** GLSL transcendental functions differ by vendor.
  Within one driver a render is stable. Cross-machine comparisons need a tolerance.
- **Approximate distances.** Templates such as `plane_wave` return a scaled estimate
  (`shrink` < 1). A template that *over*-estimates makes the raymarcher step through
  surfaces. This is a template-authoring risk, not a codegen one.
- **Smooth-min distorts the field.** `smin` is not a true distance. Large blend
  radii (`k` comparable to feature size) can create shading artefacts and make the
  marcher take smaller steps.
- **Template library size.** ffmpeg offers hundreds of ready filters; GLSL offers
  nothing. The library in `fields/` is the main authoring cost of the project.
- **No reflections or refraction.** Shading is analytic: diffuse, specular, rim, AO,
  soft shadow, fog. There is no ray bounce and no glass.
- **Multi-pass is post only.** Effect passes read the finished picture; they cannot
  change geometry, lighting or emission. Bloom glows on the rendered image, not on
  emissive surfaces.
- **Effect cost is linear in passes.** Each pass is a full-screen GPU dispatch. The
  demo (bloom + chroma + glitch) went from about 21 fps to 13 fps of wall time.
- **The fold is global.** `fold` applies to every field, so a folded object and an
  unfolded floor cannot coexist in one show. Put the fold in a template for a local
  one.
- **Mandelbulb is expensive.** Six iterations multiply the per-sample cost inside a
  160-step march.
- **`audio:` is parsed but not muxed.** Only `## Dialogue` produces a muxed track
  (flite speech, placed by bar). Audio-reactive control still needs a data channel
  into the shader (a sampled envelope baked into the shader, or the frame-strip idiom
  used by fftechno).
- **Shader compile errors are reported with prelude line numbers.** `scene.glsl` is
  prepended with ~80 lines by libplacebo; subtract them when reading an error.
- **`#` comments.** A template cannot start a line with a GLSL preprocessor
  directive. If that is ever needed, the preprocessor rule must change.
- **Camera inside a solid.** The march loop detects a negative starting distance and
  renders the background. That is a clean failure, not a fix: move the camera or the
  geometry. Large camera distances with a downward pitch are the usual cause.
- **Pattern aliasing.** `checker` and `grid` have hard edges and alias in the
  distance; the scanline pass hides some of it, but there is no derivative-based
  anti-aliasing yet.
- **2D mode has no depth.** Layer order is table order, so two shapes in the same
  section cannot interleave; a character behind a table must be listed behind it.
- **The 2D camera has no parallax.** A close-up is a uniform scale, so the background
  grows with the subject. That is the cutout look, not a perspective shot; a real
  perspective would need per-layer depths.
- **2D mode has no operators.** `u<k>`, `s<k>` and `i<k>` lose their meaning: a layer
  paints or it does not. Cross-fades (`m`) degrade to a visibility test at `w > 0.5`.
- **A 2D figure is many layers.** Ten rows per character - trousers, neck, shirt, arms
  and hands, head, hair, sclera, pupils, mouth - and each row needs a colour and a cell
  in every section. That is the cost of one fill per layer, and why the Sections table is
  wide.
- **Bubble text is capped at 48 characters.** Longer lines fail at parse time; there
  is no automatic reflow across two bubbles.
- **flite voices are robotic.** They are legible and deterministic, which is enough
  for timing, but they are not voice acting.

---

## 16. File inventory

| path | tracked | purpose |
|------|---------|---------|
| `sdfshow/*.py` | yes | the package |
| `fields/*.glsl` | yes | template library (3D bodies and `*2d.glsl` flat layers) |
| `fields/README.md` | yes | template-language guide |
| `shows/pixel/{show,fields}.md` | yes | 2D cutout show: diner then living room, four characters, close-ups, dialogue |
| `shows/island/{show,fields}.md` | yes | second 2D demo: SDF night set, sprite actors, caption dialogue |
| `assets/sprites/*.png` | yes | cleaned RGBA sprite strips for `shows/island` |
| `tools/prep_sprites.py` | yes | turn a baked-checker sheet into transparent sprite strips |
| `shows/diner/{show,fields}.md` | yes | 3D animation: booth, two people, cut-track camera, dialogue |
| `shows/first/{show,fields}.md` | yes | worked example |
| `shows/reel/{show,fields}.md` | yes | 30 s reel: five scenes, morphs, fold ripple, effect chain |
| `shows/demo/{show,fields}.md` | yes | demoscene set (tunnel, Menger, gyroid, sun, columns) |
| `shows/ops/{show,fields}.md` | yes | subtract/intersect operators, `span=2` steps |
| `shows/post/{show,fields}.md` | yes | all four effect passes on one sphere |
| `shows/ring/{show,fields}.md` | yes | one-field probe |
| `tests/*.py` | yes | pytest suite |
| `tests/gpu_parity.py` | yes | manual GPU check: generated field vs Python reference |
| `gen/<show>/*` | no | generated shader + score |
| `output/<show>/*` | no | renders, stills, logs |
| `SPEC.md`, `README.md`, `TUTORIAL.md`, `TODO.md` | yes | documentation |
| `Taskfile.yml`, `pyproject.toml` | yes | tooling |

---

## 17. Design decisions and rejected alternatives

**Port of the fftechno notion, not its code.** Stories are folders of Markdown,
templates carry mandatory placeholders, the build fails loudly, renders are
versioned. No code or dependency is shared.

**VapourSynth instead of a bespoke GL host.** The rendering path was already proven
on this machine (`core.placebo.Shader` on a `YUV444P16` blank clip). It gives GPU
raymarching with no window, no GL context management and no additional runtime. A
ModernGL host is the alternative; it buys real uniforms at the cost of a second
renderer. Deferred.

**ffmpeg encodes only.** Earlier ffmpeg-centric designs risked expressing geometry
as filters (`geq`, `frei0r`). Distance fields need loops and a `map` function, which
filters cannot express. Geometry lives in GLSL; ffmpeg receives Y4M and writes
H.264.

**No `if_steps` ladder.** The obvious port of the audio project's
`if(eq(step,0),...)` macro is a deeply nested conditional per pixel. Here, time is
uniform across the frame, so the arrangement compiles to a nested `if` on `t` and
tracks compile to small const arrays. This keeps the shader small and coherent.

**Cells are operators, not gains.** Audio sections multiply amplitude; geometry
cannot. `u/s/i/x` with an optional blend radius is the smallest language that keeps
the "arrangement table" feel while being correct for distance fields.

**A tiny expression language, not a general one.** Parameter values accept numbers,
track names and arithmetic over a fixed whitelist. This is enough for
`0.62*pulse`, `0.10*sin(t*0.7)` and camera moves, and it rejects typos by name. A
real parser would add power without adding clarity; raw GLSL remains available via
`expr` tracks and via templates.

**Materials are a separate table.** Putting `color` in the geometry parameters
would make parameter values sometimes vectors, sometimes scalars, and would force
the expression validator to special-case them. `## Materials` keeps geometry and
appearance separate, and gave the pattern/scale columns a natural home.

**Demoscene kit as templates, not a new subsystem.** A tunnel, a Menger sponge, a
gyroid and a colonnade are ordinary template bodies. They need no engine feature
beyond what a sphere needs, apart from two implementation notes: the tunnel
evaluates the two nearest ring planes so domain repetition stays a valid bound, and
the colonnade uses polar repetition to keep the centre clear. The CRT look is a
screen-space `post()` pass driven by the Stage table, so no ffmpeg filter is
involved and the effect is reproducible frame by frame.

**Heading-based table lookup.** `## Sections`, `## Materials` and `## Effects` are
located by their headings. Before this, a prose table in a show's introduction that
happened to start with `bars` was parsed as an arrangement. Data tables and
documentation tables now cannot collide.

**Effect passes are generated GLSL, not VapourSynth filters.** VapourSynth offers
`Expr`, `Convolution`, `AverageFrames`, `MaskedMerge`, `Deband` and more. Using them
would mean a second effects language, a second set of colour-space rules, and a
picture that is half shader and half filter graph. Instead each effect is another
generated `//!HOOK MAIN` shader chained over the previous clip. The graph stays three
filters wide (`BlankClip`, `Shader`, `resize`), every pass is inspectable in `gen/`,
and `TIME0` is injected into all of them so the chain stays seekable. `Deband` and
`AverageFrames` remain noted in `TODO.md` as optional, not adopted.

**Fold as a stage key, not a template parameter.** `fold_space(p)` sits in front of
every field, in both the distance and the material pass. That gives a whole-scene
kaleidoscope for one line of Markdown. The cost is that a fold cannot be applied to
one object only, which is documented as a limitation rather than hidden.

**Morph is a cross-fade, not a topology change.** `m<w>` emits `mix(d, f, w)`. That
is the cheapest possible morph and it is honest about its limit: the average of two
distances is not a distance, so it only looks right when both fields occupy the same
space. A real shape morph needs a correspondence between surfaces, which is a much
larger feature. The reel uses `m` for concentric solids and a hard section boundary for
scene changes, and the documentation says so.

**One order-of-operations trap worth recording.** In `fields/spheres.glsl` the sample
point is folded into an angular sector *before* the sphere is evaluated, and the spin
is applied to the resulting point. Rotating first and folding second makes the sphere
drift out of the sector as time advances, so the object silently leaves the view. That
ordering bug cost several iterations to find; the template now documents it.

**2D mode is a second renderer, not a flag on the first.** A flat show has no camera,
no normals and no march, so pretending it shares the 3D scene would mean a shader full
of dead branches per pixel. Instead `glsl.assemble_2d` emits a different entry point
(`render_2d`) while everything above it - the clock, the Markdown reader, the template
preprocessor, the track compiler, the effects chain and the renderer - stays shared.
The mode is a Stage key so a show states which renderer it wants in one line.

**Painter's algorithm over distance fields.** Given that a 2D layer is a flat fill,
the cheapest correct compositor is "draw back to front, overwrite". That makes the
`Fields` table a z-stack, reuses the existing arrangement table as a visibility table,
and costs one distance evaluation per layer per pixel. The alternative - depth tests
between layers - would need a depth per layer, a second value out of every template,
and a sort; it buys nothing a table order cannot express.

**One fill per layer, therefore many layers per figure.** A cutout figure is
`legs + neck + body + arms + head + hair + sclera + pupils + mouth`, ten rows. That looks
verbose next to a 3D figure, which is one field with shading, but it is the same trade
the format makes everywhere: the picture is a table, and every entry is inspectable. The
alternative - a template that returns a colour per pixel - would turn templates into
mini-shaders and lose the single-return contract that makes them cheap to write and to
test.

**An adventure scene is an homage, not a copy.** `shows/island` borrows the grammar of a
1990s pixel-art adventure - a night cliff above the sea, a stone arch, a campfire between
two figures, the spoken line in white type at the top - but not its art, characters or
script. The caption style is a renderer feature (`bubble: caption`), not a screenshot.

**The show length can be the dialogue length.** `bars: auto` measures the last line and
sets the clock from it. A trailer or an outro is a numeric `bars`; a dialogue scene
should not make the author count bars and then keep the number in step by hand.

**Close-ups are a zoom on the same stack, not a second scene.** A 2D show has no
camera to move, but a sitcom is cut in shots. `zoom`/`focus_x`/`focus_y` scale and
centre the whole layer stack, emitted as one line before any layer is evaluated, and a
`cuts` track switches them on bar boundaries. The bubbles read the same track, so a
tail still points at the speaker in a close-up. The cost is that a close-up has no
parallax: the wall comes forward with the cast. Rejected alternative: per-layer depth
and a real camera, which would double the data every template must return for a look
this format does not need.

**Cutout proportions are a template decision, not a parameter.** The first 2D heads
read as boxes because the skull, the hair and the body were all roughly the same
width, and the eyes were dark shapes that merged with the hair. The fix was to change
the templates: a large oval skull, a narrow rounded body, white sclera with small
pupils, and a hair cap cut above the eye line. No amount of per-show parameter tuning
recovers a silhouette the template does not offer.

**Text is a numpy mask, not shader work.** Evaluating a stroke font per pixel inside
the shader is possible (an early version did it) and it forces the marcher to know
about glyphs, inflates compile time and makes text a per-frame cost. Rasterising each
line once with SDFs in numpy, then compositing with `std.MaskedMerge`, keeps text out
of the shader entirely, makes the masks inspectable as `.npy`, and works identically
over 2D and 3D shows. The cost is that the masks are built at compile time, so a
bubble cannot be animated per frame; nothing needed that yet.

**Font size and panel size are separate keys.** The first version derived the bubble
from the type, so asking for smaller letters also shrank the panel until the text
touched its edge. `font` (cap height) and `panel` (padding multiplier) are now
independent, which is the only way both "small type" and "comfortable bubble" can be
true at once.

**Settings are switched by `Sections`, not by separate shows.** A show that changes
room is one `Fields` table with both rooms and a cell per field per section; `x` means
absent. This keeps one clock, one dialogue table and one render for the whole episode,
and it is the same mechanism that brings characters on and off. Duplicating the show
per room would drift the two copies apart and double the render.

**Prior art.** Shader Park (JS DSL -> GLSL SDF, headless converters), ISF (a JSON
header declaring `audio`/`audioFFT` inputs, i.e. the shader/host contract),
glslViewer (CLI, audio textures, offline sequences), Hydra and Punctual (audio-
reactive, clocked live-coding languages), sdfx / fogleman/sdf / sdfray (SDF as a
code-side CSG), and `libplacebo`'s mpv `.hook` format (the actual host contract used
here). None of them combine a Markdown song folder, a derived beat clock, mandatory
template parameters and deterministic offline rendering; that combination is the
idea being ported.