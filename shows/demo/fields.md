# fields - demo

## Fields

| name    | template      | parameters |
|---------|---------------|------------|
| tunnel  | tunnel.glsl   | spacing=1.6, offset=0.8, radius=1.25, thickness=0.055, twist=tunnel_twist |
| menger  | menger.glsl   | cx=0, cy=-0.28, cz=0, half=1.0, spin=menger_spin, iterations=3 |
| gyroid  | gyroid.glsl   | spin=gyro_spin, scale=5.5, shrink=0.55, thickness=0.06, radius=1.4 |
| sun     | sphere.glsl   | radius=1.05, cx=0, cy=0.55, cz=0 |
| pillars | pillars.glsl  | ring=4.2, count=12, radius=0.22, center_y=-0.1, half_height=1.6 |
| floor   | plane_wave.glsl | amp=0, freq=1, speed=0, level=-1.3, shrink=1 |

## Tracks

Camera moves and per-scene motion. `keys` are bar:value points; `expr` is raw GLSL
over `t`. The Stage table in `show.md` refers to these by name.

| name         | kind | values | options     |
|--------------|------|--------|-------------|
| dolly        | keys | 0:1.7\|4:1.7\|4.35:6.8\|8:6.2\|8.35:6.6\|12:7.2\|12.35:8.5\|16:8.2 | ease=smooth |
| yaw          | keys | 0:0.0\|4:0.0\|4.35:0.9\|8:2.4\|8.35:3.2\|12:4.2\|12.35:4.9\|16:5.8 | ease=smooth |
| pitch        | keys | 0:-0.02\|4:-0.02\|4.35:-0.14\|8:-0.12\|8.35:-0.13\|12:-0.09\|12.35:-0.06\|16:-0.03 | ease=smooth |
| fov          | keys | 0:1.55\|4:1.55\|4.35:1.95\|8:1.85\|8.35:1.95\|12:1.75\|12.35:1.7\|16:1.9 | ease=smooth |
| fog          | keys | 0:0.02\|4:0.02\|4.35:0.09\|8:0.06\|8.35:0.05\|12:0.06\|12.35:0.11\|16:0.08 | ease=smooth |
| hue          | expr | 0.22*sin(t*0.5) | |
| gyro_spin    | expr | 0.3*t | |
| menger_spin  | expr | 0.25*t | |
| tunnel_twist | expr | 0.25+0.1*sin(t*0.6) | |