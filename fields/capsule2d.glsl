// A flat capsule for 2D mode: the workhorse of pixel-art limbs, since a limb is a
// thick line with round ends.
vec2 pa = p.xy - vec2({{ax}}, {{ay}});
vec2 ba = vec2({{bx}}, {{by}}) - vec2({{ax}}, {{ay}});
float h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-6), 0.0, 1.0);
return length(pa - ba * h) - {{radius}};