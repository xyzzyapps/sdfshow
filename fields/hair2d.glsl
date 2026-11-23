// Hair as its own layer, so it can be a different colour from the face.
//
// Four styles, chosen by `style`, so a scene of four people does not look like four
// copies of one head:
//   0 short cap with a fringe
//   1 tall volume, swept up
//   2 long, falling past the shoulders
//   3 bald with a side band (no cap on top)
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float wide = {{wide}};
float style = {{style}};

if (style < 0.5) {
    float hair = length(q / vec2(0.355 * wide, 0.415)) - 1.0;
    hair = max(hair, -(q.y - {{fringe}}));
    hair = min(hair, length((q - vec2(-0.30 * wide, 0.10)) / vec2(0.075, 0.19)) - 1.0);
    hair = min(hair, length((q - vec2(0.30 * wide, 0.10)) / vec2(0.075, 0.19)) - 1.0);
    return hair * {{s}};
}
if (style < 1.5) {
    // Taller volume, swept up and back.
    float hair = length((q - vec2(0.03, 0.10)) / vec2(0.385 * wide, 0.50)) - 1.0;
    hair = max(hair, -(q.y - {{fringe}} - 0.10));
    return hair * {{s}};
}
if (style < 2.5) {
    // Long: a cap plus two lengths falling to the shoulders.
    float cap = length(q / vec2(0.355 * wide, 0.415)) - 1.0;
    cap = max(cap, -(q.y - {{fringe}}));
    float left = length((q - vec2(-0.34 * wide, -0.30)) / vec2(0.11, 0.55)) - 1.0;
    float right = length((q - vec2(0.34 * wide, -0.30)) / vec2(0.11, 0.55)) - 1.0;
    return min(cap, min(left, right)) * {{s}};
}
// Bald with a low band around the back of the skull.
float band = length(q / vec2(0.348 * wide, 0.408)) - 1.0;
band = max(band, -(q.y + 0.02));
band = min(band, length(vec2(q.x, q.y + 0.02) / vec2(0.36 * wide, 0.06)) - 1.0);
return band * {{s}};