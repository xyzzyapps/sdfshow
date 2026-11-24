# show - island

A night scene in the grammar of a 1990s pixel-art adventure: a cliff above the sea, a
stone arch, a campfire, two figures, and the line being spoken as a caption at the top of
the frame rather than in a speech balloon.

`mode: 2d` paints flat layers back to front. The pixel quantise is on (`pixel: 3`), so the
whole frame lands on a 3-pixel grid - that is the look, not an artefact. `bubble: caption`
turns the dialogue into white outlined type with no panel.

The scene is an homage, not a copy: original characters and lines, drawn from the same
shape vocabulary as `shows/pixel`.

bpm: 96
# Eleven bars: the last line ends at bar 11, and the show stops there.
bars: auto
fps: 30
size: 1280x720

## Stage

| key           | value            |
|---------------|------------------|
| mode          | 2d               |
| pixel         | 2                |
| outline       | 0.003            |
| outline_color | 0.02\|0.02\|0.04 |
| exposure      | 1.0              |
| background    | 0.04\|0.05\|0.12 |
| vignette      | 0.35             |
| scanlines     | 0.0              |
| grain         | 0.015            |
| hue           | 0                |
| zoom          | 1.0              |
| focus_x       | 0.0              |
| focus_y       | -0.02            |
| bubble        | caption          |
| font          | 0.024            |
| panel         | 1.0              |

The camera is one slow push (`zoom` rises with time) rather than cuts, because this is one
continuous shot.

## Fields

Back to front. Sky, stars, sea and cliff; then the arch, the ledge, the fire; then the two
figures; then a foreground rock.

| field |
|-------|
| sky |
| stars |
| moon |
| sea |
| sea_glow |
| far_cliff |
| arch_open_low |
| arch_open_top |
| arch_lit |
| arch |
| arch_shadow |
| ledge |
| ledge_lip |
| glow1 |
| glow2 |
| logs |
| flame |
| core |
| stairs1 |
| stairs2 |
| stairs3 |
| path1 |
| path2 |
| rock_left |

## Materials

Night palette: deep blue sky, stone lit dimly by the fire, a warm flame against it.

| field | color | pattern | scale | rim |
|-------|-------|---------|-------|-----|
| sky | 0.045\|0.055\|0.140 | none | 1.0 | 0 |
| stars | 0.86\|0.90\|1.0 | none | 1.0 | 0 |
| moon | 0.93\|0.90\|0.76 | none | 1.0 | 1 |
| sea | 0.06\|0.09\|0.20 | none | 1.0 | 1 |
| sea_glow | 0.20\|0.23\|0.34 | none | 1.0 | 0 |
| far_cliff | 0.09\|0.10\|0.18 | none | 1.0 | 1 |
| arch_open_low | 0.04\|0.04\|0.07 | none | 1.0 | 0 |
| arch_open_top | 0.04\|0.04\|0.07 | none | 1.0 | 0 |
| arch_lit | 0.35\|0.32\|0.32 | none | 1.0 | 1 |
| arch | 0.30\|0.29\|0.33 | none | 1.0 | 1 |
| arch_shadow | 0.25\|0.24\|0.28 | none | 1.0 | 1 |
| ledge | 0.14\|0.12\|0.16 | none | 1.0 | 1 |
| ledge_lip | 0.26\|0.21\|0.20 | none | 1.0 | 1 |
| glow1 | 0.18\|0.10\|0.08 | none | 1.0 | 0 |
| glow2 | 0.22\|0.12\|0.08 | none | 1.0 | 0 |
| logs | 0.22\|0.13\|0.09 | none | 1.0 | 1 |
| flame | 0.95\|0.52\|0.12 | none | 1.0 | 1 |
| core | 1.0\|0.86\|0.35 | none | 1.0 | 1 |
| stairs1 | 0.22\|0.20\|0.22 | none | 1.0 | 1 |
| stairs2 | 0.18\|0.16\|0.18 | none | 1.0 | 1 |
| stairs3 | 0.14\|0.13\|0.15 | none | 1.0 | 1 |
| path1 | 0.19\|0.16\|0.17 | none | 1.0 | 0 |
| path2 | 0.21\|0.18\|0.18 | none | 1.0 | 0 |
| rock_left | 0.10\|0.09\|0.13 | none | 1.0 | 1 |

