# field templates

Each `.glsl` file is the **body** of a GLSL function

```
float field_<name>(vec3 p, float t) { <template> }
```

so it must end in `return <distance>;`. `p` is the sample point and `t` is show
time in seconds. `{{placeholder}}` holes are filled from the field's `parameters`
cell and from the globals at the top of `fields.md`.

Available without importing anything:

- `PI`, `TAU`, `BAR`, `BEAT`, `STEP`, `DUR`, `FPS`, `FRAMES`
- `rotX`, `rotY`, `rotZ`, `rot2`
- `smin`, `smax`
- `hash11`, `hash21`

Write over several indented lines for readability: blank lines and lines whose
first non-space character is `#` are ignored, and the remaining lines are joined
with one space. A line must not split a token. Use `//` for GLSL comments. A
template must return a true (or close to true) distance; an over-estimate makes the
raymarcher step through surfaces.