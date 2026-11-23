# show - pixel

Two **settings**, four characters, in flat 2D pixel art: SDF shapes stacked like SVG,
quantised to a pixel grid.

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
head, hair, eyes, brows, mouth; sofa, lamp, couch cushion. That is the same idea as an
SVG document and it is what makes the faces and the furniture read at this resolution.

bpm: 96
bars: 20
fps: 30
size: 1280x720

## Stage

| key           | value                |
|---------------|----------------------|
| mode          | 2d                   |
| pixel         | 9                    |
| outline       | 0.007                |
| outline_color | 0.08\|0.05\|0.09     |
| exposure      | 1.0                  |
| background    | 0.16\|0.20\|0.24     |
| vignette      | 0.22                 |
| scanlines     | 0.0                  |
| grain         | 0.006                |
| hue           | 0                    |
| font          | 0.020                |
| panel         | 2.60                 |

`font` is the cap height as a fraction of frame height and `panel` pads the bubble
relative to the type, so the letters stay small while the bubble stays comfortable.

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
| chair |
| aina |
| aina_hair |
| aina_eye |
| aina_brow |
| aina_mouth |
| boris |
| boris_hair |
| boris_eye |
| boris_brow |
| boris_mouth |
| dora |
| dora_hair |
| dora_eye |
| dora_brow |
| dora_mouth |
| ellis |
| ellis_hair |
| ellis_eye |
| ellis_brow |
| ellis_mouth |

## Materials

Warm 1970s diner, cooler 1980s living room. Four skin and hair pairs, so nobody is a
recolour of anyone else.

| field | color | pattern | scale |
|-------|-------|---------|-------|
| sky | 0.62\|0.76\|0.80 | none | 1.0 |
| floor_diner | 0.36\|0.34\|0.31 | none | 1.0 |
| booth | 0.30\|0.16\|0.14 | none | 1.0 |
| table | 0.87\|0.80\|0.66 | none | 1.0 |
| cup | 0.96\|0.94\|0.88 | none | 1.0 |
| wall_house | 0.56\|0.52\|0.58 | none | 1.0 |
| floor_house | 0.42\|0.30\|0.24 | none | 1.0 |
| sofa | 0.40\|0.46\|0.34 | none | 1.0 |
| rug | 0.62\|0.42\|0.30 | none | 1.0 |
| lamp | 0.92\|0.86\|0.62 | none | 1.0 |
| chair | 0.46\|0.34\|0.26 | none | 1.0 |
| aina | 0.95\|0.76\|0.55 | none | 1.0 |
| aina_hair | 0.34\|0.20\|0.13 | none | 1.0 |
| aina_eye | 0.12\|0.09\|0.12 | none | 1.0 |
| aina_brow | 0.30\|0.18\|0.12 | none | 1.0 |
| aina_mouth | 0.42\|0.16\|0.18 | none | 1.0 |
| boris | 0.56\|0.76\|0.82 | none | 1.0 |
| boris_hair | 0.20\|0.16\|0.14 | none | 1.0 |
| boris_eye | 0.12\|0.09\|0.12 | none | 1.0 |
| boris_brow | 0.24\|0.16\|0.12 | none | 1.0 |
| boris_mouth | 0.36\|0.16\|0.18 | none | 1.0 |
| dora | 0.88\|0.66\|0.50 | none | 1.0 |
| dora_hair | 0.72\|0.44\|0.16 | none | 1.0 |
| dora_eye | 0.12\|0.09\|0.12 | none | 1.0 |
| dora_brow | 0.62\|0.38\|0.14 | none | 1.0 |
| dora_mouth | 0.44\|0.18\|0.20 | none | 1.0 |
| ellis | 0.72\|0.56\|0.44 | none | 1.0 |
| ellis_hair | 0.46\|0.46\|0.44 | none | 1.0 |
| ellis_eye | 0.12\|0.09\|0.12 | none | 1.0 |
| ellis_brow | 0.36\|0.36\|0.34 | none | 1.0 |
| ellis_mouth | 0.40\|0.20\|0.20 | none | 1.0 |

## Sections

The cut is at bar 8: the diner set goes away, the living room arrives, and the cast
changes with it.

| bars | sky | floor_diner | booth | table | cup | wall_house | floor_house | sofa | rug | lamp | chair | aina | aina_hair | aina_eye | aina_brow | aina_mouth | boris | boris_hair | boris_eye | boris_brow | boris_mouth | dora | dora_hair | dora_eye | dora_brow | dora_mouth | ellis | ellis_hair | ellis_eye | ellis_brow | ellis_mouth | cup |
|------|-----|-------------|-------|-------|------------|-------------|------|-----|------|-------|------|-----------|----------|-----------|------------|-------|------------|-----------|------------|-------------|------|-----------|----------|-----------|------------|-------|------------|-----------|------------|-------------|-----|
| 0-4 | u | u | u | u | u | x | x | x | x | x | x | u | u | u | u | u | u | u | u | u | u | x | x | x | x | x | x | x | x | x | x | u |
| 4-8 | u | u | u | u | u | x | x | x | x | x | x | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | x | x | x | x | x | u |
| 8-14 | x | x | x | x | x | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | x | x | x | x | x | u |
| 14-20 | x | x | x | x | x | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u | u |

## Dialogue

Bar is 2.5 s at 96 BPM.

| speaker | bars | text | voice |
|---------|------|------|-------|
| AINA | 1-2 | So we are just going to sit here? | slt |
| BORIS | 2-3 | That was the plan. | rms |
| DORA | 5-6 | I have been standing since Tuesday. | awb |
| BORIS | 6-7 | It is Thursday. | rms |
| AINA | 9-10 | Your sofa is very quiet. | slt |
| BORIS | 10-11 | It is a quiet sofa. | rms |
| AINA | 11-13 | I meant the room. | slt |
| DORA | 13-14 | The room is listening. | awb |
| ELLIS | 15-16 | I am only here for the lamp. | kal |
| DORA | 16-17 | Nobody is here for the lamp. | awb |
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

Mouths pulse gently while a line is spoken - a small open/close, not a wide gape.

| name | kind | values | options |
|------|------|--------|---------|
| mouth_a | expr | (t > 2.5 && t < 5.0) ? 0.28+0.20*sin(t*13.0) : (t > 22.5 && t < 27.5) ? 0.28+0.20*sin(t*12.0) : 0.03 | |
| mouth_b | expr | (t > 5.0 && t < 7.5) ? 0.28+0.20*sin(t*14.0) : (t > 25.0 && t < 27.5) ? 0.28+0.20*sin(t*13.0) : (t > 45.0) ? 0.28+0.20*sin(t*13.0) : 0.03 | |
| mouth_d | expr | (t > 12.5 && t < 15.0) ? 0.28+0.20*sin(t*12.0) : (t > 32.5 && t < 35.0) ? 0.28+0.20*sin(t*12.0) : (t > 40.0 && t < 42.5) ? 0.28+0.20*sin(t*12.0) : 0.03 | |
| mouth_e | expr | (t > 37.5 && t < 40.0) ? 0.28+0.20*sin(t*11.0) : (t > 42.5 && t < 45.0) ? 0.28+0.20*sin(t*11.0) : 0.03 | |
| brow_a | expr | (t > 27.0) ? 1.0 : 0.0 | |
| brow_b | expr | (t > 25.0 && t < 30.0) ? 1.0 : 0.0 | |
| brow_d | expr | (t > 32.0 && t < 37.0) ? 1.0 : 0.0 | |
| brow_e | expr | (t > 37.0) ? 1.0 : 0.0 | |