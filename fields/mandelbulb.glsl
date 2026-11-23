// Mandelbulb distance estimate. Opt-in: six iterations of pow/acos/atan per
// field evaluation is expensive, so use it in a quiet scene.
vec3 q = p - vec3({{cx}}, {{cy}}, {{cz}});
vec3 z = q;
float dr = 1.0;
float r = 0.0;
for (int i = 0; i < {{iterations}}; i++) {
    r = length(z);
    if (r > 2.0) break;
    float theta = acos(clamp(z.z / max(r, 1e-6), -1.0, 1.0));
    float phi = atan(z.y, z.x);
    dr = pow(r, {{power}} - 1.0) * {{power}} * dr + 1.0;
    float zr = pow(r, {{power}});
    theta *= {{power}};
    phi *= {{power}};
    z = zr * vec3(sin(theta) * cos(phi), sin(theta) * sin(phi), cos(theta));
    z += q;
}
return 0.5 * log(max(r, 1e-6)) * r / dr;