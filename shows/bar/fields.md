# fields - bar

Coordinates: the bar top is `y = 0`, the floor `y = -1.6`. Aina stands at `x = -1.2`,
Boris at `x = +1.2`, both facing the camera. The bubbles sit above and between them,
each tail pointing at its speaker.

## Fields

| name  | template   | parameters |
|-------|------------|------------|
| floor | plane_wave.glsl | amp=0, freq=1, speed=0, level=-1.6, shrink=1 |
| counter | box.glsl | cx=0, cy=-0.12, cz=-0.55, hx=4.2, hy=0.14, hz=0.5, round=0.04 |
| booth | capsule.glsl | ax=-3.0, ay=-1.5, az=-2.3, bx=3.0, by=-1.5, bz=-2.3, radius=0.9 |
| aina  | talker.glsl | cx=-1.15, cy=0.30, cz=0.55, facing=1, head=1.0, lean=-0.12, tilt=-0.05, mouth=mouth_a, brow=brow_a |
| boris | talker.glsl | cx=1.15, cy=0.30, cz=0.55, facing=1, head=1.0, lean=0.12, tilt=0.06, mouth=mouth_b, brow=brow_b |
| bub_a | bubble_aina.glsl | cx=-0.72, cy=1.42, cz=0.35, size=0.80, width=0.30, round=0.06, depth=0.03, tail=0.22, tail_x=-0.35, stroke=0.10 |
| bub_b | bubble_boris.glsl | cx=0.72, cy=1.42, cz=0.35, size=0.80, width=0.30, round=0.06, depth=0.03, tail=0.22, tail_x=0.35, stroke=0.10 |
| inka | bubble_aina_ink.glsl | cx=-0.72, cy=1.42, cz=0.35, size=0.80, depth=0.03, stroke=0.10 |
| inkb | bubble_boris_ink.glsl | cx=0.72, cy=1.42, cz=0.35, size=0.80, depth=0.03, stroke=0.10 |

## Tracks

No tracks here. The camera tracks live in `show.md` next to the Stage table, and the
acting tracks (`mouth_a`, `mouth_b`, `brow_a`, `brow_b`) are merged from both files.