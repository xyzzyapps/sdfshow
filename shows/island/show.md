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
| pixel         | 3                |
| outline       | 0.003            |
| outline_color | 0.02\|0.02\|0.04 |
| exposure      | 1.0              |
| background    | 0.04\|0.05\|0.12 |
| vignette      | 0.35             |
| scanlines     | 0.0              |
| grain         | 0.015            |
| hue           | 0                |
| zoom          | zoom             |
| focus_x       | focus_x          |
| focus_y       | focus_y          |
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
| far_cliff |
| arch |
| ledge |
| logs |
| flame |
| core |
| pirate_legs |
| pirate_neck |
| pirate_body |
| pirate_hands |
| pirate |
| pirate_hair |
| pirate_eye |
| pirate_pupil |
| pirate_mouth |
| kid_legs |
| kid_neck |
| kid_body |
| kid_hands |
| kid |
| kid_hair |
| kid_eye |
| kid_pupil |
| kid_mouth |
| rock_left |

## Materials

Night palette: deep blue sky, stone lit dimly by the fire, a warm flame against it.

| field | color | pattern | scale |
|-------|-------|---------|-------|
| sky | 0.045\|0.055\|0.140 | none | 1.0 |
| stars | 0.86\|0.90\|1.0 | none | 1.0 |
| moon | 0.93\|0.90\|0.76 | none | 1.0 |
| sea | 0.06\|0.09\|0.20 | none | 1.0 |
| far_cliff | 0.09\|0.10\|0.18 | none | 1.0 |
| arch | 0.30\|0.29\|0.33 | none | 1.0 |
| ledge | 0.14\|0.12\|0.16 | none | 1.0 |
| logs | 0.22\|0.13\|0.09 | none | 1.0 |
| flame | 0.95\|0.52\|0.12 | none | 1.0 |
| core | 1.0\|0.86\|0.35 | none | 1.0 |
| pirate_legs | 0.12\|0.12\|0.16 | none | 1.0 |
| pirate_neck | 0.84\|0.64\|0.48 | none | 1.0 |
| pirate_body | 0.18\|0.22\|0.34 | none | 1.0 |
| pirate_hands | 0.84\|0.64\|0.48 | none | 1.0 |
| pirate | 0.84\|0.64\|0.48 | none | 1.0 |
| pirate_hair | 0.62\|0.18\|0.16 | none | 1.0 |
| pirate_eye | 0.98\|0.97\|0.94 | none | 1.0 |
| pirate_pupil | 0.08\|0.07\|0.08 | none | 1.0 |
| pirate_mouth | 0.30\|0.10\|0.12 | none | 1.0 |
| kid_legs | 0.20\|0.26\|0.38 | none | 1.0 |
| kid_neck | 0.97\|0.86\|0.70 | none | 1.0 |
| kid_body | 0.86\|0.84\|0.74 | none | 1.0 |
| kid_hands | 0.97\|0.86\|0.70 | none | 1.0 |
| kid | 0.97\|0.86\|0.70 | none | 1.0 |
| kid_hair | 0.28\|0.18\|0.12 | none | 1.0 |
| kid_eye | 0.98\|0.97\|0.94 | none | 1.0 |
| kid_pupil | 0.08\|0.07\|0.08 | none | 1.0 |
| kid_mouth | 0.34\|0.12\|0.14 | none | 1.0 |
| rock_left | 0.10\|0.09\|0.13 | none | 1.0 |

## Sections

One continuous scene, so one section covering the whole show.

| bars | sky | stars | moon | sea | far_cliff | arch | ledge | logs | flame | core | pirate_legs | pirate_neck | pirate_body | pirate_hands | pirate | pirate_hair | pirate_eye | pirate_pupil | pirate_mouth | kid_legs | kid_neck | kid_body | kid_hands | kid | kid_hair | kid_eye | kid_pupil | kid_mouth | rock_left |
|------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0-11 | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u |

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
| mouth_b | expr | (t > 10.0 && t < 15.0) ? 0.30+0.22*sin(t*13.0) : (t > 22.5) ? 0.30+0.22*sin(t*11.0) : 0.03 | |
