// A 2D flat head: skull, neck and shoulders, with no hair or features.
//
// Hair and features are separate layers (`hair2d.glsl`, `face2d.glsl`) so each can carry
// its own flat colour - in 2D mode a layer is one fill, so a face is drawn as stacked
// shapes rather than shaded. `wide` and `shoulders` change the silhouette so four
// characters stay distinguishable even in a crowd.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float wide = {{wide}};

// Skull.
float head = length(q / vec2(0.34 * wide, 0.40)) - 1.0;

// Neck and shoulders, so the head is attached to something.
float neck = length((q - vec2(0.0, -0.42)) / vec2(0.13, 0.26)) - 1.0;
float body = length((q - vec2(0.0, -0.92)) / vec2(0.60 * {{shoulders}}, 0.46)) - 1.0;

return min(head, min(neck, body)) * {{s}};