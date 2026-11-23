// Two legs as one layer: a mirrored pair of thick blocks from the torso to the floor.
//
// A separate layer so they can be trousers while the arms are skin. Mirroring needs the
// `abs` on the *local* point inside the box formula; `abs(q.x) - 0.15` alone describes a
// box spanning -0.17..0.17, which merges the pair into one wide column.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};

vec2 leg = vec2(abs(q.x) - 0.15, q.y + 1.16);
vec2 lq = abs(leg) - vec2(0.08 - 0.06, 0.22 - 0.06);
float legs = length(max(lq, 0.0)) + min(max(lq.x, lq.y), 0.0) - 0.06;

return legs * {{s}};