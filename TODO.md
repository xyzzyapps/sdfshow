# TODO - sdfshow

Open work only. Design reasoning lives in `SPEC.md`.

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
- [x] `shows/diner`: the 3D animation (booth, two people, cut-track camera, dialogue)
- [x] `shows/pixel`: two settings switched by `Sections`, four characters,
      12 dialogue lines, 50 s render with audio
- [x] cutout restyle: `pixel` off, big heads on small bodies, white sclera with
      pupils, a jaw that drops, simplified props (no pedestal foot, no lamp glow pool,
      no chair), construction-paper palette
- [x] 2D camera: `zoom`/`focus_x`/`focus_y` as `cuts` tracks, so the show cuts
      wide -> close -> close -> wide on the speaker at bar boundaries
- [x] bubbles: panel centred on the speaker's screen position (camera-aware), wide
      tail whose tip lands on their head
- [x] dialogue rewritten: dry, distinct voices, a running gag and a button
- [x] female voice for Dora: `slt*0.92` (pitch-shifted with rubberband) instead of
      the male `awb`; the voice cell accepts `<voice>*<pitch>` and is tested
- [x] cast restyle: one paper-white skin, shirts, arms with hands, two legs; the head
      layer is the skull only (a neck painted over the shirt read as a beard)
- [x] figure templates `neck2d`, `body2d`, `arms2d`, `legs2d`; mirroring needs `abs`
      on the local point, or the pair merges into one column
- [x] opening line follows the staging: the cast stands, so Aina asks why
- [x] `bubble: caption`: SCUMM-style white type with a dark outline, no panel
- [x] `stars2d`, `arch2d`, `fire2d` templates
- [x] `shows/island`: a second 2D demo - night cliff, stone arch, campfire, two figures,
      caption dialogue, `bars: auto` ending on the last line
- [x] raster actors: `## Sprites` table, plates in `gen/`, `MaskedMerge` after the SDF
      passes; sheets resolved from the show folder or the repo root
- [x] `tools/prep_sprites.py`: key a baked checkerboard, keep the sprite, refill enclosed
      light regions, erode the anti-aliased rim; writes `assets/sprites/{boy,pirate}.png`
- [x] island cast replaced by two sprite actors (idle + talking over their own lines)
- [x] Boris's shirt moved from brick (the booth colour) to violet, so he reads against
      the diner
- [x] `bars: auto`: the clock measures the last `## Dialogue` bar, so the show stops
      with the dialogue; numeric `bars` still works, and a line past the end fails by name
- [x] mouth tracks corrected to each speaker's own bar windows (they were one line out)
- [x] `tests/test_textmask.py`: no clipping, wrap/fit budget, panel padding vs type,
      tail side
- [x] deleted `shows/bar`: the abandoned first dialogue scene, superseded by
      `shows/diner`; `tools/bubble_probe.py` now reads `shows/diner`

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