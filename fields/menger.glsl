// Menger sponge: a cube with three levels of cross-shaped holes. The classic
// folded formulation (after Inigo Quilez), in world units.
vec3 q = rotY(p - vec3({{cx}}, {{cy}}, {{cz}}), t * {{spin}});
vec3 a = abs(q);
float d = length(max(a - vec3({{half}}), 0.0))
        + min(max(a.x, max(a.y, a.z)) - {{half}}, 0.0);
float s = 1.0;
for (int i = 0; i < {{iterations}}; i++) {
    vec3 c = mod(q * s, 2.0) - 1.0;
    s *= 3.0;
    vec3 r = abs(1.0 - 3.0 * abs(c));
    float da = max(r.x, r.y);
    float db = max(r.y, r.z);
    float dc = max(r.z, r.x);
    d = max(d, (min(da, min(db, dc)) - 1.0) / s);
}
return d;