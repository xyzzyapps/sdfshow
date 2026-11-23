# fields - pixel

Screen space for `mode: 2d`: x and y are the frame offset divided by frame height, so
`y = 0` is the vertical centre, `y = -0.5` the bottom edge and `y = 0.5` the top. `x`
runs about -0.89..0.89 at 16:9.

## Fields

One table, ordered back to front. Both sets are listed and `Sections` decides which is
drawn, so the diner furniture and the living-room furniture never overlap:

- **diner** (bars 0-8): `sky`, `floor_diner`, `booth`, `table`, `cup`
- **house** (bars 8-20): `wall_house`, `floor_house`, `sofa`, `rug`, `lamp`, `chair`

Two people sit together in both rooms, at the same screen positions, which is what makes
it read as one show rather than two.

| name | template | parameters |
|------|----------|------------|
| sky | box2d.glsl | cx=0, cy=0.30, hx=1.20, hy=0.55, round=0.0 |
| floor_diner | box2d.glsl | cx=0, cy=-0.46, hx=1.20, hy=0.18, round=0.0 |
| booth | seat2d.glsl | cx=0, cy=-0.30, s=0.40, hw=1.16, hh=0.11 |
| table | table2d.glsl | cx=0.06, cy=-0.29, s=0.40, hw=0.60 |
| wall_house | box2d.glsl | cx=0, cy=0.30, hx=1.20, hy=0.55, round=0.0 |
| floor_house | box2d.glsl | cx=0, cy=-0.44, hx=1.20, hy=0.20, round=0.0 |
| sofa | sofa2d.glsl | cx=-0.10, cy=-0.40, s=0.46, hw=0.80, back=0.24 |
| rug | ellipse2d.glsl | cx=-0.05, cy=-0.47, rx=0.90, ry=0.10 |
| lamp | lamp2d.glsl | cx=0.76, cy=-0.30, s=0.34, glow=0.08 |
| chair | box2d.glsl | cx=-0.80, cy=-0.24, hx=0.15, hy=0.18, round=0.04 |
| aina | head2d.glsl | cx=-0.44, cy=-0.13, s=0.27, wide=0.90, shoulders=1.0 |
| aina_hair | hair2d.glsl | cx=-0.44, cy=-0.13, s=0.27, wide=0.90, fringe=0.16, style=0 |
| aina_eye | face2d.glsl | cx=-0.44, cy=-0.09, s=0.34, kind=0, gap=0.125, eye_y=0.055, ew=0.048, eh=0.058, bw=0.070, brow_y=0.155, brow=brow_a, mouth_y=-0.145, mouth=mouth_a |
| aina_brow | face2d.glsl | cx=-0.44, cy=-0.09, s=0.34, kind=1, gap=0.125, brow_y=0.155, bw=0.070, brow=brow_a, eye_y=0.055, ew=0.048, eh=0.058, mouth_y=-0.145, mouth=mouth_a |
| aina_mouth | face2d.glsl | cx=-0.44, cy=-0.09, s=0.34, kind=2, bw=0.078, mouth_y=-0.145, mouth=mouth_a, gap=0.125, eye_y=0.055, ew=0.048, eh=0.058, brow_y=0.155, brow=brow_a |
| boris | head2d.glsl | cx=0.06, cy=-0.13, s=0.27, wide=1.08, shoulders=1.1 |
| boris_hair | hair2d.glsl | cx=0.06, cy=-0.13, s=0.27, wide=1.08, fringe=0.08, style=1 |
| boris_eye | face2d.glsl | cx=0.06, cy=-0.09, s=0.34, kind=0, gap=0.135, eye_y=0.055, ew=0.046, eh=0.060, bw=0.073, brow_y=0.158, brow=brow_b, mouth_y=-0.140, mouth=mouth_b |
| boris_brow | face2d.glsl | cx=0.06, cy=-0.09, s=0.34, kind=1, gap=0.135, brow_y=0.158, bw=0.073, brow=brow_b, eye_y=0.055, ew=0.046, eh=0.060, mouth_y=-0.140, mouth=mouth_b |
| boris_mouth | face2d.glsl | cx=0.06, cy=-0.09, s=0.34, kind=2, bw=0.080, mouth_y=-0.140, mouth=mouth_b, gap=0.135, eye_y=0.055, ew=0.046, eh=0.060, brow_y=0.158, brow=brow_b |
| dora | head2d.glsl | cx=0.58, cy=-0.13, s=0.27, wide=0.94, shoulders=1.05 |
| dora_hair | hair2d.glsl | cx=0.58, cy=-0.13, s=0.27, wide=0.94, fringe=0.12, style=2 |
| dora_eye | face2d.glsl | cx=0.58, cy=-0.09, s=0.34, kind=0, gap=0.128, eye_y=0.055, ew=0.050, eh=0.056, bw=0.068, brow_y=0.152, brow=brow_d, mouth_y=-0.142, mouth=mouth_d |
| dora_brow | face2d.glsl | cx=0.58, cy=-0.09, s=0.34, kind=1, gap=0.128, brow_y=0.152, bw=0.068, brow=brow_d, eye_y=0.055, ew=0.050, eh=0.056, mouth_y=-0.142, mouth=mouth_d |
| dora_mouth | face2d.glsl | cx=0.58, cy=-0.09, s=0.34, kind=2, bw=0.076, mouth_y=-0.142, mouth=mouth_d, gap=0.128, eye_y=0.055, ew=0.050, eh=0.056, brow_y=0.152, brow=brow_d |
| ellis | head2d.glsl | cx=-0.78, cy=-0.13, s=0.27, wide=1.00, shoulders=0.95 |
| ellis_hair | hair2d.glsl | cx=-0.78, cy=-0.13, s=0.27, wide=1.00, fringe=0.06, style=3 |
| ellis_eye | face2d.glsl | cx=-0.78, cy=-0.09, s=0.34, kind=0, gap=0.130, eye_y=0.050, ew=0.044, eh=0.062, bw=0.066, brow_y=0.150, brow=brow_e, mouth_y=-0.138, mouth=mouth_e |
| ellis_brow | face2d.glsl | cx=-0.78, cy=-0.09, s=0.34, kind=1, gap=0.130, brow_y=0.150, bw=0.066, brow=brow_e, eye_y=0.050, ew=0.044, eh=0.062, mouth_y=-0.138, mouth=mouth_e |
| ellis_mouth | face2d.glsl | cx=-0.78, cy=-0.09, s=0.34, kind=2, bw=0.074, mouth_y=-0.138, mouth=mouth_e, gap=0.130, eye_y=0.050, ew=0.044, eh=0.062, brow_y=0.150, brow=brow_e |
| cup | ellipse2d.glsl | cx=0.36, cy=-0.250, rx=0.034, ry=0.040 |

Four silhouettes: Aina narrow, Boris broad, Dora long-haired, Ellis round and balding.

## Tracks

| name | kind | values | options |
|------|------|--------|---------|