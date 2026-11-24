// A flat 2D flame: a wobbling oval with a smaller tip on top.
//
// `speed` sets the flicker rate and `sway` the sideways drift; the tip is a second oval
// so the silhouette is a teardrop rather than a balloon. Draw a second instance in a
// warmer colour at a smaller scale for the core.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float sway = 0.06 * sin(t * {{speed}} + q.y * 2.0);
vec2 f = q - vec2(sway, 0.0);

float body = length(f / vec2({{wide}}, {{tall}})) - 1.0;
float tip = length((f - vec2(0.0, {{tall}} * 0.95)) / vec2({{wide}} * 0.55, {{tall}} * 0.55)) - 1.0;

return min(body, tip) * {{s}};