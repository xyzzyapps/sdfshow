# fields - reel

## Fields

| name    | template      | parameters |
|---------|---------------|------------|
| tunnel  | tunnel.glsl   | spacing=1.6, offset=0.8, radius=1.25, thickness=0.055, twist=tunnel_twist |
| menger  | menger.glsl   | cx=0, cy=-0.35, cz=0, half=0.9, spin=menger_spin, iterations=3 |
| gyroid  | gyroid.glsl   | spin=gyro_spin, scale=5.5, shrink=0.55, thickness=0.075, radius=1.35 |
| orbs    | spheres.glsl  | cx=0, cy=0.2, cz=0, spacing=1.3, radius=orb_r, count=1, spin=0, orb=orb_sz |
| sun     | sphere.glsl   | radius=1.1, cx=0, cy=0.5, cz=0 |
| pillars | pillars.glsl  | ring=4.4, count=14, radius=0.2, center_y=-0.05, half_height=1.7 |
| floor   | plane_wave.glsl | amp=0, freq=1, speed=0, level=-1.35, shrink=1 |

## Tracks

| name         | kind | values | options |
|--------------|------|--------|---------|
| tunnel_twist | expr | 0.22+0.09*sin(t*0.5) | |
| menger_spin  | expr | 0.22*t | |
| gyro_spin    | expr | 0.28*t | |
| orb_r        | expr | 1.15+0.09*sin(t*1.1) | |
| orb_sz       | expr | 0.44+0.04*sin(t*1.7) | |