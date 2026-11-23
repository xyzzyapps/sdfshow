# TODO - sdfshow

Open work only. Design reasoning lives in `SPEC.md`.

## P0 - scaffold

- [x] git repo, `.gitignore`
- [x] directory layout: `sdfshow/`, `fields/`, `shows/`, `gen/`, `output/`, `tests/`
- [x] Python venv (`vapoursynth`, `numpy`, `vs-placebo`, `pytest`, `ruff`, `black`)
- [x] `pyproject.toml`, `Taskfile.yml`
- [x] verify `core.placebo.Shader` renders a blank clip on this machine

## P1 - clock, markdown, codegen

- [x] `md.py` - scalars + tables with escaped pipes
- [x] `clock.py` - bpm/bars/fps -> beat, bar, step, duration, frames
- [x] `show.py` - parse `show.md` (clock, stage, field order, sections, materials)
- [x] `fields.py` - parse `fields.md` (globals, fields, tracks)
- [x] template substitution; missing placeholder raises; no defaults
- [x] track kinds: `steps`, `bars`, `keys`, `expr`
- [x] `glsl.py` - assemble a complete `.hook` shader from the parsed show
- [x] `compile` command -> `gen/<show>/scene.glsl` + `score.json`

## P2 - renderer

- [x] `render.py` - generate a `.vpy`, `vspipe` -> `ffmpeg` (encode only)
- [x] `render --static` / `frame` -> a single PNG
- [x] `render` -> H.264 MP4, versioned, build lock
- [x] `render --from/--to` - correct clock via the `TIME0` hand-off (verified
      against a still at the same time, 44 dB PSNR after H.264)
- [ ] frame cache / resume - only if 1080p shows become slow (720p renders at
      ~140 fps on this machine, so this is not urgent)
- [x] half-open ranges: `--to 5` is exactly 150 frames at 30 fps (verified: 5.000 s,
      150 frames, and the first frame matches a still at the same time at 41 dB PSNR)
- [ ] `clips` command: render one short clip per section in a single run (the
      four `output/demo/clips/*_5s.mp4` files were made with four `render` calls)
- [ ] `remux` - replace the audio track without re-rendering (needed only when
      audio binding lands)

## P3 - arrangement

- [x] `Sections` cells: `u`, `u<k>`, `s`, `s<k>`, `i`, `i<k>`, `x`
- [x] ordered composition (row order is semantic)
- [x] validation: sections cover 0..bars, every field placed, every field defined,
      first active cell is a union
- [x] per-field material ids + colour (second evaluation pass at the hit point)

## P4 - stage and effects

- [x] stage scalars: distance, yaw, pitch, fov, fog, exposure, background, light
- [x] stage values may be track names (animated camera)
- [x] material surface patterns: `checker`, `grid`, `stripes`, with a `scale`
- [x] single-pass screen space: `scanlines`, `plasma`, `grain`, `vignette`,
      `hue` colour cycling
- [x] demoscene template kit: `tunnel`, `menger`, `gyroid`, `pillars`
- [x] `shows/demo` - four bar-clocked scenes (tunnel, Menger, gyroid, sun+columns)
- [x] guard: a camera started inside a solid renders background, not a backwards march
- [ ] optional: starfield / 2D scroller text
- [ ] optional: bloom or feedback (needs multi-pass)
- [ ] separate `stage.md` if `show.md` gets crowded (currently two files is enough)
- [ ] output presets (1080x1920 vertical, 1080x1080, 1920x1080) - `size` already
      accepts any WxH; a preset is only a convenience

## P5 - audio binding (optional)

- [ ] mux `audio:` without ffmpeg filtering (`-c:a copy` or AAC encode only)
- [ ] per-field RMS envelopes baked into the shader as sampled const arrays (or a
      frame-strip uniform channel), driving track values
- [ ] loudness rules only if audio is actually mastered here (it is not: sdfshow
      consumes an existing file)

## P6 - docs and audit

- [x] `SPEC.md`: architecture, control surfaces, semantics, acceptance checks
- [x] `README.md` quick start
- [ ] choose and add a licence (none is declared yet)
- [ ] reference-shader parity test: generated field vs a hand-written field, on a
      fixed sample lattice (the equivalent of fftechno's "-213 dB" proof)
- [ ] clean-room build from a fresh clone (venv, config, compile, render)
- [ ] second worked example that exercises `s`, `i` and a `span` > 1 steps track