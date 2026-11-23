// Gyroid shell clipped to a sphere. `shrink` keeps the approximate distance
// under the true one, so the raymarcher cannot step through the surface.
vec3 q = rotY(p, t * {{spin}});
float g = dot(sin(q * {{scale}}), cos(q.yzx * {{scale}}));
float shell = abs(g) / {{scale}} * {{shrink}} - {{thickness}};
return max(shell, length(q) - {{radius}});