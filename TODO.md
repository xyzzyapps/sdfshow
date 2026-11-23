# TODO - sdfshow

Open work only. Design reasoning lives in `SPEC.md`.

## Done

- [x] scaffold: repo, venv, `pyproject.toml`, `Taskfile.yml`
- [x] `md.py` reader; `clock.py`; `show.py`; `fields.py`; `tracks.py`; `glsl.py`
- [x] `compile` -> `gen/<show>/scene.glsl` + `score.json`
- [x] `frame` -> PNG; `render` -> versioned MP4; build lock; `-threads 1`
- [x] half-open `--from/--to`; `TIME0` hand-off so seeks match full renders
- [x] `clips` -> one short clip per section
- [x] arrangement cells `u`, `u<k>`, `s<k>`, `i<k>`, `x`; ordered; validated
- [x] per-field material ids, colour, patterns (`checker`/`grid`/`stripes`), scale
- [x] screen pass: `scanlines`, `plasma`, `grain`, `vignette`, `hue`
- [x] space folds: `fold: none|mirror|kaleido`, `fold_count`
- [x] effect passes: `bloom`, `chroma`, `crt`, `glitch` (generated GLSL chain)\n- [x] morph cells (`m<w>`), animatable cell operands, `fold_count` as a track\n- [x] effect knobs as tracks; tracks may live in either `show.md` or `fields.md`
- [x] templates: sphere, box, capsule, torus, cylinder, cone, hexprism, plane_wave,
      terrain, helix, tunnel, menger, gyroid, pillars, mandelbulb
- [x] prelude: `vnoise`, `fbm`, `hash13`, `apply_pattern`, `hue_rotate`
- [x] shows: `first`, `ring`, `demo`, `ops`, `post`, `reel` (30 s)
- [x] docs: `README.md`, `SPEC.md`, `TUTORIAL.md`
- [x] GPU parity check (`tests/gpu_parity.py`, max error 0.0076 vs 0.01 tolerance)
- [x] clean-room build from a fresh clone (clone, venv, `pip install -e .`,
      `vapoursynth config`, compile, frame, render and parity all pass)

## Done: SDF text via VapourSynth overlay, dialogue + TTS

Text is no longer rendered in the shader. The stroke font is evaluated in numpy
(sdfshow/textmask.py), giving a signed-distance mask that is word-wrapped, sized to
fit its budget and antialiased analytically. ender.py composites the masks with
std.MaskedMerge after the SDF passes, so type never enters the raymarch.

Fixed along the way: Cut track kind (step keys, needed for hard camera cuts),
per-component animated 	arget, and three collision bugs where a template local
shadowed 	.

- [x] sdfshow/textmask.py: SDF text, word wrap, fit-to-width, rounded panel, tail
- [x] VapourSynth overlay compositing (std.MaskedMerge; there is no Overlay)
- [x] sdfshow/dialog.py: one table drives bubbles and lite TTS
- [x] cuts track kind, animated 	arget
- [x] shows/diner: 16 bars, 9 cuts, 9 lines, two figures
- [ ] known: each figure's torso shows the bench silhouette through it
- [ ] known: shows/bar is superseded by shows/diner; delete or fold together
- [ ] the second bench needs its own booth field with lip: 1

## Old note: dialog scene (shows/bar)

Infrastructure is in place and unit-tested; the bubble text does not render correctly
yet. **Known bug**: the letters come out as vertical bars. The stroke font itself is
correct - 	ools/font_probe.py and 	ools/bubble_probe.py both render the string
cleanly - so the fault is the mapping from bubble space to cell space in
ields/bubble_ink.glsl plus _ink in dialog.glsl_lines. Next steps: render the ink
field with a single glyph and a hard-coded cell rectangle to find which axis is wrong,
instead of iterating on the full scene.

- [x] stroke font (sdfshow/glyphs.py, 44 glyphs) + two probes under 	ools/
- [x] ## Dialogue table: one source for bubble text and spoken audio
- [x] TTS via ffmpeg lite, placed at its bar and mixed (sdfshow/dialog.py)
- [x] per-speaker bubble + ink templates generated into gen/
- [x] sf_detail parameter so the marcher gets a cheap bound and only the material
      pass evaluates glyphs (23.8 s -> 3.9 s per frame at 720p)
- [ ] the bubble-text mapping bug above
- [ ] two-scene framing (bar wide, then two-shot)
- [ ] run the full render and check the audio lines land on their bubbles

## Next

- [ ] choose and add a licence (none is declared yet)
- [ ] temporal effects via `std.AverageFrames` (trails/strobes) with cut guards
- [ ] `placebo.Deband` for dark gradients (optional, one line in the pass chain)
- [ ] frame cache / resume, only if 1080p shows become slow
- [ ] `remux`: replace the audio track without re-rendering
- [ ] 2D overlay layer (text, scrollers) - needs an RGBA mask input to a shader pass
- [ ] torus knot, infinite stairs, sierpinski fold, apollonian
- [ ] per-object transforms (a local fold/rotation parameter on a field)
- [ ] output presets (1080x1920, 1080x1080)

## Audio binding (optional)

- [ ] mux `audio:` without ffmpeg filtering (`-c:a copy` or AAC encode only)
- [ ] per-field RMS envelopes baked into the shader, or a data channel into a pass
- [ ] loudness rules only if audio is actually mastered here (it is not)