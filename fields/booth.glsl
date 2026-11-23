// A diner booth: two facing benches. The table is its own field, so this template only
// draws the seating.
//
// Note: no local may be named `t`, `p` or `q`-adjacent to the sign of the shader's own
// time parameter - a local `t` collides with `float t` in every field signature and the
// shader will not compile.
vec3 q = p - vec3({{cx}}, {{cy}}, {{cz}});
float side = {{flip}} > 0.5 ? -1.0 : 1.0;
float s = q.x * side;

// Bench: a seat slab...
vec3 seat = abs(vec3(s - 1.05, q.y + 0.44, q.z)) - vec3(0.36, 0.055, 0.40);
float bench = length(max(seat, 0.0)) + min(max(seat.x, max(seat.y, seat.z)), 0.0)
            - 0.035;

// ...and a backrest.
vec3 back = abs(vec3(s - 1.36, q.y + 0.10, q.z)) - vec3(0.055, 0.36, 0.40);
float backrest = length(max(back, 0.0)) + min(max(back.x, max(back.y, back.z)), 0.0)
               - 0.035;

return min(bench, backrest);