// The letters of a speech bubble, as their own distance field.
//
// Generated per speaker (see sdfshow/dialog.py). The panel is a separate field, so the
// text can carry a darker material and read without relief shading.
//
// The text lives on an axis-aligned plane facing +z, at `cz + depth + gap`. A
// billboard would be more general, but a plane keeps the mapping to one scale factor,
// which is the part that has to be exactly right: `ts` converts cell units to world
// units, and `_ink` indexes characters in advance units.
vec3 c = vec3({{cx}}, {{cy}}, {{cz}});
float size = {{size}};

int line = {{speaker}}_live(t);
if (line < 0) return 1e9;

float ts = size * 0.22;
float width = {{speaker}}_width(line) * ts;
float half_w = 0.5 * width;
float half_h = 0.5 * ts;
float zf = {{cz}} + {{depth}} + 0.012;

// Cheap bound: the text's slab, wider and taller than the ink by a hair.
float bound = length(vec3(max(abs(p.x - {{cx}}) - half_w - 0.02, 0.0),
                          max(abs(p.y - ({{cy}} - 0.42 * ts + half_h)) - half_h - 0.02, 0.0),
                          max(abs(p.z - zf) - 0.012, 0.0)))
            + min(max(max(abs(p.x - {{cx}}) - half_w - 0.02,
                          abs(p.y - ({{cy}} - 0.42 * ts + half_h)) - half_h - 0.02),
                      abs(p.z - zf) - 0.012), 0.0);
if (sf_detail < 0.5) return bound;

// Cell space: the baseline sits `cy - 0.42*ts`, so cell y 0..1 spans the cap height.
vec2 cell = vec2((p.x - {{cx}}) / ts + half_w / ts, (p.y - ({{cy}} - 0.42 * ts)) / ts);
float ink = {{speaker}}_ink(cell, line) * ts - {{stroke}} * ts;

// A thin slab at the plane, so the letters have flat depth.
float layer = max(ink, abs(p.z - zf) - 0.008);
return layer;