// A flat ellipse, for 2D mode. `cx`/`cy` are screen coordinates (x right, y up, both
// divided by the frame height, so y = 0 is the vertical centre and x = 0 is central).
// `rx`/`ry` are radii in the same units. Not rounded, not shaded: a flat shape.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / vec2({{rx}}, {{ry}});
return (length(q) - 1.0) * min({{rx}}, {{ry}});