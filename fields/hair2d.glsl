// Hair as its own layer, so it can be a different colour from the face.
//
// Four cutout styles, chosen by `style`, so four heads do not read as one:
//   0 a bowl cap with a straight fringe
//   1 a flat top, cut high and square
//   2 a cap with two long panels down to the jaw
//   3 bald on top, with a low ring at the sides and back
//
// `fringe` is the lowest q.y the cap reaches. It must stay above the eye line (the eye
// layer sits near q.y = 0.08), or the cap covers the face - which is what made the first
// version read as one dark mass.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float wide = {{wide}};
float style = {{style}};

float cap = length(q / vec2(0.415 * wide, 0.475)) - 1.0;
cap = max(cap, -(q.y - {{fringe}}));

if (style < 0.5) {
    // Bowl: the cap with no extra volume.
    return cap * {{s}};
}
if (style < 1.5) {
    // Flat top: a rounded cap that sits on the crown, cut at the fringe. The local cannot
    // be called `flat` - that is a GLSL interpolation qualifier and the shader will not
    // compile.
    vec2 hq = abs(q - vec2(0.0, 0.22)) - vec2(0.40 * wide - 0.10, 0.26 - 0.10);
    float top = length(max(hq, 0.0)) + min(max(hq.x, hq.y), 0.0) - 0.10;
    return max(top, -(q.y - {{fringe}})) * {{s}};
}
if (style < 2.5) {
    // Long: the cap plus a panel at each side, falling to the jaw.
    float left = length((q - vec2(-0.38 * wide, -0.16)) / vec2(0.10, 0.40)) - 1.0;
    float right = length((q - vec2(0.38 * wide, -0.16)) / vec2(0.10, 0.40)) - 1.0;
    return min(cap, min(left, right)) * {{s}};
}
// Bald: a grey patch at each temple, clipped to the skull so it reads as hair on the
// head rather than a pair of earmuffs. A ring around the skull was too heavy at this size.
float left = length((q - vec2(-0.29 * wide, 0.14)) / vec2(0.10, 0.14)) - 1.0;
float right = length((q - vec2(0.29 * wide, 0.14)) / vec2(0.10, 0.14)) - 1.0;
float skull = length(q / vec2(0.40 * wide, 0.46)) - 1.0;
return max(min(left, right), skull) * {{s}};