// Rounded box centred at (cx, cy, cz) with half-extents (hx, hy, hz).
vec3 q = abs(p - vec3({{cx}}, {{cy}}, {{cz}})) - vec3({{hx}}, {{hy}}, {{hz}});
return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0) - {{round}};