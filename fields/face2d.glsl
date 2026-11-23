// One 2D face feature on its own layer: eyes, brows, mouth or pupils.
//
// A layer paints one flat colour, so a face is stacked: white sclera, dark pupils, a dark
// mouth. That is the cutout look - not shading, just shapes.
//
// One template serves every kind. Every parameter is bound at the top because a kind that
// ignores a value still has to resolve it; `kind` is compared as a float, since parameter
// substitution always emits a float literal (`0.0`, not `0`).
// `kind` 0 sclera, 1 brows, 2 mouth, 3 pupils.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float kind = {{kind}};

float gap = {{gap}};
float ewide = {{ew}};
float etall = {{eh}};
float ey = {{eye_y}};
float by = {{brow_y}};
float bwide = {{bw}};
float my = {{mouth_y}};
float lift = {{brow}} * 0.05;
// The mouth opens downward from a hinge at its top edge, so a talking character reads as
// a jaw dropping rather than a shape inflating around its centre.
float open = 0.020 + {{mouth}} * 0.10;

if (kind < 0.5) {
    float eyes = min(
        length((q - vec2(-gap, ey)) / vec2(ewide, etall)) - 1.0,
        length((q - vec2(gap, ey)) / vec2(ewide, etall)) - 1.0
    );
    return eyes * {{s}};
}
if (kind < 1.5) {
    float brows = min(
        length((q - vec2(-gap, by + lift)) / vec2(bwide, 0.016)) - 1.0,
        length((q - vec2(gap, by + lift)) / vec2(bwide, 0.016)) - 1.0
    );
    return brows * {{s}};
}
if (kind < 2.5) {
    // Top edge fixed at `my`, bottom edge at `my - 2*open`: the jaw drops.
    return (length((q - vec2(0.0, my - open)) / vec2(bwide, open)) - 1.0) * {{s}};
}
// Pupils: small dark discs inside each sclera, both looking slightly inward.
float pupils = min(
    length((q - vec2(-gap + 0.012, ey - etall * 0.05)) / vec2(ewide * 0.40, etall * 0.42)) - 1.0,
    length((q - vec2(gap - 0.012, ey - etall * 0.05)) / vec2(ewide * 0.40, etall * 0.42)) - 1.0
);
return pupils * {{s}};