// A ring of `count` columns at `ring` radius, using polar repetition. The local
// frame is exact near the ring: radial offset plus tangential arc offset.
float ang = atan(p.z, p.x);
float r = length(p.xz);
float cell = TAU / {{count}};
ang = mod(ang + 0.5 * cell, cell) - 0.5 * cell;
vec2 q = vec2(r * cos(ang) - {{ring}}, r * sin(ang));
float d = length(q) - {{radius}};
return max(d, abs(p.y - {{center_y}}) - {{half_height}});