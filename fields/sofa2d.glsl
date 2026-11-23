// A 2D sofa: one low, wide silhouette so it reads as seating rather than a shape behind
// the cast's heads.
//
// The backrest is deliberately short and the whole thing sits low: in a scene where two
// people sit *on* the sofa, a tall backrest covers the people. `hw` is the half-width,
// `back` the backrest height above the seat.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};

// Seat cushion: wide and shallow.
float seat = length((q - vec2(0.0, 0.0)) / vec2({{hw}}, 0.19)) - 1.0;
// Backrest: a short riser behind the seat.
float back = length((q - vec2(0.0, {{back}})) / vec2({{hw}} * 0.95, 0.13)) - 1.0;
// Arms at both ends.
float arm_l = length((q - vec2(-{{hw}}, 0.06)) / vec2(0.12, 0.24)) - 1.0;
float arm_r = length((q - vec2({{hw}}, 0.06)) / vec2(0.12, 0.24)) - 1.0;

float sofa = min(seat, min(back, min(arm_l, arm_r)));
return sofa * {{s}};