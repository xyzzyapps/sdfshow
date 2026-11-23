// A diner coffee cup and saucer, small enough to sit on a table.
vec3 q = p - vec3({{cx}}, {{cy}}, {{cz}});

// Cup: a cylinder with a hollowed interior.
float outer = length(vec2(length(q.xz) - 0.075, max(abs(q.y - 0.055) - 0.055, 0.0))) - 0.012;
float inner = length(vec2(length(q.xz) - 0.062, max(abs(q.y - 0.058) - 0.052, 0.0))) - 0.010;
float cup = max(outer, -inner);
cup = max(cup, -(q.y - 0.108));

// Handle: a torus on the -x side, half buried in the cup.
vec3 h = q - vec3(-0.082, 0.055, 0.0);
float handle = length(vec2(length(h.xy) - 0.042, h.z)) - 0.011;

// Saucer.
float saucer = length(vec2(length(q.xz) - 0.115, max(abs(q.y - 0.012) - 0.010, 0.0))) - 0.010;
saucer = max(saucer, -(q.y - 0.004));

return min(min(cup, handle), saucer);