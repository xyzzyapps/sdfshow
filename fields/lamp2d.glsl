// A 2D floor lamp: a slim stand, a shade, and a soft pool of light.
//
// `glow` widens the pool under the shade, which is what makes a living room read as lit
// rather than as flat shapes.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};

// Base, stand, shade.
float base = length((q - vec2(0.0, -0.02)) / vec2(0.16, 0.035)) - 1.0;
float stand = length((q - vec2(0.0, 0.34)) / vec2(0.022, 0.36)) - 1.0;
float shade = length((q - vec2(0.0, 0.76)) / vec2(0.20, 0.14)) - 1.0;
shade = max(shade, -(q.y - 0.90));

float lamp = min(base, min(stand, shade));
// Pool of light: a wide, flat ellipse on the floor.
float pool = length((q - vec2(0.0, 0.02)) / vec2(0.42 + {{glow}}, 0.22 + {{glow}} * 0.3)) - 1.0;
return min(lamp, pool) * {{s}};