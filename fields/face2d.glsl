// A single 2D face feature on its own layer: eyes, brows or mouth.
//
// Features are separate fields rather than part of the head, because in 2D mode each
// layer paints one flat colour - that is what gives the cutout look, and it is also how
// a pixel-art face is drawn (dark shapes on a light head, not shading).
//
// One template serves all three kinds. Every parameter it can touch is bound at the top
// because a kind that ignores a value still has to resolve it; and `kind` is compared as
// a float, since parameter substitution always emits a float literal (`0.0`, not `0`).
// `kind` 0 eyes, 1 brows, 2 mouth.
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
float open = 0.010 + {{mouth}} * 0.05;

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
float mouth_s = length((q - vec2(0.0, my)) / vec2(bwide, open)) - 1.0;
return mouth_s * {{s}};