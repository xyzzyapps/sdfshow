// A wavy ground plane. The sine displacement is not a true distance, so `shrink`
// pulls the estimate below the real distance (the marcher stays safe).
float w = {{amp}} * sin({{freq}} * p.x + t * {{speed}})
        * sin({{freq}} * p.z + t * {{speed}} * 0.7);
return ((p.y - {{level}}) - w) * {{shrink}};