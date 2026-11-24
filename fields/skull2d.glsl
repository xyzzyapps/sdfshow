// A 3/4 head silhouette: a cranium and a narrower jaw, not a circle.
//
// `w` and `h` are half-width and half-height in screen units. The jaw ellipse is narrower
// and lower, so the outline has cheekbones and a chin; a single oval reads as a cartoon
// head no matter what is drawn on it.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float w = {{w}};
float h = {{h}};
float cranium = length(q / vec2(w, h * 0.78)) - 1.0;
float jaw = length((q - vec2(0.0, -h * 0.55)) / vec2(w * 0.80, h * 0.52)) - 1.0;
return min(cranium, jaw) * {{s}};
