// A talker: a head-and-shoulders figure. `mouth` opens the mouth, `brow` lifts the
// brows, `tilt` leans the head, `lean` turns the shoulders. All are tracks, so the
// figure reads as speaking.
//
// Layout is in figure-local units with the origin at the chest: the body capsule
// spans roughly y = -0.9 .. 0.0, the neck 0.0 .. 0.1, and the head is centred at
// y = 0.34 with radius 0.28.
vec3 q = p - vec3({{cx}}, {{cy}}, {{cz}});

// Body: a rounded capsule from the seat to the shoulders.
float body = length(vec3(q.x, max(abs(q.y + 0.52) - 0.40, 0.0), q.z * 1.12)) - 0.38;

// Neck: a short cylinder, so the head does not float.
float neck = length(vec3(q.x, max(abs(q.y - 0.03) - 0.10, 0.0), q.z * 1.12)) - 0.13;

// Head, leaning and tilting.
vec3 h = q - vec3(0.0, 0.36, 0.0);
h = rotZ(rotX(h, {{lean}}), {{tilt}});
float head = length(vec3(h.x, h.y / {{head}}, h.z)) - 0.27;

// Hair: a slightly larger cap over the top and back of the head.
float hair = length(vec3(h.x, h.y - 0.04, h.z) / 1.03) - 0.272;
hair = max(hair, -(h.y + 0.06));

// Face features, in head-local space, on the +z side.
float eye_y = 0.05 + {{brow}} * 0.02;
float eyes = min(
    length(h - vec3(-0.095, eye_y, 0.235)) - 0.036,
    length(h - vec3(0.095, eye_y, 0.235)) - 0.036
);
// Brows: flattened capsules that lift with `brow`.
float brows = min(
    length(vec3((h.x + 0.095) * 0.9, (h.y - 0.135 - {{brow}} * 0.05) * 3.2,
                h.z - 0.235)) - 0.030,
    length(vec3((h.x - 0.095) * 0.9, (h.y - 0.135 - {{brow}} * 0.05) * 3.2,
                h.z - 0.235)) - 0.030
);

// Mouth: a small crater, taller as `mouth` opens.
float m_open = 0.012 + {{mouth}} * 0.055;
vec3 m = h - vec3(0.0, -0.075, 0.245);
float mouth_d = length(vec3(m.x * 2.6, m.y * 2.6, m.z * 1.6)) - m_open;

float figure = min(body, neck);
figure = min(figure, head);
figure = min(figure, hair);
figure = smin(figure, eyes, 0.02);
figure = smin(figure, brows, 0.015);
figure = max(figure, -mouth_d);
return figure;