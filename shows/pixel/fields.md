# fields - pixel

Screen space for `mode: 2d`: x and y are the frame offset divided by frame height, so
`y = 0` is the vertical centre, `y = -0.5` the bottom edge and `y = 0.5` the top. `x`
runs about -0.89..0.89 at 16:9. `zoom` and `focus_x`/`focus_y` scale this space around a
focus point, which is how the show cuts to close-ups.

## Fields

One table, ordered back to front. Both sets are listed and `Sections` decides which is
drawn, so the diner furniture and the living-room furniture never overlap:

- **diner** (bars 0-8): `sky`, `floor_diner`, `booth`, `table`, `cup`
- **house** (bars 8-20): `wall_house`, `floor_house`, `sofa`, `rug`, `lamp`

Every part of a figure is its own row, because a 2D layer is one flat fill: trousers, neck, shirt, arms and hands, head, hair, white sclera, dark pupils,
dark mouth. The same is
true of furniture.

| name | template | parameters |
|------|----------|------------|
| sky | box2d.glsl | cx=0, cy=0.30, hx=1.20, hy=0.55, round=0.0 |
| floor_diner | box2d.glsl | cx=0, cy=-0.46, hx=1.20, hy=0.18, round=0.0 |
| booth | seat2d.glsl | cx=0, cy=-0.30, s=0.40, hw=1.16, hh=0.13 |
| table | table2d.glsl | cx=-0.18, cy=-0.29, s=0.40, hw=0.60 |
| wall_house | box2d.glsl | cx=0, cy=0.30, hx=1.20, hy=0.55, round=0.0 |
| floor_house | box2d.glsl | cx=0, cy=-0.44, hx=1.20, hy=0.20, round=0.0 |
| sofa | sofa2d.glsl | cx=-0.10, cy=-0.40, s=0.46, hw=0.92, back=0.26 |
| rug | ellipse2d.glsl | cx=-0.05, cy=-0.46, rx=0.56, ry=0.06 |
| lamp | lamp2d.glsl | cx=0.76, cy=-0.30, s=0.34, glow=0.08 |
| cup | ellipse2d.glsl | cx=-0.18, cy=-0.250, rx=0.034, ry=0.040 |
| aina_legs | legs2d.glsl | cx=-0.44, cy=-0.06, s=0.30 |
| aina_neck | neck2d.glsl | cx=-0.44, cy=-0.06, s=0.30, shoulders=0.95 |
| aina_body | body2d.glsl | cx=-0.44, cy=-0.06, s=0.30, shoulders=0.95 |
| aina_hands | arms2d.glsl | cx=-0.44, cy=-0.06, s=0.30, shoulders=0.95 |
| aina | head2d.glsl | cx=-0.44, cy=-0.06, s=0.30, wide=0.92 |
| aina_hair | hair2d.glsl | cx=-0.44, cy=-0.06, s=0.30, wide=0.92, fringe=0.20, style=0 |
| aina_eye | face2d.glsl | cx=-0.44, cy=-0.06, s=0.34, kind=0, gap=0.125, eye_y=0.075, ew=0.058, eh=0.066, bw=0.095, brow_y=0.160, brow=0, mouth_y=-0.110, mouth=mouth_a |
| aina_pupil | face2d.glsl | cx=-0.44, cy=-0.06, s=0.34, kind=3, gap=0.125, eye_y=0.075, ew=0.058, eh=0.066, bw=0.095, brow_y=0.160, brow=0, mouth_y=-0.110, mouth=mouth_a |
| aina_mouth | face2d.glsl | cx=-0.44, cy=-0.06, s=0.34, kind=2, gap=0.125, eye_y=0.075, ew=0.058, eh=0.066, bw=0.095, brow_y=0.160, brow=0, mouth_y=-0.110, mouth=mouth_a |
| boris_legs | legs2d.glsl | cx=0.06, cy=-0.06, s=0.30 |
| boris_neck | neck2d.glsl | cx=0.06, cy=-0.06, s=0.30, shoulders=1.12 |
| boris_body | body2d.glsl | cx=0.06, cy=-0.06, s=0.30, shoulders=1.12 |
| boris_hands | arms2d.glsl | cx=0.06, cy=-0.06, s=0.30, shoulders=1.12 |
| boris | head2d.glsl | cx=0.06, cy=-0.06, s=0.30, wide=1.10 |
| boris_hair | hair2d.glsl | cx=0.06, cy=-0.06, s=0.30, wide=1.10, fringe=0.20, style=1 |
| boris_eye | face2d.glsl | cx=0.06, cy=-0.06, s=0.34, kind=0, gap=0.135, eye_y=0.075, ew=0.056, eh=0.068, bw=0.100, brow_y=0.160, brow=0, mouth_y=-0.108, mouth=mouth_b |
| boris_pupil | face2d.glsl | cx=0.06, cy=-0.06, s=0.34, kind=3, gap=0.135, eye_y=0.075, ew=0.056, eh=0.068, bw=0.100, brow_y=0.160, brow=0, mouth_y=-0.108, mouth=mouth_b |
| boris_mouth | face2d.glsl | cx=0.06, cy=-0.06, s=0.34, kind=2, gap=0.135, eye_y=0.075, ew=0.056, eh=0.068, bw=0.100, brow_y=0.160, brow=0, mouth_y=-0.108, mouth=mouth_b |
| dora_legs | legs2d.glsl | cx=0.58, cy=-0.06, s=0.30 |
| dora_neck | neck2d.glsl | cx=0.58, cy=-0.06, s=0.30, shoulders=1.00 |
| dora_body | body2d.glsl | cx=0.58, cy=-0.06, s=0.30, shoulders=1.00 |
| dora_hands | arms2d.glsl | cx=0.58, cy=-0.06, s=0.30, shoulders=1.00 |
| dora | head2d.glsl | cx=0.58, cy=-0.06, s=0.30, wide=0.96 |
| dora_hair | hair2d.glsl | cx=0.58, cy=-0.06, s=0.30, wide=0.96, fringe=0.20, style=2 |
| dora_eye | face2d.glsl | cx=0.58, cy=-0.06, s=0.34, kind=0, gap=0.128, eye_y=0.075, ew=0.060, eh=0.064, bw=0.092, brow_y=0.160, brow=0, mouth_y=-0.112, mouth=mouth_d |
| dora_pupil | face2d.glsl | cx=0.58, cy=-0.06, s=0.34, kind=3, gap=0.128, eye_y=0.075, ew=0.060, eh=0.064, bw=0.092, brow_y=0.160, brow=0, mouth_y=-0.112, mouth=mouth_d |
| dora_mouth | face2d.glsl | cx=0.58, cy=-0.06, s=0.34, kind=2, gap=0.128, eye_y=0.075, ew=0.060, eh=0.064, bw=0.092, brow_y=0.160, brow=0, mouth_y=-0.112, mouth=mouth_d |
| ellis_legs | legs2d.glsl | cx=-0.78, cy=-0.06, s=0.30 |
| ellis_neck | neck2d.glsl | cx=-0.78, cy=-0.06, s=0.30, shoulders=0.92 |
| ellis_body | body2d.glsl | cx=-0.78, cy=-0.06, s=0.30, shoulders=0.92 |
| ellis_hands | arms2d.glsl | cx=-0.78, cy=-0.06, s=0.30, shoulders=0.92 |
| ellis | head2d.glsl | cx=-0.78, cy=-0.06, s=0.30, wide=1.02 |
| ellis_hair | hair2d.glsl | cx=-0.78, cy=-0.06, s=0.30, wide=1.02, fringe=0.20, style=3 |
| ellis_eye | face2d.glsl | cx=-0.78, cy=-0.06, s=0.34, kind=0, gap=0.130, eye_y=0.075, ew=0.056, eh=0.066, bw=0.098, brow_y=0.160, brow=0, mouth_y=-0.108, mouth=mouth_e |
| ellis_pupil | face2d.glsl | cx=-0.78, cy=-0.06, s=0.34, kind=3, gap=0.130, eye_y=0.075, ew=0.056, eh=0.066, bw=0.098, brow_y=0.160, brow=0, mouth_y=-0.108, mouth=mouth_e |
| ellis_mouth | face2d.glsl | cx=-0.78, cy=-0.06, s=0.34, kind=2, gap=0.130, eye_y=0.075, ew=0.056, eh=0.066, bw=0.098, brow_y=0.160, brow=0, mouth_y=-0.108, mouth=mouth_e |

The whole cast shares one paper-white skin; shirts, hair, trousers and silhouette
carry the difference. Aina narrow with a bowl cut, Boris broad with a flat top, Dora
long-haired, Ellis round and balding.

## Tracks

| name | kind | values | options |
|------|------|--------|---------|
