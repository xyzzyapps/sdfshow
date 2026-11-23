# fields - pixel

Screen space for `mode: 2d`: x and y are the frame offset divided by frame height, so
`y = 0` is the vertical centre, `y = -0.5` the bottom edge and `y = 0.5` the top. `x`
runs about -0.89..0.89 at 16:9.

## Fields

Back to front. Features come *after* their head so they paint on top, and the cup comes
after the table so it sits on it.

| name     | template     | parameters |
|----------|--------------|------------|
| back     | box2d.glsl   | cx=0, cy=0.30, hx=1.20, hy=0.55, round=0.0 |
| floor    | box2d.glsl   | cx=0, cy=-0.46, hx=1.20, hy=0.18, round=0.0 |
| bench    | box2d.glsl   | cx=0, cy=-0.26, hx=0.95, hy=0.06, round=0.03 |
| table    | box2d.glsl   | cx=0, cy=-0.33, hx=0.62, hy=0.030, round=0.012 |
| aina     | head2d.glsl  | cx=-0.44, cy=-0.02, s=0.44, wide=0.90, fringe=0.16, shoulders=1.0 |
| boris    | head2d.glsl  | cx=0.44, cy=-0.02, s=0.44, wide=1.08, fringe=0.08, shoulders=1.1 |
| aina_hair | hair2d.glsl | cx=-0.44, cy=-0.02, s=0.44, wide=0.90, fringe=0.16 |
| boris_hair | hair2d.glsl | cx=0.44, cy=-0.02, s=0.44, wide=1.08, fringe=0.08 |
| aina_eye | face2d.glsl  | cx=-0.44, cy=-0.02, s=0.44, kind=0, gap=0.125, eye_y=0.055, ew=0.048, eh=0.058, bw=0.072, brow_y=0.155, brow=brow_a, mouth_y=-0.145, mouth=mouth_a |
| boris_eye | face2d.glsl | cx=0.44, cy=-0.02, s=0.44, kind=0, gap=0.135, eye_y=0.055, ew=0.046, eh=0.060, bw=0.075, brow_y=0.158, brow=brow_b, mouth_y=-0.140, mouth=mouth_b |
| aina_brow | face2d.glsl | cx=-0.44, cy=-0.02, s=0.44, kind=1, gap=0.125, brow_y=0.155, bw=0.072, brow=brow_a, eye_y=0.055, ew=0.048, eh=0.058, mouth_y=-0.145, mouth=mouth_a |
| boris_brow | face2d.glsl | cx=0.44, cy=-0.02, s=0.44, kind=1, gap=0.135, brow_y=0.158, bw=0.075, brow=brow_b, eye_y=0.055, ew=0.046, eh=0.060, mouth_y=-0.140, mouth=mouth_b |
| aina_mouth | face2d.glsl | cx=-0.44, cy=-0.02, s=0.44, kind=2, bw=0.080, mouth_y=-0.145, mouth=mouth_a, gap=0.125, eye_y=0.055, ew=0.048, eh=0.058, brow_y=0.155, brow=brow_a |
| boris_mouth | face2d.glsl | cx=0.44, cy=-0.02, s=0.44, kind=2, bw=0.082, mouth_y=-0.140, mouth=mouth_b, gap=0.135, eye_y=0.055, ew=0.046, eh=0.060, brow_y=0.158, brow=brow_b |
| cup      | ellipse2d.glsl | cx=-0.02, cy=-0.30, rx=0.050, ry=0.062 |

`wide` and `shoulders` are what separate the two silhouettes: Aina narrow, Boris broad.
Aina's fringe is lower, so her hair reads as a different cut.

## Tracks

| name | kind | values | options |
|------|------|--------|---------|