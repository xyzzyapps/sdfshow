// A speech bubble facing the camera, with its text carved into it.
//
// Everything is a distance field, so the bubble catches light, casts a shadow and
// moves with the camera like any other field. The text is a stroke font (see
// sdfshow/glyphs.py): every glyph is a chain of capsules, and only the glyph under
// the sample is evaluated, so cost does not grow with line length.
//
// Performance note. A glyph is a switch over dozens of capsules, which is far more
// expensive than a sphere. It must therefore never run inside the raymarch loop: the
// bubble first returns a cheap panel-slab bound, and only the material pass - which
// runs once per pixel at the hit point - asks for the ink. `{{speaker}}_live` gates
// the whole field, so a bubble that is not on screen costs one comparison.
vec3 c = vec3({{cx}}, {{cy}}, {{cz}});
float size = {{size}};

int line = {{speaker}}_live(t);
if (line < 0) return 1e9;

vec3 view = normalize(camera_position(t) - c);
vec3 right = normalize(cross(vec3(0.0, 1.0, 0.0), view));
vec3 up = cross(view, right);
vec3 rel = p - c;
vec3 f = vec3(dot(rel, right), dot(rel, up), dot(rel, view));

float ts = size * 0.22;
// One text cell is 1.0 tall and FONT_ADV wide; the panel is that plus padding, so
// the glyphs are framed rather than clipped.
float ph = 0.5 * (ts * 1.0 + ts * 0.85);
float pw = max(0.5 * ({{speaker}}_width(line) * ts + ts * 0.85), {{width}});
float depth = {{depth}};

// Cheap bound: an oriented box, no text. It must enclose the tail as well, or the
// marcher will treat the tail's space as empty and the detailed pass never runs there.
float bound = length(max(abs(f) - vec3(pw, ph + {{tail}}, depth), 0.0))
            + min(max(max(abs(f.x) - pw, abs(f.y) - ph - {{tail}}),
                      abs(f.z) - depth), 0.0);

// Detailed surface: panel, tail, ink. Only evaluated once per pixel, at the hit.
if (sf_detail < 0.5) return bound;

float panel = length(max(abs(f.xy) - vec2(pw, ph), 0.0))
            + min(max(abs(f.x) - pw, abs(f.y) - ph), 0.0)
            - {{round}};

// Tail: a triangle hanging under the panel, in panel units scaled by ts.
float tx = {{tail_x}} * pw;
float tail = seg2(f.xy,
                  vec2(tx - 0.20 * ts, -ph + 0.5 * ts),
                  vec2(tx + 0.20 * ts, -ph + 0.5 * ts),
                  vec2(tx + {{tail_x}} * 0.30 * ts, -ph - {{tail}}));
panel = min(panel, tail);

vec2 cell = vec2((f.x + 0.5 * {{speaker}}_width(line) * ts) / ts, (f.y + 0.425 * ts) / ts);
float ink = {{speaker}}_ink(cell, line) * ts - {{stroke}} * ts;

// The panel is a plain slab. The letters are a *separate field* with their own darker
// material (see gen/<show>/bubble_<speaker>_ink.glsl): a relief of the same colour
// would need shadowing to read, whereas a second field composites through the normal
// material path and is legible at any size.
float slab = max(panel, abs(f.z) - depth);
return slab;