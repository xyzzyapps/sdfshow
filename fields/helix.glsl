// Helical tube around Y. The space is repeated on `pitch` and rotated by the
// local height, then a sphere is subtracted at radius `radius`. The twist makes
// the estimate approximate, so `shrink` must be below 1.
vec3 q = p - vec3({{cx}}, {{cy}}, {{cz}});
float y = mod(q.y + 0.5 * {{pitch}}, {{pitch}}) - 0.5 * {{pitch}};
float ang = y * (TAU / {{pitch}}) * {{turn}};
q.xz = rot2(q.xz, ang);
return (length(q - vec3({{radius}}, 0.0, 0.0)) - {{tube}}) * {{shrink}};