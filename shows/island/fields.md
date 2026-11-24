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
| sea_glow | box2d.glsl | cx=-0.20, cy=-0.07, hx=0.50, hy=0.006, round=0.0 |
| far_cliff | ellipse2d.glsl | cx=-0.55, cy=-0.10, rx=0.55, ry=0.22 |
| arch_open_low | panel2d.glsl | cx=0.55, cy=-0.18, s=1.0, hx=0.150, hy=0.120, round=0.0, rot=0.0, cut=9.0, axis=0, side=1 |
| arch_open_top | tone2d.glsl | cx=0.55, cy=-0.06, s=1.0, rx=0.150, ry=0.160, rot=0.0, cut=0.0, axis=1, side=-1 |
| arch_lit | arch2d.glsl | cx=0.535, cy=-0.048, s=0.55, hw=0.42, thick=0.26, drop=0.95 |
| arch | arch2d.glsl | cx=0.55, cy=-0.06, s=0.55, hw=0.42, thick=0.26, drop=0.95 |
| arch_shadow | arch2d.glsl | cx=0.565, cy=-0.075, s=0.55, hw=0.42, thick=0.26, drop=0.95 |
| ledge | box2d.glsl | cx=0, cy=-0.42, hx=1.60, hy=0.12, round=0.06 |
| ledge_lip | box2d.glsl | cx=0, cy=-0.315, hx=1.60, hy=0.012, round=0.006 |
| glow1 | ellipse2d.glsl | cx=-0.31, cy=-0.295, rx=0.28, ry=0.09 |
| glow2 | ellipse2d.glsl | cx=-0.33, cy=-0.288, rx=0.15, ry=0.05 |
| logs | ellipse2d.glsl | cx=-0.30, cy=-0.30, rx=0.075, ry=0.028 |
| flame | fire2d.glsl | cx=-0.31, cy=-0.25, s=0.11, wide=0.50, tall=0.95, speed=9.0 |
| core | fire2d.glsl | cx=-0.31, cy=-0.27, s=0.05, wide=0.45, tall=0.70, speed=11.0 |
| stairs1 | box2d.glsl | cx=0.66, cy=-0.300, hx=0.11, hy=0.010, round=0.003 |
| stairs2 | box2d.glsl | cx=0.71, cy=-0.312, hx=0.08, hy=0.010, round=0.003 |
| stairs3 | box2d.glsl | cx=0.75, cy=-0.324, hx=0.06, hy=0.010, round=0.003 |
| path1 | quad2d.glsl | cx=-0.08, cy=-0.332, s=1.0, x0=-0.090, y0=-0.016, x1=0.090, y1=-0.016, x2=0.060, y2=0.016, x3=-0.065, y3=0.016 |
| path2 | quad2d.glsl | cx=0.20, cy=-0.338, s=1.0, x0=-0.070, y0=-0.012, x1=0.070, y1=-0.012, x2=0.046, y2=0.012, x3=-0.050, y3=0.012 |
| rock_left | box2d.glsl | cx=-0.80, cy=-0.48, hx=0.35, hy=0.08, round=0.08 |

A figure is a stack of shapes in two or three tones: trousers and boots, a shirt with a
lit panel and a shadow panel, arms and hands, a head with a lit cheek, a shadow cheek and
a chin, hair with a highlight, then sclera, pupils and mouth.

## Tracks

| name | kind | values | options |
|------|------|--------|---------|
