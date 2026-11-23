# show - bar

Two characters at a bar, arguing about nothing. Two scenes:

| bars | scene |
|------|-------|
| 0-4  | both at the bar, wide; two lines are exchanged |
| 4-8  | a closer two-shot; two more lines, then the light goes down |

Speech bubbles are SDF geometry, and so is the text inside them: the stroke font in
`sdfshow/glyphs.py` builds each glyph from capsules, so a bubble catches light and
casts a shadow like everything else. The `## Dialogue` table is the single source for
both the bubble text and the spoken audio, so they cannot drift apart.

bpm: 90
bars: 8
fps: 30
size: 1280x720

## Stage

| key        | value                  |
|------------|------------------------|
| distance   | dolly                  |
| yaw        | yaw                    |
| pitch      | -0.02                  |
| fov        | 2.3                    |
| target     | 0\|0.62\|0            |
| fog        | 0.035                  |
| exposure   | 1.22                   |
| background | 0.05\|0.035\|0.03     |
| light      | 0.35\|0.8\|0.55        |
| scanlines  | 0.05                   |
| grain      | 0.015                  |
| vignette   | 0.2                    |
| hue        | 0                      |
| fold       | none                   |

## Fields

| field   |
|---------|
| floor   |
| counter |
| booth   |
| aina    |
| boris   |

## Materials

| field | color             | pattern | scale |
|-------|-------------------|---------|-------|
| floor | 0.10\|0.07\|0.06 | grid    | 2.0   |
| counter | 0.55\|0.30\|0.14 | none  | 1.0   |
| booth | 0.28\|0.10\|0.12 | none    | 1.0   |
| aina  | 0.95\|0.72\|0.45 | none    | 1.0   |
| boris | 0.55\|0.70\|0.95 | none    | 1.0   |

## Sections

| bars | floor | counter | booth | aina | boris |
|------|-------|-----|-------|------|-------|-------|-------|
| 0-4  | x     | x       | x     | u    | x     |
| 4-8  | x     | x       | x     | u    | x     |

## Dialogue

`bars` is the window the bubble holds the screen. Columns are
`speaker | bars | text | voice`; the voice is an ffmpeg flite voice. Bar 2.67 s at
90 BPM, so bars 1-2 is 2.67-5.33 s.

| speaker | bars | text                          | voice |
|---------|------|-------------------------------|-------|
| AINA    | 1-2  | So who is she anyway?         | slt   |
| BORIS   | 2-3  | She works at the bureau.      | rms   |
| AINA    | 5-6  | Nobody works at the bureau.   | slt   |
| BORIS   | 6-8  | Then who keeps calling me?    | rms   |

## Tracks

Camera and acting. `mouth` oscillates only while its character is speaking, so the
figure reads as talking rather than as a static bust.

| name    | kind | values | options |
|---------|------|--------|---------|
| dolly   | keys | 0:7.0\|4:6.6\|4.4:5.6\|8:5.2 | ease=smooth |
| yaw     | keys | 0:0.26\|4:0.16\|4.4:0.02\|8:-0.02 | ease=smooth |
| mouth_a | expr | (t > 2.67 && t < 5.33) ? 0.5+0.5*sin(t*26.0) : (t > 13.33 && t < 16.0) ? 0.5+0.5*sin(t*24.0) : 0.06 | |
| mouth_b | expr | (t > 5.33 && t < 8.0) ? 0.5+0.5*sin(t*23.0) : (t > 16.0) ? 0.5+0.5*sin(t*25.0) : 0.06 | |
| brow_a  | expr | (t > 13.0 && t < 16.0) ? 1.0 : 0.0 | |
| brow_b  | expr | (t > 16.0) ? 1.0 : 0.0 | |