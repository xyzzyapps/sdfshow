# SPEC.md - sdfshow (SRS)

Software requirements and architecture for **sdfshow**: signed-distance-field shows
authored as Markdown, compiled to a single GLSL raymarcher, and rendered frame-exact
through VapourSynth. Version 0.1.0.

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
- deterministic, seekable frames; versioned outputs; a build lock.

Out of scope for 0.1.0:

- audio generation or audio-reactive control (a later milestone; see `TODO.md`);
- a GUI, a real-time preview, mesh export, or PBR/pathtracing;
- arbitrary GLSL supplied by the user outside `fields/` (templates are function
  bodies, by design);
- multi-pass shaders and image-based effects (bloom, feedback, chromatic
  aberration); a single-pass screen-space `post()` exists.

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

---

## 3. Clock model

From `show.md`:

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

Module responsibilities:

| module | responsibility |
|--------|----------------|
| `config.py` | paths, stage defaults, encode constants, `unique_path` |
| `md.py` | one Markdown reader: scalars, tables, escaped pipes, `key/value` tables |
| `clock.py` | the clock and its tokens |
| `show.py` | `show.md` parsing, cells, sections, materials, validation |
| `tracks.py` | track parsing, parameter-expression validation, track GLSL |
| `fields.py` | `fields.md` parsing, template preprocessing and substitution, field GLSL |
| `glsl.py` | whole-shader assembly: prelude, scene, materials, camera, shading, hook |
| `render.py` | compile, VapourSynth script generation, vspipe/ffmpeg orchestration |
| `proc.py` | exclusive build lock, quiet subprocess execution |
| `cli.py` | argument parsing and command dispatch |

---

## 5. Control surface A - `show.md`

Required scalars: `bpm`, `bars`, `fps`. Optional: `size` (`WxH`, default 1280x720),
`audio` (a path, reserved; not yet muxed into the render).

### 5.1 Stage

A `| key | value |` table. Values are numbers, `r|g|b` triples, track names, or
arithmetic over tracks and `t`.

| key | meaning | default |
|-----|---------|---------|
| `distance` | camera distance from target | `4.2` |
| `yaw` | orbit angle, radians | `0.6` |
| `pitch` | elevation, radians | `-0.18` |
| `fov` | focal length in the ray construction (larger = narrower) | `1.9` |
| `target` | look-at point, `x|y|z` | `0|0|0` |
| `fog` | exponential fog density | `0.03` |
| `exposure` | pre-tonemap gain | `1.1` |
| `background` | `r|g|b`, also the fog colour | `0.02|0.025|0.04` |
| `light` | key light direction, `x|y|z` | `0.6|0.8|0.5` |
| `scanlines` | screen pass: darken alternate pixel rows | `0` |
| `plasma` | screen pass: slow colour wash | `0` |
| `grain` | screen pass: per-pixel noise | `0.012` |
| `vignette` | screen pass: radial darkening | `0.22` |
| `hue` | rotate every material colour around grey | `0` |

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
6. The first active cell of a section is a union (`u` or `u<k>`).

Cells: `u`, `u<k>`, `s<k>`, `i<k>`, `x`. A blank cell is `x`. `0` is accepted as
`x` for readability.

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
| `steps` | `|`-separated numbers | `span=<bars>` (default 1), `ease=none|smooth` |
| `bars` | `|`-separated numbers | `ease=none|smooth` |
| `keys` | `bar:value|bar:value` | `ease=none|smooth` |
| `expr` | one GLSL expression over `t` | none |

Track names are unique and become `track_<name>`. `expr` is the escape hatch: its
contents are not token-validated (it may use any GLSL expression).

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
point only, not during marching.

---

## 9. Generated shader

Structure, in order:

1. `//!HOOK MAIN`, `//!BIND HOOKED`, `//!DESC <show>`, and the `// @TIME0@` sentinel.
2. Defines: `FPS`, `BAR`, `BEAT`, `STEP`, `DUR`, `FRAMES`, `PI`, `TAU`, and
   `TIME0` (0 unless the render starts later).
3. Helpers: `smin`, `smax`, hashes, rotations, `apply_pattern`, `hue_rotate`.
4. Generated track functions and field functions.
5. `map_scene`, `mat_id`, `mat_color`.
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

---

## 10. Renderer

`render.py` generates a VapourSynth script:

```
clip = core.std.BlankClip(W, H, format=vs.YUV444P16, length=NF, fpsnum=FPS)
clip = core.placebo.Shader(clip, shader_s=..., width=W, height=H,
                           sigmoidize=False, linearize=False, matrix=5)
clip = core.resize.Bicubic(clip, format=vs.YUV420P8, matrix_in_s="470bg",
                           matrix_s="470bg", range_in_s="limited", range_s="limited")
```

