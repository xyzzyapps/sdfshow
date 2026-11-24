// A field of stars: one dot per hash cell, so the sky needs no texture and no list.
//
// `s` is the cell size in screen units and `size` scales the dot. Each cell jitters its
// star inside the cell, so the grid does not read. The dots are barely 2-4 px at the
// pixel quantise used by the island scene, which is the point.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
vec2 cell = floor(q);
vec2 f = fract(q) - 0.5;
float jx = hash21(cell + vec2(1.3, 7.1)) - 0.5;
float jy = hash21(cell + vec2(9.7, 3.3)) - 0.5;
float r = (0.03 + 0.05 * hash21(cell + vec2(5.1, 11.7))) * {{size}};
return (length(f - vec2(jx, jy) * 0.6) - r) * {{s}};