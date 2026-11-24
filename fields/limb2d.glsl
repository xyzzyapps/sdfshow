// A rotated capsule: an arm, a leg or a lock of hair.
//
// The capsule runs along the local x axis for `2*len`, with radius `wide`, rotated by
// `rot` radians. `taper` narrows the +x end, so an arm or a leg is not a tube. A limb is two numbers and an angle rather than a fixed template, which
// is what lets a character stand at an angle instead of facing the camera.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float a = {{rot}};
float ca = cos(a), sa = sin(a);
vec2 r = vec2(ca * q.x + sa * q.y, -sa * q.x + ca * q.y);
float rad = {{wide}} * (1.0 - {{taper}} * clamp((r.x / {{len}} + 1.0) * 0.5, 0.0, 1.0));
float d = length(vec2(max(abs(r.x) - {{len}}, 0.0), r.y)) - rad;
return d * {{s}};
