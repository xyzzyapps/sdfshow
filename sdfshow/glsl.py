"""Assemble the complete libplacebo/GLSL shader for a show.

The generated shader is one ``//!HOOK MAIN`` fragment hook. Time is derived from the
frame index (``float t = float(frame) / FPS``), so every frame is a pure function of
its index: renders are seekable and a still frame is exactly the frame the video
would contain.

Pieces, in order: constants and helpers, generated tracks and field functions, the
section-aware scene function (``map_scene``), the material pass, the raymarcher and
shading, and ``hook()``.
"""

from __future__ import annotations

import colorsys

from . import config as C
from .fields import Fields, render_functions
from .show import Show, pattern_id
from .tracks import expression, num

_SMIN = """\
float smin(float a, float b, float k) {
    if (k <= 0.0) return min(a, b);
    float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
    return mix(b, a, h) - k * h * (1.0 - h);
}
float smax(float a, float b, float k) { return -smin(-a, -b, k); }
"""

_TRANSFORMS = """\
vec2 rot2(vec2 p, float a) {
    float c = cos(a), s = sin(a);
    return mat2(c, -s, s, c) * p;
}
vec3 rotX(vec3 p, float a) {
    float c = cos(a), s = sin(a);
    return vec3(p.x, c * p.y - s * p.z, s * p.y + c * p.z);
}
vec3 rotY(vec3 p, float a) {
    float c = cos(a), s = sin(a);
    return vec3(c * p.x + s * p.z, p.y, -s * p.x + c * p.z);
}
vec3 rotZ(vec3 p, float a) {
    float c = cos(a), s = sin(a);
    return vec3(c * p.x - s * p.y, s * p.x + c * p.y, p.z);
}
"""

_HASH = """\
float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}
float hash11(float n) { return fract(sin(n * 127.1) * 43758.5453); }
"""

_PATTERN = """\
// Surface patterns. `pat` is 0 none, 1 checker, 2 grid, 3 stripes.
vec3 apply_pattern(int pat, float scale, vec3 c, vec3 p) {
    if (pat == 1) {
        float ch = mod(floor(p.x * scale) + floor(p.z * scale), 2.0);
        c *= mix(1.0, 0.22, ch);
    } else if (pat == 2) {
        vec2 f = abs(fract(p.xz * scale) - 0.5);
        float line = smoothstep(0.44, 0.5, max(f.x, f.y));
        c *= 1.0 - 0.8 * line;
    } else if (pat == 3) {
        float s = step(0.5, fract(p.y * scale));
        c *= mix(1.0, 0.3, s);
    }
    return c;
}
// Rotate a colour around the grey axis (cheap demoscene colour cycling).
vec3 hue_rotate(vec3 c, float a) {
    const vec3 k = vec3(0.57735);
    float ca = cos(a);
    return c * ca + cross(k, c) * sin(a) + k * dot(k, c) * (1.0 - ca);
}
"""

_NOISE = """\
float hash13(vec3 p) {
    p = fract(p * 0.1031);
    p += dot(p, p.yzx + 33.33);
    return fract((p.x + p.y) * p.z);
}
float vnoise(vec3 p) {
    vec3 i = floor(p);
    vec3 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float n000 = hash13(i + vec3(0.0, 0.0, 0.0));
    float n100 = hash13(i + vec3(1.0, 0.0, 0.0));
    float n010 = hash13(i + vec3(0.0, 1.0, 0.0));
    float n110 = hash13(i + vec3(1.0, 1.0, 0.0));
    float n001 = hash13(i + vec3(0.0, 0.0, 1.0));
    float n101 = hash13(i + vec3(1.0, 0.0, 1.0));
    float n011 = hash13(i + vec3(0.0, 1.0, 1.0));
    float n111 = hash13(i + vec3(1.0, 1.0, 1.0));
    float nx00 = mix(n000, n100, f.x);
    float nx10 = mix(n010, n110, f.x);
    float nx01 = mix(n001, n101, f.x);
    float nx11 = mix(n011, n111, f.x);
    return mix(mix(nx00, nx10, f.y), mix(nx01, nx11, f.y), f.z);
}
float fbm(vec3 p) {
    float sum = 0.0;
    float amp = 0.5;
    for (int i = 0; i < 4; i++) {
        sum += amp * vnoise(p);
        p = p * 2.03 + 11.7;
        amp *= 0.5;
    }
    return sum;
}
"""


