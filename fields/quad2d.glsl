// A convex quad from four corners, in local units: a boot, a hat brim, a coat tail, a
// stone slab.
//
// Vertices must be counter-clockwise. The distance is the max of the four edge
// half-planes: exact along the edges and slightly short at the corners, which is all a
// flat fill and a rim need.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
vec2 v0 = vec2({{x0}}, {{y0}});
vec2 v1 = vec2({{x1}}, {{y1}});
vec2 v2 = vec2({{x2}}, {{y2}});
vec2 v3 = vec2({{x3}}, {{y3}});
float d0 = dot(q - v0, normalize(vec2(v1.y - v0.y, -(v1.x - v0.x))));
float d1 = dot(q - v1, normalize(vec2(v2.y - v1.y, -(v2.x - v1.x))));
float d2 = dot(q - v2, normalize(vec2(v3.y - v2.y, -(v3.x - v2.x))));
float d3 = dot(q - v3, normalize(vec2(v0.y - v3.y, -(v0.x - v3.x))));
return max(max(d0, d1), max(d2, d3)) * {{s}};
