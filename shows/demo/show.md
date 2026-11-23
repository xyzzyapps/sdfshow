# show - demo

A four-scene demoscene set, cut on bar lines at 120 BPM (2 s per bar):

| bars  | scene |
|-------|-------|
| 0-4   | ring tunnel, camera inside the mouth |
| 4-8   | Menger sponge over a checkerboard floor |
| 8-12  | spinning gyroid over the floor |
| 12-16 | striped sun and a hall of columns |

bpm: 120
bars: 16
fps: 30
size: 960x540

## Stage

Camera keys ramp quickly at each cut (a 0.35-bar move), then hold while the scene
turns. `hue` cycles the palette; `scanlines` and `plasma` are the CRT pass.

| key        | value                     |
|------------|---------------------------|
| distance   | dolly                     |
| yaw        | yaw                       |
| pitch      | pitch                     |
| fov        | fov                       |
| target     | 0\|0\|0                   |
| fog        | fog                       |
| exposure   | 1.28                      |
| background | 0.018\|0.012\|0.032       |
| light      | 0.45\|0.8\|0.35           |
| scanlines  | 0.13                      |
| plasma     | 0.045                     |
| grain      | 0.02                      |
| vignette   | 0.24                      |
| hue        | hue                       |

## Fields

| field   |
|---------|
| tunnel  |
| menger  |
| gyroid  |
| sun     |
| pillars |
| floor   |

## Materials

`pattern` is `none`, `checker`, `grid` or `stripes`; `scale` sets its frequency.

| field   | color            | pattern | scale |
|---------|------------------|---------|-------|
| tunnel  | 0.20\|0.90\|1.0  | stripes | 2.0   |
| menger  | 1.00\|0.75\|0.20 | none    | 1.0   |
| gyroid  | 0.35\|1.00\|0.65 | none    | 1.0   |
| sun     | 1.00\|0.35\|0.12 | stripes | 3.0   |
| pillars | 0.55\|0.30\|1.00 | stripes | 2.0   |
| floor   | 0.08\|0.10\|0.22 | checker | 1.6   |

## Sections

| bars  | tunnel | menger | gyroid | sun | pillars | floor |
|-------|--------|--------|--------|-----|---------|-------|
| 0-4   | u      | x      | x      | x   | x       | x     |
| 4-8   | x      | u      | x      | x   | x       | u     |
| 8-12  | x      | x      | u      | x   | x       | u     |
| 12-16 | x      | x      | x      | u   | u       | u     |