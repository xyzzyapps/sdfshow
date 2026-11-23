// Capped cylinder along Y.
vec2 d = abs(vec2(length(p.xz - vec2({{cx}}, {{cz}})), p.y - {{cy}}))
       - vec2({{radius}}, {{half_height}});
return min(max(d.x, d.y), 0.0) + length(max(d, 0.0));