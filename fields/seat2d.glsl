// A 2D booth bench: one flat band behind the cast.
//
// No backrest. A backrest tall enough to see is tall enough to cover the people sitting
// on it, and in a pixel-art scene of four heads the furniture should read as a single
// horizontal band, not as shapes competing with faces.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float seat = length(q / vec2({{hw}}, {{hh}})) - 1.0;
return seat * {{s}};