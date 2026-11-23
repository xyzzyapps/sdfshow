// A 2D table: a flat top on a slim pedestal. Furniture for the diner set.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};

float top = length((q - vec2(0.0, 0.0)) / vec2({{hw}}, 0.075)) - 1.0;
float stem = length((q - vec2(0.0, -0.30)) / vec2(0.055, 0.28)) - 1.0;
float foot = length((q - vec2(0.0, -0.58)) / vec2({{hw}} * 0.42, 0.045)) - 1.0;

return min(top, min(stem, foot)) * {{s}};