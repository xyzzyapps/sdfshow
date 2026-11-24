// A short neck, drawn behind the shirt so only the part between chin and collar shows.
//
// The neck is its own layer: drawn after the head it painted a white column down the
// chest and read as a beard; drawn before the torso it is covered at the bottom and the
// head covers the top, leaving a collar's width of neck.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float shoulders = {{shoulders}};

return (length((q - vec2(0.0, -0.52)) / vec2(0.14 * shoulders, 0.20)) - 1.0) * {{s}};
