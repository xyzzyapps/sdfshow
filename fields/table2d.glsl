// A 2D table: one thick slab on one thick pedestal.
//
// Furniture in a cutout scene is a colour block with a rounded corner, not a modelled
// object. The foot the first version had was a third shape at this size - invisible, and
// it only made the silhouette busy.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};

vec2 tq = abs(q) - vec2({{hw}} - 0.06, 0.09 - 0.06);
float top = length(max(tq, 0.0)) + min(max(tq.x, tq.y), 0.0) - 0.06;

vec2 pq = abs(q - vec2(0.0, -0.34)) - vec2(0.07 - 0.03, 0.34 - 0.03);
float stem = length(max(pq, 0.0)) + min(max(pq.x, pq.y), 0.0) - 0.03;

return min(top, stem) * {{s}};