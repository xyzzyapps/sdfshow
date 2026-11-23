// Capped cone along Y: radius r1 at the bottom, r2 at the top, half-height h.
// Exact distance (Inigo Quilez's capped cone).
vec2 q = vec2(length(p.xz - vec2({{cx}}, {{cz}})), p.y - {{cy}});
vec2 k1 = vec2({{r2}}, {{half_height}});
vec2 k2 = vec2({{r2}} - {{r1}}, 2.0 * {{half_height}});
vec2 ca = vec2(q.x - min(q.x, (q.y < 0.0) ? {{r1}} : {{r2}}), abs(q.y) - {{half_height}});
vec2 cb = q - k1 + k2 * clamp(dot(k1 - q, k2) / dot(k2, k2), 0.0, 1.0);
float s = (cb.x < 0.0 && ca.y < 0.0) ? -1.0 : 1.0;
return s * sqrt(min(dot(ca, ca), dot(cb, cb)));