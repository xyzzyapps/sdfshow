// Hexagonal prism along Z. `radius` is the circumradius, `half_height` the
// half-depth. Exact distance (Inigo Quilez's hex prism).
vec3 q = abs(p - vec3({{cx}}, {{cy}}, {{cz}}));
const vec3 k = vec3(-0.8660254, 0.5, 0.57735);
q.xy -= 2.0 * min(dot(k.xy, q.xy), 0.0) * k.xy;
vec2 d = vec2(
    length(q.xy - vec2(clamp(q.x, -k.z * {{radius}}, k.z * {{radius}}), {{radius}}))
        * sign(q.y - {{radius}}),
    q.z - {{half_height}}
);
return min(max(d.x, d.y), 0.0) + length(max(d, 0.0));