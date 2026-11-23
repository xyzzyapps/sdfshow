# show - pixel

Two characters in a diner booth, as flat 2D pixel art: **SDF shapes stacked like SVG,
quantised to a pixel grid.**

`mode: 2d` changes the renderer entirely. There is no raymarch, no camera, no normals
and no fog; every field is a flat shape in screen space and the picture is painted
back-to-front, so the `Fields` table reads top-to-bottom as a z-stack (first row is
furthest back). That is the whole reason this look is cheap: one field evaluation per
layer per pixel, so snapping to a chunky pixel grid costs almost nothing.

`pixel: 9` snaps the sample coordinate to a 9-device-pixel grid, and `outline` draws a
dark rim around every layer, which is what gives the cutout edge.

Because a 2D layer is one flat fill, a face is built from **separate layers** - head,
then eyes, then brows, then mouth - each with its own colour. That is the same idea as
an SVG document, and it is what makes the pixel-art face read.

bpm: 96
bars: 12
fps: 30
size: 1280x720

## Stage

Only the 2D keys matter here; the 3D ones are ignored in `mode: 2d`.

| key           | value                |
|---------------|----------------------|
| mode          | 2d                   |
| pixel         | 9                    |
| outline       | 0.007                |
| outline_color | 0.08\|0.05\|0.09     |
| exposure      | 1.0                  |
| background    | 0.16\|0.20\|0.24     |
| vignette      | 0.22                 |
| scanlines     | 0.0                  |
| grain         | 0.006                |
| hue           | 0                    |

## Fields

| field |
|-------|
| back |
| floor |
| bench |
| table |
| aina |
| boris |
| aina_hair |
| boris_hair |
| aina_eye |
| boris_eye |
| aina_brow |
| boris_brow |
| aina_mouth |
| boris_mouth |
| cup |

## Materials

A warm 1970s diner palette: mustard wall, cream vinyl, teal and rust seating, and dark
features so the faces read.

| field       | color             | pattern | scale |
|-------------|-------------------|---------|-------|
| back        | 0.84\|0.66\|0.36 | none    | 1.0   |
| floor       | 0.36\|0.34\|0.31 | none    | 1.0   |
| bench       | 0.30\|0.16\|0.14 | none    | 1.0   |
| table       | 0.87\|0.80\|0.66 | none    | 1.0   |
| aina        | 0.95\|0.76\|0.55 | none    | 1.0   |
| boris       | 0.56\|0.76\|0.82 | none    | 1.0   |
| aina_hair   | 0.34\|0.20\|0.13 | none    | 1.0   |
| boris_hair  | 0.20\|0.16\|0.14 | none    | 1.0   |
| aina_eye    | 0.12\|0.09\|0.12 | none    | 1.0   |
| boris_eye   | 0.12\|0.09\|0.12 | none    | 1.0   |
| aina_brow   | 0.30\|0.18\|0.12 | none    | 1.0   |
| boris_brow  | 0.24\|0.16\|0.12 | none    | 1.0   |
| aina_mouth  | 0.42\|0.16\|0.18 | none    | 1.0   |
| boris_mouth | 0.36\|0.16\|0.18 | none    | 1.0   |
| cup         | 0.96\|0.94\|0.88 | none    | 1.0   |

## Sections

| bars  | back | floor | bench | table | aina | boris | aina_hair | boris_hair | aina_eye | boris_eye | aina_brow | boris_brow | aina_mouth | boris_mouth | cup |
|-------|------|-------|-------|-------|------|-------|----------|-----------|-----------|------------|------------|-------------|-----|
| 0-6   | u    | u     | u     | u     | u    | u     | u         | u          | u        | u         | u         | u          | u           | u           | u   |
| 6-12  | u    | u     | u     | u     | u    | u     | u         | u          | u        | u         | u         | u          | u           | u           | u   |

## Dialogue

Bar is 2.5 s at 96 BPM.

| speaker | bars  | text                              | voice |
|---------|-------|-----------------------------------|-------|
| AINA    | 1-2   | So we are just going to sit here? | slt   |
| BORIS   | 2-3   | That was the plan.                | rms   |
| AINA    | 3-4   | For how long?                     | slt   |
| BORIS   | 4-6   | Until one of us has a thought.    | rms   |
| AINA    | 7-8   | I had one.                        | slt   |
| BORIS   | 8-9   | Was it about the menu?            | rms   |
| AINA    | 9-10  | It was about the menu.            | slt   |
| BORIS   | 10-12 | Then we are still here.           | rms   |

## Effects

| effect | key       | value |
|--------|-----------|-------|
| bloom  | threshold | 0.75  |
| bloom  | strength  | 0.18  |
| bloom  | radius    | 1.5   |
| chroma | amount    | 0.008 |

## Tracks

| name    | kind | values | options |
|---------|------|--------|---------|
| mouth_a | expr | (t > 2.5 && t < 5.0) ? 0.5+0.5*sin(t*22.0) : (t > 17.5 && t < 25.0) ? 0.5+0.5*sin(t*20.0) : 0.05 | |
| mouth_b | expr | (t > 5.0 && t < 15.0) ? 0.5+0.5*sin(t*21.0) : (t > 25.0) ? 0.5+0.5*sin(t*19.0) : 0.05 | |
| brow_a  | expr | (t > 16.0 && t < 20.0) ? 1.0 : 0.0 | |
| brow_b  | expr | (t > 24.0) ? 1.0 : 0.0 | |