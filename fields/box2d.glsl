// A flat rounded box for 2D mode. `round` is the corner radius, so `round = 0` is a
// crisp rectangle and a large `round` approaches an ellipse.
vec2 q = abs(p.xy - vec2({{cx}}, {{cy}})) - vec2({{hx}}, {{hy}}) + {{round}};
return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - {{round}};