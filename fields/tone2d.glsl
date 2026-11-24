// A rotated half-ellipse: one tone of a two-tone shape.
//
// `axis` 0 cuts vertically, 1 horizontally. `cut` is where the boundary sits and `side`
// picks the kept half (+1 keeps the coordinate below the cut, -1 above it). Drawn over
// the base shape at the same size, the hard edge is the light boundary - which is how
// pixel art shades a face or a coat with two fills instead of a gradient.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float a = {{rot}};
float ca = cos(a), sa = sin(a);
vec2 r = vec2(ca * q.x + sa * q.y, -sa * q.x + ca * q.y);
float d = length(r / vec2({{rx}}, {{ry}})) - 1.0;
float edge = ({{axis}} < 0.5) ? {{side}} * (r.x - {{cut}}) : {{side}} * (r.y - {{cut}});
return max(d, edge) * {{s}};