def _fold(mode: str, count: float) -> str:
    """Generate the space fold applied before every field."""
    if mode == "none":
        return "vec3 fold_space(vec3 p) { return p; }\n"
    if mode == "mirror":
        return (
            "vec3 fold_space(vec3 p) {\n"
            "    p.x = abs(p.x);\n"
            "    p.z = abs(p.z);\n"
            "    return p;\n"
            "}\n"
        )
    return (
        "vec3 fold_space(vec3 p) {\n"
        "    float a = atan(p.z, p.x);\n"
        "    float r = length(p.xz);\n"
        f"    float sector = TAU / {num(count)};\n"
        "    a = mod(a + 0.5 * sector, sector) - 0.5 * sector;\n"
        "    a = abs(a);\n"
        "    p.x = cos(a) * r;\n"
        "    p.z = sin(a) * r;\n"
        "    return p;\n"
        "}\n"
    )


def _f(value: str, where: str) -> str:
    """A GLSL float literal from a stage value."""
    try:
        return num(float(value))
    except ValueError as exc:
        raise SystemExit(
            f"show.md: stage '{where}' must be a number (got '{value}')"
        ) from exc


def _vec3(value: str, where: str) -> str:
    """A ``r|g|b`` stage value as a GLSL ``vec3`` constructor."""
    parts = [p.strip() for p in value.split("|") if p.strip()]
    if len(parts) != 3:
        raise SystemExit(f"show.md: stage '{where}' must be r|g|b (got '{value}')")
    return "vec3(" + ", ".join(_f(p, where) for p in parts) + ")"


def _motion(show: Show, fields: Fields, key: str) -> str:
    """A stage value as a GLSL expression (a number, a track, or arithmetic)."""
    raw = show.stage_value(key)
    if not raw:
        raise SystemExit(f"show.md: stage '{key}' has no default and no value")
    return expression(raw, fields.tracks)


def _material_colour(index: int, name: str, show: Show) -> str:
    """A field's colour: explicit in ``## Materials``, else a golden-angle default."""
    material = show.materials.get(name)
    if material is not None:
        return "vec3(" + ", ".join(num(c) for c in material.color) + ")"
    hue = (index * 0.61803398875) % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.55, 1.0)
    return f"vec3({num(r)}, {num(g)}, {num(b)})"


def _section_chain(show: Show, fields: Fields, material: bool = False) -> str:
    """The nested ``if`` over the arrangement, shared by map and material passes."""
    bar = show.clock.bar
    order = show.fields_order
    by_name = fields.by_name()
    lines: list[str] = []
    for index, section in enumerate(show.sections):
        last = index == len(show.sections) - 1
        if not last:
            head = f"{'if' if index == 0 else '} else if'} (t < {num(section.hi * bar)}) {{"
        else:
            head = "} else {" if index else "{"
        lines.append(head)
        if material:
            for field_name in order:
                cell = section.cells[field_name]
                if cell.op != "u":
                    continue
                field_index = order.index(field_name)
                fn = by_name[field_name].function
                lines.append(f"    float dd{field_index} = {fn}(p, t);")
                lines.append(
                    f"    if (dd{field_index} < best) {{ best = dd{field_index}; "
                    f"id = {field_index}; }}"
                )
            continue
        base = True
        for field_name in order:
            cell = section.cells[field_name]
            if not cell.active:
                continue
            fn = by_name[field_name].function
            if base:
                lines.append(f"    d = {fn}(p, t);")
                base = False
            elif cell.op == "u":
                lines.append(f"    d = smin(d, {fn}(p, t), {num(cell.k)});")
            elif cell.op == "s":
                lines.append(f"    d = smax(d, -{fn}(p, t), {num(cell.k)});")
            elif cell.op == "i":
                lines.append(f"    d = smax(d, {fn}(p, t), {num(cell.k)});")
        if base:
            lines.append("    d = 1e9;")
    lines.append("}")
    return "\n".join(lines)


