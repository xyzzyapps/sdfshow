// A stone arch: two pillars and a semicircular ring above the springing.
//
// `hw` is the half-span to the pillar centres and the radius of the ring, `thick` the
// stone width, `drop` how far the pillars run below the springing. The ring is clipped
// to y >= 0 so the opening stays open; the pillars are mirrored with abs on x.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float hw = {{hw}};
float thick = {{thick}};
float drop = {{drop}};

vec2 pq = vec2(abs(q.x) - hw, q.y + drop * 0.5);
vec2 pbox = abs(pq) - vec2(thick * 0.5, drop * 0.5);
float pillar = length(max(pbox, 0.0)) + min(max(pbox.x, pbox.y), 0.0) - thick * 0.10;

float ring = abs(length(q) - hw) - thick * 0.5;
ring = max(ring, -q.y);

return min(pillar, ring) * {{s}};