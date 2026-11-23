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

## 2D templates

Files ending in `2d.glsl` are used by `mode: 2d`. The contract is the same function
body, but `p` is **screen space**: the frame offset divided by frame height, so
`y = 0` is the centre, `-0.5` the bottom and `0.5` the top. Only `p.xy` is
meaningful. A 2D template returns the distance to a flat shape, not to a solid;
`dist` is in the same units as `p`.

Two rules matter in 2D:

- **One layer, one fill.** The renderer paints each layer a single colour, so a face
  or a piece of furniture is several templates (or several rows), not one shape with
  painted details.
- **No local named `t` or `table`.** Those shadow the shader's time parameter or a
  built-in and the shader fails to compile. `q`, `d` and `s` are safe.