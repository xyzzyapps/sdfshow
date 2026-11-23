// A flat cutout head: one big oval skull and nothing else.
//
// No neck. The head layer is drawn over the torso, so any neck would paint a white
// column across the shirt - which read as a beard. A cutout head sits directly on the
// shoulders, and the overlap is enough to look attached.
//
// `wide` changes the skull, so four people are distinguishable from shape alone, before
// colour. The torso, arms and legs are separate layers (`body2d`, `arms2d`, `legs2d`).
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float wide = {{wide}};

// Skull: a tall oval, not a circle - a circle reads as a ball, an oval reads as a face.
return (length(q / vec2(0.40 * wide, 0.46)) - 1.0) * {{s}};