def assemble(show: Show, fields: Fields) -> str:
    """Build the complete shader source for *show*."""
    clock = show.clock
    order = show.fields_order
    colours = [_material_colour(index, name, show) for index, name in enumerate(order)]
    patterns = [
        pattern_id(show.materials[name].pattern) if name in show.materials else 0
        for name in order
    ]
    scales = [
        show.materials[name].scale if name in show.materials else 1.0 for name in order
    ]

    defines = "\n".join(
        [
            f"#define FPS {num(float(clock.fps))}",
            f"#define BAR {num(clock.bar)}",
            f"#define BEAT {num(clock.beat)}",
            f"#define STEP {num(clock.step)}",
            f"#define DUR {num(clock.duration)}",
            f"#define FRAMES {clock.frames}",
            "#define PI 3.14159265358979",
            "#define TAU 6.28318530717959",
            "#ifndef TIME0",
            "#define TIME0 0.0",
            "#endif",
        ]
    )

    stage = {
        key: _motion(show, fields, key)
        for key in ("distance", "yaw", "pitch", "fov", "fog", "exposure")
    }
    post = {
        key: _motion(show, fields, key)
        for key in ("scanlines", "plasma", "grain", "vignette", "hue")
    }
    target = _vec3(show.stage_value("target"), "target")
    light = _vec3(show.stage_value("light"), "light")
    background = _vec3(show.stage_value("background"), "background")

    camera = f"""\
vec3 camera_target(float t) {{
    return {target};
}}
vec3 camera_position(float t) {{
    float dist = {stage["distance"]};
    float yaw = {stage["yaw"]};
    float pitch = {stage["pitch"]};
    return camera_target(t) + dist * vec3(
        cos(pitch) * sin(yaw), sin(pitch), cos(pitch) * cos(yaw)
    );
}}
vec3 camera_ray(vec2 uv, float t) {{
    vec3 ro = camera_position(t);
    vec3 ta = normalize(camera_target(t) - ro);
    vec3 right = normalize(cross(ta, vec3(0.0, 1.0, 0.0)));
    vec3 up = cross(right, ta);
    return normalize(uv.x * right + uv.y * up + {stage["fov"]} * ta);
}}
"""

    scene = f"""\
float map_scene(vec3 p, float t) {{
    p = fold_space(p);
    float d = 1e9;
{_section_chain(show, fields)}
    return d;
}}
int mat_id(vec3 p, float t) {{
    int id = 0;
    float best = 1e9;
{_section_chain(show, fields, material=True)}
    return id;
}}
vec3 mat_color(int id, vec3 p, float t) {{
    vec3 c[{len(colours)}] = vec3[{len(colours)}](
        {", ".join(colours)}
    );
    int ptn[{len(colours)}] = int[{len(colours)}]({", ".join(str(x) for x in patterns)});
    float scl[{len(colours)}] = float[{len(colours)}](
        {", ".join(num(x) for x in scales)}
    );
    int i = clamp(id, 0, {len(colours) - 1});
    vec3 base = apply_pattern(ptn[i], scl[i], c[i], p);
    return hue_rotate(base, {post["hue"]});
}}
"""

    shading = f"""\
vec3 calc_normal(vec3 p, float t) {{
    const float e = {C.SURFACE_EPS:.6g};
    vec2 h = vec2(1.0, -1.0);
    return normalize(
        h.xyy * map_scene(p + h.xyy * e, t) +
        h.yyx * map_scene(p + h.yyx * e, t) +
        h.yxy * map_scene(p + h.yxy * e, t) +
        h.xxx * map_scene(p + h.xxx * e, t)
    );
}}
float calc_ao(vec3 p, vec3 n, float t) {{
    float occ = 0.0;
    float sca = 1.0;
    for (int i = 0; i < {C.AO_STEPS}; i++) {{
        float h = 0.012 + 0.13 * float(i) / float({C.AO_STEPS - 1});
        float dd = map_scene(p + n * h, t);
        occ += (h - dd) * sca;
        sca *= 0.82;
    }}
    return clamp(1.0 - 2.2 * occ, 0.0, 1.0);
}}
float soft_shadow(vec3 ro, vec3 rd, float t) {{
    float res = 1.0;
    float d = 0.02;
    for (int i = 0; i < {C.SHADOW_STEPS}; i++) {{
        float h = map_scene(ro + rd * d, t);
        res = min(res, 8.0 * h / d);
        d += clamp(h, 0.01, 0.25);
        if (res < 0.004 || d > 12.0) break;
    }}
    return clamp(res, 0.0, 1.0);
}}
vec3 post(vec3 col, vec2 uv, vec2 screen, float t) {{
    col *= clamp(1.0 - {post["vignette"]} * dot(uv, uv), 0.0, 1.0);
    float sl = 0.5 + 0.5 * sin(screen.y * PI);
    col *= 1.0 - {post["scanlines"]} * sl;
    float pl = sin(uv.x * 7.0 + t * 1.7)
             + sin(uv.y * 8.0 - t * 1.3)
             + sin((uv.x + uv.y) * 5.0 + t * 0.9);
    col += {post["plasma"]} * (0.5 + 0.5 * sin(pl * 1.5 + t)) * vec3(0.15, 0.35, 0.6);
    return col;
}}
vec3 render(vec2 uv, float t) {{
    vec3 ro = camera_position(t);
    vec3 rd = camera_ray(uv, t);
    vec3 bg = {background};
    float travel = 0.0;
    float hit = 0.0;
    for (int i = 0; i < {C.MARCH_STEPS}; i++) {{
        vec3 p = ro + rd * travel;
        float s = map_scene(p, t);
        if (s < 0.0) break;  // the camera started inside geometry
        if (s < {C.SURFACE_EPS:.6g} + 0.0006 * travel) {{ hit = 1.0; break; }}
        travel += s;
        if (travel > 48.0) break;
    }}
    vec3 col = bg;
    if (hit > 0.5) {{
        vec3 p = ro + rd * travel;
        vec3 fp = fold_space(p);
        vec3 base = mat_color(mat_id(fp, t), fp, t);
        vec3 n = calc_normal(p, t);
        float ao = calc_ao(p, n, t);
        vec3 l = normalize({light});
        float diff = clamp(dot(n, l), 0.0, 1.0);
        float sh = soft_shadow(p + n * 0.003, l, t);
        float rim = pow(1.0 - clamp(dot(n, -rd), 0.0, 1.0), 3.0);
        vec3 hv = normalize(l - rd);
        float spec = pow(clamp(dot(n, hv), 0.0, 1.0), 48.0);
        col = base * (0.08 + 0.92 * diff * sh) * ao;
        col += vec3(1.0) * spec * 0.35 * sh;
        col += base * rim * 0.30;
        float fog = clamp(1.0 - exp(-{stage["fog"]} * travel), 0.0, 0.85);
        col = mix(col, bg, fog);
    }}
    col *= {stage["exposure"]};
    col = col / (1.0 + col);
    col = pow(max(col, 0.0), vec3(0.4545));
    return col;
}}
"""

    hook = f"""\
//!HOOK MAIN
//!BIND HOOKED
//!DESC {show.name}
// @TIME0@

{defines}

{_SMIN}
{_HASH}
{_PATTERN}
{_NOISE}
{_TRANSFORMS}
{_fold(show.stage_value("fold").strip().lower(), float(show.stage_value("fold_count")))}

{render_functions(fields)}

{scene}
{camera}
{shading}

vec4 hook() {{
    vec2 res = target_size;
    vec2 uv = (HOOKED_pos * res - 0.5 * res) / res.y;
    uv.y = -uv.y;  // texture rows run top-down; put +y up
    float t = (float(frame) + TIME0) / FPS;
    vec3 col = render(uv, t);
    col = post(col, uv, HOOKED_pos * res, t);
    float g = hash21(HOOKED_pos * res + float(frame)) - 0.5;
    col += g * {post["grain"]};
    return vec4(col, 1.0);
}}
"""
    return hook


