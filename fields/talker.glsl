// A talker: a head-and-shoulders figure. `mouth` opens the mouth, `brow` lifts the
// brows, `tilt` leans the head, `lean` turns the shoulders, `shape` fattens the head.
//
// Layout is in figure-local units with the origin at the chest: the body capsule spans
// roughly y = -0.9 .. 0.0, the neck 0.0 .. 0.1, and the head is centred at y = 0.36.
//
// The figure is deliberately simple - body, neck, head, hair, eyes, brows, mouth -
// because at 720p it reads through silhouette and one hard key light, not detail.
vec3 q = p - vec3({{cx}}, {{cy}}, {{cz}});

// Body: a rounded capsule from the seat to the shoulders, flattened front-to-back so it
// reads as a torso rather than a pill.
float body = length(vec3(q.x * 1.05, max(abs(q.y + 0.52) - 0.40, 0.0), q.z * 1.12))
           - 0.38;

// Neck: a short cylinder, so the head sits on something.
float neck = length(vec3(q.x, max(abs(q.y - 0.03) - 0.10, 0.0), q.z * 1.12)) - 0.125;

// Head, leaning and tilting.
vec3 h = q - vec3(0.0, 0.36, 0.0);
h = rotZ(rotX(h, {{lean}}), {{tilt}});
float head = length(vec3(h.x, h.y / {{shape}}, h.z)) - 0.27;

// Hair: a cap over the top and back of the head, cut at the brow line.
float hair = length(vec3(h.x, h.y - 0.035, h.z) / 1.035) - 0.274;
hair = max(hair, -(h.y + 0.055));

// Eyes: small spheres proud of the face, so they catch a highlight.
float eye_y = 0.045 + {{brow}} * 0.018;
float eyes = min(
    length(h - vec3(-0.098, eye_y, 0.232)) - 0.037,
    length(h - vec3(0.098, eye_y, 0.232)) - 0.037
);
// Brows: thin capsules that lift with `brow`.
float brows = min(
    length(vec3((h.x + 0.098) * 0.85, (h.y - 0.132 - {{brow}} * 0.045) * 3.4,
                h.z - 0.232)) - 0.028,
    length(vec3((h.x - 0.098) * 0.85, (h.y - 0.132 - {{brow}} * 0.045) * 3.4,
                h.z - 0.232)) - 0.028
);

// Mouth: a small crater, taller as `mouth` opens.
float m_open = 0.014 + {{mouth}} * 0.050;
vec3 m = h - vec3(0.0, -0.078, 0.242);
float mouth_d = length(vec3(m.x * 2.4, m.y * 2.4, m.z * 1.5)) - m_open;

float figure = min(body, neck);
figure = min(figure, head);
figure = min(figure, hair);
figure = smin(figure, eyes, 0.02);
figure = smin(figure, brows, 0.015);
figure = max(figure, -mouth_d);
return figure;