## Sections

One continuous scene, so one section covering the whole show.

| bars | sky | stars | moon | sea | sea_glow | far_cliff | arch_open_low | arch_open_top | arch_lit | arch | arch_shadow | ledge | ledge_lip | glow1 | glow2 | logs | flame | core | stairs1 | stairs2 | stairs3 | path1 | path2 | rock_left |
|------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0-11 | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u |

## Sprites

Raster actors over the SDF set. Later rows win inside their window; `cycle`/`alt` flip
between two frames every N frames, which is the lip flap, the walk-in and the laugh.
`flip 1` mirrors the boy so he faces the pirate.

| id | sheet | cell | bars | frame | x | y | height | flip | cycle | alt |
|----|-------|------|------|-------|-----|-----|--------|------|-------|-----|
| pirate | assets/sprites/pirate.png | 126x88 | 0-11 | 0 | -0.50 | -0.295 | 0.34 | 0 | 0 | 0 |
| pirate | assets/sprites/pirate.png | 126x88 | 4-4.4 | 2 | -0.50 | -0.295 | 0.34 | 0 | 0 | 0 |
| pirate | assets/sprites/pirate.png | 126x88 | 4.4-6 | 1 | -0.50 | -0.295 | 0.34 | 0 | 4 | 0 |
| pirate | assets/sprites/pirate.png | 126x88 | 9-9.4 | 3 | -0.50 | -0.295 | 0.34 | 0 | 0 | 0 |
| pirate | assets/sprites/pirate.png | 126x88 | 9.4-11 | 1 | -0.50 | -0.295 | 0.34 | 0 | 4 | 0 |
| boy | assets/sprites/boy.png | 200x234 | 0-1 | 3 | 0.40 | -0.295 | 0.38 | 1 | 4 | 4 |
| boy | assets/sprites/boy.png | 200x234 | 1-11 | 0 | 0.40 | -0.295 | 0.38 | 1 | 0 | 0 |
| boy | assets/sprites/boy.png | 200x234 | 1-3 | 1 | 0.40 | -0.295 | 0.38 | 1 | 4 | 0 |
| boy | assets/sprites/boy.png | 200x234 | 7-7.3 | 2 | 0.40 | -0.295 | 0.38 | 1 | 0 | 0 |
| boy | assets/sprites/boy.png | 200x234 | 7.3-8 | 1 | 0.40 | -0.295 | 0.38 | 1 | 4 | 0 |

## Dialogue

Bar is 2.5 s at 96 BPM. `bars: auto` ends the scene on the last line.

| speaker | bars | text | voice |
|---------|------|------|-------|
| AINA | 1-3 | You are sure the pirate leaders are up here? | slt |
| BORIS | 4-6 | That is what the map said. | rms |
| AINA | 7-8 | Maps lie. | slt |
| BORIS | 9-11 | Not this one. I drew it. | rms |

## Tracks

A single push-in, and mouths on each speaker's own windows.

| name | kind | values | options |
|------|------|--------|---------|
| zoom | expr | 1.0+0.0025*t | |
| focus_x | expr | 0.0 | |
| focus_y | expr | -0.02 | |
| mouth_a | expr | (t > 2.5 && t < 7.5) ? 0.30+0.22*sin(t*12.0) : (t > 17.5 && t < 20.0) ? 0.30+0.22*sin(t*13.0) : 0.03 | |
| talk_pip | expr | (t > 2.5 && t < 7.5) ? 0.30+0.22*sin(t*12.0) : (t > 17.5 && t < 20.0) ? 0.30+0.22*sin(t*13.0) : 0.0 | |
| mouth_b | expr | (t > 10.0 && t < 15.0) ? 0.30+0.22*sin(t*13.0) : (t > 22.5) ? 0.30+0.22*sin(t*11.0) : 0.03 | |