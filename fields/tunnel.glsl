// A repeating ring tunnel along Z. `offset` places the ring planes; the two
// nearest planes are evaluated so the distance is a valid bound (a single mod()
// would overestimate near a cell boundary).
float s = {{spacing}};
float z0 = mod(p.z - {{offset}} + 0.5 * s, s) - 0.5 * s;
float z1 = z0 > 0.0 ? z0 - s : z0 + s;
vec2 a = rot2(p.xy, z0 * {{twist}});
vec2 b = rot2(p.xy, z1 * {{twist}});
float d0 = length(vec2(length(a) - {{radius}}, z0)) - {{thickness}};
float d1 = length(vec2(length(b) - {{radius}}, z1)) - {{thickness}};
return min(d0, d1);