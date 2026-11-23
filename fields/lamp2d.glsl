// A 2D floor lamp: a trapezoid shade, a thick stand, a small base.
//
// Three blocks, one colour. The soft pool of light the first version drew was a fourth
// block the same colour as the lamp, which read as a puddle rather than as light; in a
// cutout scene lighting is a colour choice, not a shape.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};

// Shade: a flat-bottomed oval, which reads as a paper shade at this size. The cut keeps
// the half below y = 0.90: `max(shade, q.y - 0.90)` is negative there, and the two
// operands intersect. Negating the cut (as the first version did) removed the shade
// entirely and left a floating pole.
float shade = length((q - vec2(0.0, 0.74)) / vec2(0.24 + {{glow}} * 0.4, 0.13)) - 1.0;
shade = max(shade, q.y - 0.90);

// Stand and base.
vec2 sq = abs(q - vec2(0.0, 0.30)) - vec2(0.04 - 0.02, 0.32 - 0.02);
float stand = length(max(sq, 0.0)) + min(max(sq.x, sq.y), 0.0) - 0.02;
vec2 bq = abs(q - vec2(0.0, -0.02)) - vec2(0.16 - 0.04, 0.05 - 0.04);
float base = length(max(bq, 0.0)) + min(max(bq.x, bq.y), 0.0) - 0.04;

return min(shade, min(stand, base)) * {{s}};