// A 2D flat head: skull plus a hair cap, with no face features.
//
// Features are separate layers (`face2d.glsl`) so each can carry its own dark colour -
// in 2D mode a layer is one flat fill, so a face is drawn as stacked shapes rather than
// shaded. `wide` squashes or stretches the head so two characters read differently in
// silhouette even at a glance.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float wide = {{wide}};

// Skull.
float head = length(q / vec2(0.34 * wide, 0.40)) - 1.0;

// Hair: a slightly larger cap, cut by a horizontal fringe line.
float hair = length(q / vec2(0.355 * wide, 0.415)) - 1.0;
hair = max(hair, -(q.y - {{fringe}}));

// Neck and shoulders, so the head is attached to something.
float neck = length((q - vec2(0.0, -0.42)) / vec2(0.13, 0.26)) - 1.0;
float body = length((q - vec2(0.0, -0.92)) / vec2(0.60 * {{shoulders}}, 0.46)) - 1.0;

return min(min(head, neck), body) * {{s}};