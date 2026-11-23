# fields - first

Globals are available to every field as `{{name}}`. `bar`, `beat`, `step`, `dur`,
`frames`, `fps`, `w` and `h` are injected from `show.md` and may not be redefined.

## Fields

One row per field: `name | template | parameters`. A parameter value is a number, a
track name, or arithmetic over tracks and `t` (`0.62*pulse`). No defaults: a missing
placeholder fails the build by name.

| name  | template        | parameters |
|-------|-----------------|------------|
| core  | sphere.glsl     | radius=0.62*pulse, cx=0, cy=0.10*sin(t*0.7), cz=0 |
| ring  | torus.glsl      | radius=ring_radius, thickness=0.055, spin=0.35, tilt=tilt |
| floor | plane_wave.glsl | amp=wave_amp, freq=2.1, speed=1.2, level=-1.05, shrink=0.55 |

## Tracks

`steps` is a repeating list on a 16th-note grid (`span` in bars, default 1); `bars`
is one value per bar, looping; `keys` are explicit `bar:value` points; `expr` is a
raw GLSL expression over `t`. `ease=smooth` smooths interpolation.

| name        | kind  | values                                             | options     |
|-------------|-------|----------------------------------------------------|-------------|
| pulse       | steps | 1.05\|0.92\|0.86\|0.92                              | ease=smooth |
| dolly       | keys  | 0:4.8\|3:4.1\|7:4.5                                 | ease=smooth |
| spin        | expr  | 0.45+0.12*t                                        |             |
| ring_radius | bars  | 1.15\|1.35\|1.25\|1.15\|1.3\|1.5\|1.4\|1.25         | ease=smooth |
| tilt        | expr  | 0.9+0.15*sin(t*0.8)                                |             |
| wave_amp    | expr  | 0.045+0.03*sin(t*1.3)                              |             |