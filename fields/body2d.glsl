// A cutout torso: one rounded block, the shirt.
//
// The head, arms and legs are separate layers, so body parts need not share a colour:
// the torso carries the shirt, the arms carry skin, the legs carry trousers. That is the
// same one-fill-per-layer rule that makes the face five rows.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float shoulders = {{shoulders}};

vec2 bq = abs(q - vec2(0.0, -0.76)) - vec2(0.34 * shoulders - 0.10, 0.20 - 0.10);
float body = length(max(bq, 0.0)) + min(max(bq.x, bq.y), 0.0) - 0.10;

return body * {{s}};