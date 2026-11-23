// Capsule between (ax, ay, az) and (bx, by, bz).
vec3 a = vec3({{ax}}, {{ay}}, {{az}});
vec3 b = vec3({{bx}}, {{by}}, {{bz}});
vec3 pa = p - a;
vec3 ba = b - a;
float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
return length(pa - ba * h) - {{radius}};