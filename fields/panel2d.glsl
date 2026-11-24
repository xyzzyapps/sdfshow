// A rounded box clipped by one axis: the lit or shadow panel of a coat.
//
// Same cut/side convention as `tone2d`. Passing a large cut and side 1 disables the clip,
// so the template can also be a plain box.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float a = {{rot}};
float ca = cos(a), sa = sin(a);
vec2 r = vec2(ca * q.x + sa * q.y, -sa * q.x + ca * q.y);
vec2 bq = abs(r) - vec2({{hx}} - {{round}}, {{hy}} - {{round}});
float d = length(max(bq, 0.0)) + min(max(bq.x, bq.y), 0.0) - {{round}};
float edge = ({{axis}} < 0.5) ? {{side}} * (r.x - {{cut}}) : {{side}} * (r.y - {{cut}});
return max(d, edge) * {{s}};
