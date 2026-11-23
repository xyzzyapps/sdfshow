// A ring of `count` spheres at `radius` from the Y axis, spinning about it.
//
// Order matters here. The sample point is folded into one angular sector *first*
// and the sphere is evaluated in that sector; the spin is applied to the ring
// afterwards. Doing it the other way round (rotating the point, then folding) makes
// the sphere drift away from the ray as time advances, which reads as a scene that
// silently disappears.
vec3 q = p - vec3({{cx}}, {{cy}}, {{cz}});
float cell = TAU / max({{count}}, 1.0);
float a = atan(q.z, q.x);
a = mod(a + 0.5 * cell, cell) - 0.5 * cell;
float r = length(q.xz);
vec3 f = vec3(r * cos(a), q.y, r * sin(a));
f = rotY(f, -t * {{spin}});
return length(f - vec3({{radius}}, 0.0, 0.0)) - {{orb}};