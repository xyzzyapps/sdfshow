// A flat cutout head: a big skull, a short neck, a small rounded body.
//
// The silhouette is the character. A cutout cartoon reads by head-to-body ratio, so the
// skull is deliberately large and the torso small; `wide` and `shoulders` vary that ratio
// so four people are distinguishable from shape alone, before colour.
//
// Hair and features are separate layers (`hair2d.glsl`, `face2d.glsl`) because in 2D mode
// one layer paints one flat colour.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float wide = {{wide}};

// Skull: a tall oval, not a circle - a circle reads as a ball, an oval reads as a face.
float head = length(q / vec2(0.40 * wide, 0.46)) - 1.0;

// Neck: short and thick, so the head is attached rather than floating.
float neck = length((q - vec2(0.0, -0.45)) / vec2(0.15, 0.20)) - 1.0;

// Body: a rounded block (a coat), narrower than the head so the head reads as the
// character. A body as wide as the skull reads as a box, not a person.
vec2 bq = abs(q - vec2(0.0, -0.86)) - vec2(0.34 * {{shoulders}} - 0.12, 0.30);
float body = length(max(bq, 0.0)) + min(max(bq.x, bq.y), 0.0) - 0.12;

return min(head, min(neck, body)) * {{s}};