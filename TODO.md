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

## In progress: dialog scene (shows/bar)

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