// Sphere. `radius` may be a number, a track name, or arithmetic over tracks.
vec3 q = p - vec3({{cx}}, {{cy}}, {{cz}});
return length(q) - {{radius}};