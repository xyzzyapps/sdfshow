// Torus in the XZ plane. `spin` rotates it about Y; `tilt` leans it about X.
vec3 q = rotX(rotY(p, t * {{spin}}), {{tilt}});
return length(vec2(length(q.xz) - {{radius}}, q.y)) - {{thickness}};