_EFFECT_DEFAULTS: dict[str, dict[str, str]] = {
    "bloom": {"threshold": "0.55", "strength": "0.8", "radius": "2.0"},
    "chroma": {"amount": "0.05"},
    "crt": {"curvature": "0.12"},
    "glitch": {"amount": "0.06", "rate": "9.0", "chance": "0.08"},
}


def _effect_num(name: str, params: dict[str, str], key: str) -> str:
    """One numeric effect parameter with its default applied."""
    raw = params.get(key, _EFFECT_DEFAULTS[name][key])
    try:
        return num(float(raw))
    except ValueError as exc:
        raise SystemExit(
            f"show.md: effect '{name}' parameter '{key}' must be a number"
        ) from exc


def assemble_effect(name: str, params: dict[str, str], clock) -> str:
    """Build one libplacebo post-pass shader.

    Effect passes read the previous pass through ``HOOKED_tex``; they never touch
    the SDF. ``TIME0`` is injected into every pass so animated effects (glitch)
    stay seekable.
    """
    if name == "bloom":
        body = f"""\
    vec4 c = HOOKED_tex(HOOKED_pos);
    float lum = dot(c.rgb, vec3(0.2126, 0.7152, 0.0722));
    vec3 b = vec3(0.0);
    float wsum = 0.0;
    for (int y = -2; y <= 2; y++) {{
        for (int x = -2; x <= 2; x++) {{
            vec2 o = vec2(float(x), float(y)) * {_effect_num(name, params, "radius")};
            float w = 1.0 / (1.0 + dot(o, o));
            b += HOOKED_texOff(o).rgb * w;
            wsum += w;
        }}
    }}
    b /= wsum;
    float k = smoothstep({_effect_num(name, params, "threshold")}, 1.0, lum);
    return vec4(c.rgb + b * k * {_effect_num(name, params, "strength")}, 1.0);
"""
    elif name == "chroma":
        body = f"""\
    vec4 c = HOOKED_tex(HOOKED_pos);
    vec2 d = HOOKED_pos - 0.5;
    vec2 o = d * dot(d, d) * {_effect_num(name, params, "amount")};
    vec3 col;
    col.r = HOOKED_tex(HOOKED_pos + o).r;
    col.g = c.g;
    col.b = HOOKED_tex(HOOKED_pos - o).b;
    return vec4(col, 1.0);
"""
    elif name == "crt":
        body = f"""\
    vec2 d = HOOKED_pos - 0.5;
    float r2 = dot(d, d);
    vec2 pos = 0.5 + d * (1.0 + {_effect_num(name, params, "curvature")} * r2);
    if (pos.x < 0.0 || pos.x > 1.0 || pos.y < 0.0 || pos.y > 1.0) {{
        return vec4(0.0, 0.0, 0.0, 1.0);
    }}
    return HOOKED_tex(pos);
"""
    elif name == "glitch":
        body = f"""\
    float t = (float(frame) + TIME0) / FPS;
    float band = floor(HOOKED_pos.y * 28.0);
    float tick = floor(t * {_effect_num(name, params, "rate")});
    float n = hash11(band * 1.37 + tick * 7.1);
    vec2 pos = HOOKED_pos;
    if (n > 1.0 - {_effect_num(name, params, "chance")}) {{
        pos.x += (hash11(band + tick * 3.3) - 0.5) * {_effect_num(name, params, "amount")};
    }}
    vec3 col;
    col.r = HOOKED_tex(pos + vec2(0.0015, 0.0)).r;
    col.g = HOOKED_tex(pos).g;
    col.b = HOOKED_tex(pos - vec2(0.0015, 0.0)).b;
    return vec4(col, 1.0);
"""
    else:
        raise SystemExit(f"unknown effect '{name}'")

    return f"""\
//!HOOK MAIN
//!BIND HOOKED
//!DESC effect: {name}
// @TIME0@

#define FPS {num(float(clock.fps))}
#ifndef TIME0
#define TIME0 0.0
#endif

float hash11(float n) {{ return fract(sin(n * 127.1) * 43758.5453); }}

vec4 hook() {{
{body}}}
"""
