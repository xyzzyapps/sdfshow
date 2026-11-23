# fields - diner

Coordinates: the table top is `y = 0.02`, the floor `y = -1.55`. Aina sits at
`x = -0.72`, Boris at `x = +0.86`, both facing the camera across the booth.

## Fields

| name  | template        | parameters |
|-------|-----------------|------------|
| floor | plane_wave.glsl | amp=0, freq=1, speed=0, level=-1.55, shrink=1 |
| wall  | box.glsl        | cx=0, cy=0.60, cz=-2.30, hx=4.4, hy=2.20, hz=0.10, round=0.02 |
| booth | booth.glsl      | cx=0, cy=0, cz=-0.35, flip=0 |
| table | box.glsl        | cx=0.06, cy=-0.02, cz=0.05, hx=0.92, hy=0.045, hz=0.52, round=0.03 |
| cup   | cup.glsl        | cx=-0.22, cy=0.07, cz=0.15 |
| aina  | talker.glsl     | cx=-0.72, cy=0.30, cz=0.06, lean=-0.06, tilt=-0.04, shape=1.06, mouth=mouth_a, brow=brow_a |
| boris | talker.glsl     | cx=0.86, cy=0.30, cz=0.06, lean=0.06, tilt=0.05, shape=0.92, mouth=mouth_b, brow=brow_b |

Aina's `shape=1.06` gives her a longer face, Boris's `0.92` a rounder one - the two
silhouettes have to be separable from a close-up without colour.

## Tracks

| name | kind | values | options |
|------|------|--------|---------|