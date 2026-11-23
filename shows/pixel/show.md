# show - pixel

Two **settings**, four characters, drawn as flat cutouts: SDF shapes stacked like SVG,
with thin dark rims and no shading. The look is construction paper, not pixels - simple
blocks, big heads, white eyes with pupils, and a camera that cuts between a wide shot
and close-ups on bar boundaries.

`mode: 2d` is a second renderer. There is no raymarch, no camera, no normals and no fog;
every field is a flat shape in screen space and the frame is painted back-to-front, so
the `Fields` table reads top-to-bottom as a z-stack (first row is furthest back).

**Settings are switched by `Sections`.** A field whose cell is `x` is not drawn at all, so
the diner furniture and the living-room furniture are both in the `Fields` table and only
one set is active at a time. Before the cut the diner is on screen; after it, the house.

| setting | bars | who |
|---------|------|-----|
| the diner | 0-8 | Aina and Boris in a booth; Dora arrives and stands |
| the house | 8-20 | Aina and Boris on the sofa; Dora and Ellis standing |

Because a 2D layer is one flat fill, every part is its own layer with its own colour -
head, hair, white eyes, pupils, mouth; sofa, lamp, cushion. That is the same idea as an
SVG document, and it is what makes the faces and the furniture read.

bpm: 96
bars: 20
fps: 30
size: 1280x720

## Stage

| key           | value                |
|---------------|----------------------|
| mode          | 2d                   |
| pixel         | 1                    |
| outline       | 0.005                |
| outline_color | 0.10\|0.06\|0.06     |
| exposure      | 1.0                  |
| background    | 0.58\|0.78\|0.88     |
| vignette      | 0.0                  |
| scanlines     | 0.0                  |
| grain         | 0.0                  |
| hue           | 0                    |
| zoom          | zoom                 |
| focus_x       | focus_x              |
| focus_y       | focus_y              |
| font          | 0.020                |
| panel         | 2.60                 |

`font` is the cap height as a fraction of frame height and `panel` pads the bubble
relative to the type, so the letters stay small while the bubble stays comfortable.

`zoom` and `focus_x`/`focus_y` are a screen-space camera: a `cuts` track switches a wide
shot for a close-up on the speaker at a bar boundary, which is the South Park grammar of
wide, close, close, wide.

## Fields

Back to front. Diner furniture first, then house furniture, then the cast, then details.

| field |
|-------|
| sky |
| floor_diner |
| booth |
| table |
| cup |
| wall_house |
| floor_house |
| sofa |
| rug |
| lamp |
| aina |
| aina_hair |
| aina_eye |
| aina_pupil |
| aina_mouth |
| boris |
| boris_hair |
| boris_eye |
| boris_pupil |
| boris_mouth |
| dora |
| dora_hair |
| dora_eye |
| dora_pupil |
| dora_mouth |
| ellis |
| ellis_hair |
| ellis_eye |
| ellis_pupil |
| ellis_mouth |

## Materials

Construction paper: bright, flat blocks, no patterns. Four skin and hair pairs, so
nobody is a recolour of anyone else. Eyes are white sclera with dark pupils; the mouth
is the darkest red on the face, because it is the shape that moves.

| field | color | pattern | scale |
|-------|-------|---------|-------|
| sky | 0.58\|0.80\|0.90 | none | 1.0 |
| floor_diner | 0.46\|0.40\|0.36 | none | 1.0 |
| booth | 0.62\|0.18\|0.20 | none | 1.0 |
| table | 0.94\|0.88\|0.72 | none | 1.0 |
| cup | 0.98\|0.96\|0.92 | none | 1.0 |
| wall_house | 0.74\|0.66\|0.58 | none | 1.0 |
| floor_house | 0.52\|0.36\|0.26 | none | 1.0 |
| sofa | 0.32\|0.52\|0.46 | none | 1.0 |
| rug | 0.70\|0.42\|0.32 | none | 1.0 |
| lamp | 0.98\|0.86\|0.44 | none | 1.0 |
| aina | 0.99\|0.82\|0.64 | none | 1.0 |
| aina_hair | 0.24\|0.15\|0.11 | none | 1.0 |
| aina_eye | 0.99\|0.98\|0.95 | none | 1.0 |
| aina_pupil | 0.10\|0.08\|0.09 | none | 1.0 |
| aina_mouth | 0.36\|0.12\|0.14 | none | 1.0 |
| boris | 0.72\|0.54\|0.42 | none | 1.0 |
| boris_hair | 0.88\|0.74\|0.32 | none | 1.0 |
| boris_eye | 0.99\|0.98\|0.95 | none | 1.0 |
| boris_pupil | 0.10\|0.08\|0.09 | none | 1.0 |
| boris_mouth | 0.36\|0.12\|0.14 | none | 1.0 |
| dora | 0.96\|0.74\|0.54 | none | 1.0 |
| dora_hair | 0.80\|0.34\|0.16 | none | 1.0 |
| dora_eye | 0.99\|0.98\|0.95 | none | 1.0 |
| dora_pupil | 0.10\|0.08\|0.09 | none | 1.0 |
| dora_mouth | 0.36\|0.12\|0.14 | none | 1.0 |
| ellis | 0.86\|0.68\|0.52 | none | 1.0 |
| ellis_hair | 0.62\|0.62\|0.58 | none | 1.0 |
| ellis_eye | 0.99\|0.98\|0.95 | none | 1.0 |
| ellis_pupil | 0.10\|0.08\|0.09 | none | 1.0 |
| ellis_mouth | 0.36\|0.12\|0.14 | none | 1.0 |

