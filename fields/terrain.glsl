// Noise terrain: a ground plane displaced by 4-octave value noise. `shrink`
// keeps the estimate conservative because the displacement is not a distance.
float h = {{amp}} * (fbm(vec3(p.x * {{freq}}, {{offset}}, p.z * {{freq}})) - 0.5);
return ((p.y - {{level}}) - h) * {{shrink}};