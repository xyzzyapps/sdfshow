// Two arms and hands as one layer: a capsule from each shoulder to a round hand.
//
// They are their own layer so they can be skin while the torso is a shirt, and so they
// draw over the torso at the sides. The pair is mirrored from one side with abs on x.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float shoulders = {{shoulders}};

float ax = abs(q.x);
vec2 point = vec2(ax, q.y);
vec2 shoulder = vec2(0.28 * shoulders, -0.58);
vec2 hand = vec2(0.36 * shoulders, -0.90);
vec2 span = hand - shoulder;
float along = clamp(dot(point - shoulder, span) / dot(span, span), 0.0, 1.0);
float arm = length(point - shoulder - span * along) - 0.08;
float palm = length(point - hand) - 0.10;

return min(arm, palm) * {{s}};