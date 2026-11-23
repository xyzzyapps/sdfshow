// A 2D sofa: one thick silhouette, softened at the joins.
//
// Seat, back and arms are three rounded blocks merged with a smooth minimum, so the eye
// sees one object with soft corners rather than three separate cushions. The backrest is
// short on purpose: in a scene where people sit on the sofa, a tall back covers them.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};

float seat = length((q - vec2(0.0, 0.0)) / vec2({{hw}}, 0.21)) - 1.0;
float back = length((q - vec2(0.0, {{back}})) / vec2({{hw}} * 0.96, 0.15)) - 1.0;
float arm_l = length((q - vec2(-{{hw}}, 0.04)) / vec2(0.13, 0.26)) - 1.0;
float arm_r = length((q - vec2({{hw}}, 0.04)) / vec2(0.13, 0.26)) - 1.0;

float body = smin(seat, back, 0.12);
body = smin(body, min(arm_l, arm_r), 0.10);
return body * {{s}};