# show - ops

A verification show for the two operators the demo does not use: `s` (subtract)
and `i` (intersect), plus a `steps` track with `span=2`.

| bars | what happens |
|------|--------------|
| 0-1  | a breathing rounded cube |
| 1-2  | a torus channel is carved out of it |
| 2-3  | a sphere and a cube are smoothly intersected |
| 3-4  | the torus carves the intersection |

bpm: 120
bars: 4
fps: 30
size: 640x360

## Stage

| key        | value                |
|------------|----------------------|
| distance   | 5.4                  |
| yaw        | 0.6+0.18*t           |
| pitch      | -0.08                |
| fov        | 1.8                  |
| target     | 0\|0\|0             |
| fog        | 0.02                 |
| exposure   | 1.2                  |
| background | 0.02\|0.015\|0.03   |
| light      | 0.5\|0.8\|0.4        |
| grain      | 0.01                 |
| vignette   | 0.2                  |

## Fields

| field |
|-------|
| shell |
| cube  |
| ring  |

## Materials

| field | color            | pattern | scale |
|-------|------------------|---------|-------|
| shell | 0.65\|0.35\|1.0 | none    | 1.0   |
| cube  | 1.0\|0.72\|0.2  | grid    | 3.0   |
| ring  | 0.2\|0.8\|1.0   | none    | 1.0   |

## Sections

| bars | shell  | cube   | ring   |
|------|--------|--------|--------|
| 0-1  | x      | u      | x      |
| 1-2  | x      | u      | s0.15  |
| 2-3  | u      | i0.25  | x      |
| 3-4  | u      | i0.25  | s0.08  |