`vs-placebo` requires `YUVxxxP16` input; the blank clip is only a frame carrier,
because the shader ignores `HOOKED_tex` entirely.

The script rewrites the `// @TIME0@` sentinel with the render's first frame. The
shader source itself stays identical across renders.

Encoding:

```
vspipe -c y4m -s A -e B gen/<s>/render.vpy -
  | ffmpeg -f yuv4mpegpipe -i - [-i audio] -c:v libx264 -preset slow -crf 18
           -pix_fmt yuv420p -threads 1 -movflags +faststart output/<s>/show.mp4
```

`-threads 1` is deliberate. With threaded rate control, x264 can make different
decisions on identical input, so two renders of the same show would differ by a few
hundred bytes. Single-threaded x264 makes the encoded file byte-identical; the cost
is small at these sizes (480 frames of 960x540 in about 15 s on the reference
machine).

ffmpeg is used only as an encoder/muxer. No ffmpeg filter touches the picture: all
geometry and shading are the generated GLSL.

Stills use the same path with `-s F -e F -frames:v 1 -update 1` to write a PNG.
Ranges are half-open: `--from A --to B` encodes frames
`frame_at(A) .. frame_limit(B) - 1`, so `--to 5` is exactly five seconds.

---

## 11. Outputs, versioning, locking

- `gen/<show>/scene.glsl` is generated; `fields/` is the source of truth.
- `gen/<show>/score.json` records the resolved clock, sections and cells for audits.
- `output/<show>/show.mp4`, `frame_NNNNN.png`; if a target exists, `_v2`, `_v3`, ...
- `output/<show>/logs/{vspipe,ffmpeg}.log` capture stderr.
- `output/<show>/logs/.build.lock` (created with `O_EXCL`) prevents concurrent
  builds of the same show.

---

## 12. Verification and acceptance

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
  source.

Manual / visual:

- `python -m sdfshow frame --show first --at 5` shows the sphere, the ring and the
  wavy floor;
- `python -m sdfshow frame --show demo --at 2` shows the ring tunnel;
- `shows/ring` is the single-field probe;
- a still rendered via `--at` must equal the corresponding frame of the full video
  when both are decoded to the same colour space (verified at 44 dB PSNR after
  H.264, i.e. compression-only difference);
- a `--from`/`--to` render must equal the same frame range of the full render;
- two full renders must be byte-identical (verified by file hash, with
  `-threads 1`);
- a repeat `compile` must be byte-identical.

---

## 13. Extension guide

### Add a field template

1. Create `fields/<name>.glsl` returning a distance.
2. Add a `{{placeholder}}` for every knob.
3. Add a row to a show's `## Fields` table with values for each placeholder.
4. `compile`, then `frame` at a time where the field is active.

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

---

## 14. Risks and limitations

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
- **No audio yet.** `audio:` is parsed but not muxed. Audio-reactive control needs
  a data channel into the shader (a sampled envelope array baked into the shader, or
  the frame-strip idiom used by fftechno).
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

---

## 15. File inventory

| path | tracked | purpose |
|------|---------|---------|
| `sdfshow/*.py` | yes | the package |
| `fields/*.glsl` | yes | template library |
| `fields/README.md` | yes | template-language guide |
| `shows/first/{show,fields}.md` | yes | worked example |
| `shows/demo/{show,fields}.md` | yes | demoscene set (tunnel, Menger, gyroid, sun, columns) |
| `shows/ring/{show,fields}.md` | yes | one-field probe |
| `tests/*.py` | yes | pytest suite |
| `gen/<show>/*` | no | generated shader + score |
| `output/<show>/*` | no | renders, stills, logs |
| `SPEC.md`, `README.md`, `TODO.md` | yes | documentation |
| `Taskfile.yml`, `pyproject.toml` | yes | tooling |

---

## 16. Design decisions and rejected alternatives

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

**Heading-based table lookup.** `## Sections` and `## Materials` are located by
their headings. Before this, a prose table in a show's introduction that happened
to start with `bars` was parsed as an arrangement. Data tables and documentation
tables now cannot collide.

**Prior art.** Shader Park (JS DSL -> GLSL SDF, headless converters), ISF (a JSON
header declaring `audio`/`audioFFT` inputs, i.e. the shader/host contract),
glslViewer (CLI, audio textures, offline sequences), Hydra and Punctual (audio-
reactive, clocked live-coding languages), sdfx / fogleman/sdf / sdfray (SDF as a
code-side CSG), and `libplacebo`'s mpv `.hook` format (the actual host contract used
here). None of them combine a Markdown song folder, a derived beat clock, mandatory
template parameters and deterministic offline rendering; that combination is the
idea being ported.