// A 2D window: an opaque pane with a frame and muntins drawn on it.
//
// In a flat 2D scene a window is a filled rectangle, not a hole - a cut-out would show
// the background through the glass. Three shapes on one layer: the pane, a border around
// its edge, and a cross of muntins.
vec2 q = (p.xy - vec2({{cx}}, {{cy}})) / {{s}};
float part = {{part}};

float pane = length(q / vec2({{hw}}, {{hh}})) - 1.0;
float inner = length(q / vec2({{hw}} - 0.16, {{hh}} - 0.16)) - 1.0;
float border = max(pane, -inner);
float mh = length(q / vec2({{hw}}, 0.055)) - 1.0;
float mv = length(q / vec2(0.055, {{hh}})) - 1.0;

// `part` 0 is the glass (a flat fill), 1 is the frame and muntins, drawn as a separate
// darker layer on top. Splitting them is what lets the frame read at a coarse pixel
// grid: one layer is one colour, so the frame needs its own.
if (part < 0.5) return pane * {{s}};
return min(border, min(mh, mv)) * {{s}};