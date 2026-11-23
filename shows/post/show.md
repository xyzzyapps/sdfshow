# show - post

A one-bar probe for the effect chain: bloom, chroma, CRT curvature and glitch all
run in sequence over a single striped sphere.

bpm: 120
bars: 1
fps: 30
size: 480x270

## Stage

| key        | value                |
|------------|----------------------|
| distance   | 3.2                  |
| yaw        | 0.2*t                |
| pitch      | -0.1                 |
| fov        | 1.8                  |
| target     | 0\|0\|0             |
| fog        | 0.0                  |
| exposure   | 1.6                  |
| background | 0.01\|0.008\|0.02   |
| light      | 0.4\|0.9\|0.5        |
| grain      | 0.005                |
| vignette   | 0.1                  |
| scanlines  | 0.05                 |

## Fields

| field |
|-------|
| ball  |

## Materials

| field | color            | pattern | scale |
|-------|------------------|---------|-------|
| ball  | 1.0\|0.55\|0.1  | stripes | 3.0   |

## Sections

| bars | ball |
|------|------|
| 0-1  | u    |

## Effects

| effect | key       | value |
|--------|-----------|-------|
| bloom  | threshold | 0.4   |
| bloom  | strength  | 0.9   |
| bloom  | radius    | 3.0   |
| chroma | amount    | 0.10  |
| crt    | curvature | 0.18  |
| glitch | chance    | 0.25  |
| glitch | amount    | 0.08  |