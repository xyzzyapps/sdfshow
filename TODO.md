# TODO - sdfshow

Open work only. Design reasoning lives in `SPEC.md`.

## Blocked on approval

- [ ] delete `shows/diner` and `shows/bar`: both are superseded by `shows/pixel`
      (the 2D rework folded their two-figure dialogue into one show with two settings).
      They still compile, so deleting them is a judgement call, not a fix.

## Open

- [ ] `polygon2d`: a flat polygon needs a vertex-list macro the template language
      does not have
- [ ] temporal effects via `std.AverageFrames` (trails/strobes) with cut guards
- [ ] `placebo.Deband` for dark gradients (optional, one line in the pass chain)
- [ ] frame cache / resume, only if 1080p shows become slow
- [ ] `remux`: replace the audio track without re-rendering
- [ ] per-object transforms (a local fold/rotation parameter on a field)
- [ ] output presets (1080x1920, 1080x1080)
- [ ] torus knot, infinite stairs, sierpinski fold, apollonian

## Audio binding (optional)

- [ ] mux `audio:` without ffmpeg filtering (`-c:a copy` or AAC encode only)
- [ ] per-field RMS envelopes baked into the shader, or a data channel into a pass
- [ ] loudness rules only if audio is actually mastered here (it is not)

## Done

### Renderers

- [x] 3D: raymarcher with normals, AO, soft shadows, fog, tonemap
- [x] 2D: `mode: 2d`, flat layers painted back-to-front in screen space, no march
- [x] `pixel` quantise and `outline` rim as stage keys (both may be tracks)
- [x] effect passes: `bloom`, `chroma`, `crt`, `glitch`, generated as hook shaders
- [x] space folds: `fold: none|mirror|kaleido`, `fold_count` as a track
- [x] screen pass: `scanlines`, `plasma`, `grain`, `vignette`, `hue`

### Arrangement and templates

- [x] arrangement cells `u`, `u<k>`, `s<k>`, `i<k>`, `m<w>`, `x`; ordered; validated
- [x] morph cells (`m<w>`), animatable cell operands
- [x] templates: sphere, box, capsule, torus, cylinder, cone, hexprism,
      plane_wave, terrain, helix, tunnel, menger, gyroid, pillars, mandelbulb
- [x] flat templates: ellipse2d, box2d, capsule2d, head2d, hair2d, face2d,
      seat2d, table2d, sofa2d, lamp2d, window2d
- [x] template library documented in `fields/README.md`

### Text and dialogue

- [x] `textmask.py`: SDF stroke font, word wrap, fit-to-width, rounded panel, tail
- [x] bubbles composited by VapourSynth as numpy masks (`std.MaskedMerge`; there is
      no `Overlay` in this build)
- [x] `dialog.py`: one `## Dialogue` table drives bubbles, seating and flite TTS
- [x] fixed: the first text line was clipped above the bubble canvas
- [x] `font` and `panel` stage keys: type size and bubble padding are independent
- [x] per-speaker seating from field `cx`, so a tail follows its speaker
- [x] calmer mouth animation (a small pulse, not a full open/close)

### Shows

- [x] `shows/first`, `shows/ring`, `shows/ops`, `shows/post`, `shows/demo`
- [x] `shows/reel`: 30 s, five scenes, morphs, kaleido ripple, effect chain
- [x] `shows/pixel`: two settings switched by `Sections`, four characters,
      12 dialogue lines, 50 s render with audio

### Pipeline

- [x] `compile` -> `gen/<show>/scene.glsl` + `score.json`
- [x] `frame` -> PNG; `render` -> versioned MP4; build lock; `-threads 1`, `-r 1`
- [x] half-open `--from/--to`; `TIME0` hand-off so seeks match full renders
- [x] `clips` -> one short clip per section

### Documentation and checks

- [x] `README.md`, `SPEC.md`, `TUTORIAL.md` cover both renderers, dialogue and
      bubbles (SPEC section 10 is the 2D contract)
- [x] `LICENSE.md`: PolyForm Noncommercial 1.0.0
- [x] 53 pytest tests, ruff and black clean
- [x] GPU parity check (`tests/gpu_parity.py`)
- [x] clean-room build from a fresh clone