# fields - island

Screen space for `mode: 2d`: `y = 0` is the centre, `-0.5` the bottom, `0.5` the top;
`x` runs about -0.89..0.89 at 16:9. `zoom`/`focus_*` push in on the same stack.

## Fields

| name | template | parameters |
|------|----------|------------|
| sky | box2d.glsl | cx=0, cy=0.10, hx=1.60, hy=1.00, round=0.0 |
| stars | stars2d.glsl | cx=0, cy=0.10, s=0.055, size=1.0 |
| moon | ellipse2d.glsl | cx=-0.30, cy=0.33, rx=0.050, ry=0.050 |
| sea | box2d.glsl | cx=0, cy=-0.14, hx=1.60, hy=0.12, round=0.0 |
| far_cliff | ellipse2d.glsl | cx=-0.55, cy=-0.10, rx=0.55, ry=0.22 |
| arch | arch2d.glsl | cx=0.55, cy=-0.06, s=0.55, hw=0.42, thick=0.26, drop=0.95 |
| ledge | box2d.glsl | cx=0, cy=-0.42, hx=1.60, hy=0.12, round=0.06 |
| logs | ellipse2d.glsl | cx=-0.30, cy=-0.30, rx=0.075, ry=0.028 |
| flame | fire2d.glsl | cx=-0.31, cy=-0.25, s=0.11, wide=0.50, tall=0.95, speed=9.0 |
| core | fire2d.glsl | cx=-0.31, cy=-0.27, s=0.05, wide=0.45, tall=0.70, speed=11.0 |
| pirate_legs | legs2d.glsl | cx=-0.50, cy=0.02, s=0.24 |
| pirate_neck | neck2d.glsl | cx=-0.50, cy=0.02, s=0.24, shoulders=1.02 |
| pirate_body | body2d.glsl | cx=-0.50, cy=0.02, s=0.24, shoulders=1.02 |
| pirate_hands | arms2d.glsl | cx=-0.50, cy=0.02, s=0.24, shoulders=1.02 |
| pirate | head2d.glsl | cx=-0.50, cy=0.02, s=0.24, wide=1.04 |
| pirate_hair | hair2d.glsl | cx=-0.50, cy=0.02, s=0.24, wide=1.04, fringe=0.20, style=0 |
| pirate_eye | face2d.glsl | cx=-0.50, cy=0.02, s=0.27, kind=0, gap=0.130, eye_y=0.075, ew=0.056, eh=0.066, bw=0.098, brow_y=0.160, brow=0, mouth_y=-0.108, mouth=mouth_b |
| pirate_pupil | face2d.glsl | cx=-0.50, cy=0.02, s=0.27, kind=3, gap=0.130, eye_y=0.075, ew=0.056, eh=0.066, bw=0.098, brow_y=0.160, brow=0, mouth_y=-0.108, mouth=mouth_b |
| pirate_mouth | face2d.glsl | cx=-0.50, cy=0.02, s=0.27, kind=2, gap=0.130, eye_y=0.075, ew=0.056, eh=0.066, bw=0.098, brow_y=0.160, brow=0, mouth_y=-0.108, mouth=mouth_b |
| kid_legs | legs2d.glsl | cx=0.38, cy=0.02, s=0.23 |
| kid_neck | neck2d.glsl | cx=0.38, cy=0.02, s=0.23, shoulders=0.92 |
| kid_body | body2d.glsl | cx=0.38, cy=0.02, s=0.23, shoulders=0.92 |
| kid_hands | arms2d.glsl | cx=0.38, cy=0.02, s=0.23, shoulders=0.92 |
| kid | head2d.glsl | cx=0.38, cy=0.02, s=0.23, wide=0.92 |
| kid_hair | hair2d.glsl | cx=0.38, cy=0.02, s=0.23, wide=0.92, fringe=0.20, style=1 |
| kid_eye | face2d.glsl | cx=0.38, cy=0.02, s=0.26, kind=0, gap=0.125, eye_y=0.075, ew=0.058, eh=0.066, bw=0.095, brow_y=0.160, brow=0, mouth_y=-0.110, mouth=mouth_a |
| kid_pupil | face2d.glsl | cx=0.38, cy=0.02, s=0.26, kind=3, gap=0.125, eye_y=0.075, ew=0.058, eh=0.066, bw=0.095, brow_y=0.160, brow=0, mouth_y=-0.110, mouth=mouth_a |
| kid_mouth | face2d.glsl | cx=0.38, cy=0.02, s=0.26, kind=2, gap=0.125, eye_y=0.075, ew=0.058, eh=0.066, bw=0.095, brow_y=0.160, brow=0, mouth_y=-0.110, mouth=mouth_a |
| rock_left | box2d.glsl | cx=-0.80, cy=-0.48, hx=0.35, hy=0.08, round=0.08 |

Two figures, ten layers each: trousers, neck, shirt, arms and hands, head, hair, sclera,
pupils, mouth.

## Tracks

| name | kind | values | options |
|------|------|--------|---------|