## Sections

The cut is at bar 8: the diner set goes away, the living room arrives, and the cast
changes with it.

| bars | sky | floor_diner | booth | table | cup | wall_house | floor_house | sofa | rug | lamp | aina | aina_hair | aina_eye | aina_pupil | aina_mouth | boris | boris_hair | boris_eye | boris_pupil | boris_mouth | dora | dora_hair | dora_eye | dora_pupil | dora_mouth | ellis | ellis_hair | ellis_eye | ellis_pupil | ellis_mouth |
| ------ | ----- | ------------- | ------- | ------- | ------------ | ------------- | ------ | ----- | ------ | ------- | ----------- | ---------- | ----------- | ------------ | ------- | ------------ | ----------- | ------------ | ------------- | ------ | ----------- | ---------- | ----------- | ------------ | ------- | ------------ | ----------- | ------------ | ------------- | ----- |
| 0-4 | u | u | u | u | u | x | x | x | x | x | u | u | u | u | u | u | u | u | u | u | x | x | x | x | x | x | x | x | x | x |
| 4-8 | u | u | u | u | u | x | x | x | x | x | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | x | x | x | x | x |
| 8-14 | x | x | x | x | x | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | x | x | x | x | x |
| 14-20 | x | x | x | x | x | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u |

## Dialogue

Bar is 2.5 s at 96 BPM.

| speaker | bars | text | voice |
|---------|------|------|-------|
| AINA | 1-2 | We have been sitting here for an hour. | slt |
| BORIS | 2-3 | The sign says wait to be seated. | rms |
| DORA | 5-6 | I have been standing since Tuesday. | awb |
| BORIS | 6-7 | It is Thursday. | rms |
| AINA | 9-10 | This is not the same room. | slt |
| BORIS | 10-11 | The furniture moved with us. | rms |
| AINA | 11-13 | That is not how furniture works. | slt |
| DORA | 13-14 | It is how this furniture works. | awb |
| ELLIS | 15-16 | I am here about the lamp. | kal |
| DORA | 16-17 | Nobody is here about the lamp. | awb |
| ELLIS | 17-18 | I am. | kal |
| BORIS | 18-20 | Then we are all accounted for. | rms |

## Effects

| effect | key | value |
|--------|-----|-------|
| bloom | threshold | 0.75 |
| bloom | strength | 0.18 |
| bloom | radius | 1.5 |
| chroma | amount | 0.008 |

## Tracks

Mouths open on a jaw hinge while a line is spoken - a real travel, from a closed line
to an open oval - and stay shut between lines.

`zoom` and `focus_*` are `cuts` tracks: hard switches on bar boundaries, so a close-up
starts the frame the speaker's line starts. The shot list is wide, close, close, wide.

| name | kind | values | options |
|------|------|--------|---------|
| mouth_a | expr | (t > 2.5 && t < 5.0) ? 0.30+0.22*sin(t*13.0) : (t > 22.5 && t < 25.0) ? 0.30+0.22*sin(t*12.0) : (t > 27.5 && t < 32.5) ? 0.30+0.22*sin(t*14.0) : 0.03 | |
| mouth_b | expr | (t > 5.0 && t < 7.5) ? 0.30+0.22*sin(t*14.0) : (t > 15.0 && t < 17.5) ? 0.30+0.22*sin(t*12.0) : (t > 25.0 && t < 27.5) ? 0.30+0.22*sin(t*13.0) : (t > 45.0) ? 0.30+0.22*sin(t*13.0) : 0.03 | |
| mouth_d | expr | (t > 12.5 && t < 15.0) ? 0.30+0.22*sin(t*12.0) : (t > 32.5 && t < 35.0) ? 0.30+0.22*sin(t*12.0) : (t > 40.0 && t < 42.5) ? 0.30+0.22*sin(t*12.0) : 0.03 | |
| mouth_e | expr | (t > 37.5 && t < 40.0) ? 0.30+0.22*sin(t*11.0) : (t > 42.5 && t < 45.0) ? 0.30+0.22*sin(t*11.0) : 0.03 | |
| zoom | cuts | 0:1.0\|1:2.3\|2:2.2\|3:1.0\|5:2.1\|6:2.2\|7:1.0\|9:2.3\|10:2.2\|11:2.3\|13:2.1\|14:1.0\|15:2.2\|16:2.1\|17:2.2\|18:2.2 | |
| focus_x | cuts | 0:0.0\|1:-0.44\|2:0.06\|3:0.0\|5:0.58\|6:0.06\|7:0.0\|9:-0.44\|10:0.06\|11:-0.44\|13:0.58\|14:0.0\|15:-0.72\|16:0.58\|17:-0.72\|18:0.06 | |
| focus_y | cuts | 0:-0.12\|1:-0.08\|2:-0.08\|3:-0.12\|5:-0.08\|6:-0.08\|7:-0.12\|9:-0.08\|10:-0.08\|11:-0.08\|13:-0.08\|14:-0.12\|15:-0.08\|16:-0.08\|17:-0.08\|18:-0.08 | |