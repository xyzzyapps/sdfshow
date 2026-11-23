# show - diner

Two characters in a diner booth, four minutes of nothing, in the observational
comedy register: a warm cream/maroon/teal 1990s set, quick cuts, and dialogue about
absolutely nothing.

| section | bars | shots |
|---------|------|-------|
| one | 0-8 | wide two-shot, then alternating close-ups |
| two | 8-16 | the other side of the booth, closer, then a two-shot to end |

**This scene composites two shaders and two overlays.**

1. the SDF scene (`scene.glsl`) renders the room, the booths and both figures;
2. a bloom pass lifts the practicals;
3. speech bubbles are numpy SDF text masks composited by VapourSynth *after* the
   shader, so type never enters the raymarch;
4. dialogue is synthesized with `flite` from the same table the bubbles read, so the
   spoken line and the drawn line cannot drift.

bpm: 96
bars: 16
fps: 30
size: 1280x720

## Stage

The key light comes from the camera side (`+z`), because both characters face the lens.
A grey-ish fill keeps the dark maroon vinyl from going black.

| key        | value                    |
|------------|--------------------------|
| distance   | dolly                    |
| yaw        | yaw                      |
| pitch      | pitch                    |
| fov        | fov                      |
| target     | tx\|0.86\|0.10           |
| fog        | 0.010                    |
| exposure   | 1.55                     |
| background | 0.055\|0.045\|0.040      |
| light      | -0.18\|0.42\|-0.89       |
| scanlines  | 0.035                    |
| plasma     | 0.0                      |
| grain      | 0.012                    |
| vignette   | 0.30                     |
| hue        | 0                        |
| fold       | none                     |

## Fields

| field |
|-------|
| floor |
| wall  |
| booth |
| table |
| cup   |
| aina  |
| boris |

## Materials

Cream walls, maroon vinyl, warm wood, and two figures told apart by hue alone: Aina
warm ochre, Boris cool teal - the same split the show used for its two leads, without
being anyone.

| field | color             | pattern | scale |
|-------|-------------------|---------|-------|
| floor | 0.46\|0.40\|0.33 | checker | 1.1   |
| wall  | 0.72\|0.66\|0.52 | none    | 1.0   |
| booth | 0.42\|0.13\|0.15 | none    | 1.0   |
| table | 0.62\|0.44\|0.24 | none    | 1.0   |
| cup   | 0.90\|0.87\|0.80 | none    | 1.0   |
| aina  | 0.93\|0.74\|0.50 | none    | 1.0   |
| boris | 0.52\|0.72\|0.80 | none    | 1.0   |

## Sections

| bars  | floor | wall | booth | table | cup | aina | boris |
|-------|-------|------|-------|-------|-----|------|-------|
| 0-8   | u     | u    | u     | u     | u   | u    | u     |
| 8-16  | u     | u    | u     | u     | u   | u    | u     |

## Dialogue

`bars` is the window the bubble holds the screen. Bar is 2.5 s at 96 BPM.

| speaker | bars  | text                              | voice |
|---------|-------|-----------------------------------|-------|
| AINA    | 1-3   | So we are just going to sit here?  | slt   |
| BORIS   | 3-4   | That was the plan.                 | rms   |
| AINA    | 4-6   | For how long?                      | slt   |
| BORIS   | 6-7   | Until one of us has a thought.     | rms   |
| AINA    | 9-10  | I had one.                         | slt   |
| BORIS   | 10-11 | Was it about the menu?             | rms   |
| AINA    | 11-13 | It was about the menu.             | slt   |
| BORIS   | 13-15 | Then we are still here.            | rms   |
| AINA    | 15-16 | Still here.                        | slt   |

## Effects

| effect | key       | value |
|--------|-----------|-------|
| bloom  | threshold | 0.62  |
| bloom  | strength  | 0.35  |
| bloom  | radius    | 2.0   |
| chroma | amount    | 0.012 |
| glitch | chance    | 0.004 |
| glitch | amount    | 0.010 |

## Tracks

The camera is keyed on **bar boundaries**, so a cut lands on the beat: `ease=none`
makes each key a hard cut rather than a ramp. `tx` is the look-at x, which is what
swings between the two faces.

| name  | kind | values | options |
|-------|------|--------|---------|
| dolly | cuts | 0:6.2\|2.5:3.4\|5:3.2\|7:7.6\|10:3.6\|12:3.4\|14:7.2 |
| tx    | cuts | 0:0.05\|2.5:-0.72\|5:0.86\|7:0.05\|10:-0.72\|12:0.84\|14:0.05 |
| yaw   | cuts | 0:0.02\|2.5:-0.10\|5:0.10\|7:0.0\|10:-0.08\|12:0.09\|14:0.0 |
| pitch | cuts | 0:-0.02\|2.5:-0.05\|5:-0.05\|7:-0.02\|10:-0.06\|12:-0.06\|14:-0.02 |
| fov   | cuts | 0:1.9\|2.5:1.55\|5:1.5\|7:2.05\|10:1.5\|12:1.5\|14:2.0 |
| mouth_a | expr | (t > 2.5 && t < 7.5) ? 0.45+0.5*sin(t*24.0) : (t > 22.5 && t < 32.5) ? 0.45+0.5*sin(t*22.0) : 0.05 | |
| mouth_b | expr | (t > 7.5 && t < 17.5) ? 0.45+0.5*sin(t*23.0) : (t > 32.5) ? 0.45+0.5*sin(t*21.0) : 0.05 | |
| brow_a  | expr | (t > 22.0 && t < 26.0) ? 1.0 : 0.0 | |
| brow_b  | expr | (t > 30.0) ? 1.0 : 0.0 | |