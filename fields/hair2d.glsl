// Hair as its own layer, so it can be a different colour from the face.
//
// A cap over the skull, cut by a horizontal fringe line. Drawn after the head and before
// the features, which is the same stacking order an SVG document would use.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float wide = {{wide}};

float hair = length(q / vec2(0.355 * wide, 0.415)) - 1.0;
// Fringe: everything below the line is cut away.
hair = max(hair, -(q.y - {{fringe}}));
// Two sideburn tabs, so the cut does not look like a bowl.
hair = min(hair, length((q - vec2(-0.30 * wide, 0.10)) / vec2(0.075, 0.19)) - 1.0);
hair = min(hair, length((q - vec2(0.30 * wide, 0.10)) / vec2(0.075, 0.19)) - 1.0);
return hair * {{s}};