# fields - ops

## Fields

| name  | template   | parameters |
|-------|------------|------------|
| shell | sphere.glsl | radius=1.15, cx=0, cy=0, cz=0 |
| cube  | box.glsl   | cx=0, cy=0, cz=0, hx=chop, hy=chop, hz=chop, round=0.06 |
| ring  | torus.glsl | radius=0.85, thickness=0.12, spin=0.0, tilt=0.0 |

## Tracks

`span=2` makes the four values last two bars: one value per half-bar.

| name | kind  | values              | options              |
|------|-------|---------------------|----------------------|
| chop | steps | 0.9\|0.62\|1.0\|0.75 | span=2, ease=smooth |