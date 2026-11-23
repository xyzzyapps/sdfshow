# show - reel

A 30-second demoscene reel: four scenes, six fields, morphs, a shifting fold and a
changing effect chain. 120 BPM, so one bar is 2 s and the whole piece is 15 bars.

| bars  | scene |
|-------|-------|
| 0-3   | ring tunnel, camera creeping forward |
| 3-7   | tunnel morphs into a Menger sponge over the floor |
| 7-8   | the sponge collapses to a gyroid |
| 8-12  | gyroid morphs into a kaleidoscopic sphere cluster |
| 12-15 | sphere cluster collapses to a synthwave sun in a colonnade |

bpm: 120
bars: 15
fps: 30
size: 1280x720

## Stage

The camera arcs continuously; each scene owns a distance range so the cuts read as
dollies rather than jumps. `fold_count` and `hue` are tracks, so the fold breathes and
the palette drifts.

| key        | value                  |
|------------|------------------------|
| distance   | dolly                  |
| yaw        | yaw                    |
| pitch      | pitch                  |
| fov        | fov                    |
| target     | 0\|0.05\|0            |
| fog        | fog                    |
| exposure   | 1.3                    |
| background | 0.02\|0.012\|0.035    |
| light      | 0.45\|0.85\|0.4       |
| scanlines  | 0.10                   |
| plasma     | 0.03                   |
| grain      | 0.02                   |
| vignette   | 0.26                   |
| hue        | hue                    |
| fold       | kaleido                |
| fold_count | foldn                  |

## Fields

| field   |
|---------|
| tunnel  |
| menger  |
| gyroid  |
| orbs    |
| sun     |
| pillars |
| floor   |

## Materials

| field   | color            | pattern | scale |
|---------|------------------|---------|-------|
| tunnel  | 0.20\|0.85\|1.0 | stripes | 2.0   |
| menger  | 1.00\|0.72\|0.22 | none   | 1.0   |
| gyroid  | 0.35\|1.00\|0.62 | none   | 1.0   |
| orbs    | 0.85\|0.35\|1.0 | none    | 1.0   |
| sun     | 1.00\|0.35\|0.12 | stripes | 3.0   |
| pillars | 0.50\|0.28\|1.0 | stripes | 2.0   |
| floor   | 0.07\|0.09\|0.20 | checker | 1.6   |

## Sections

`m` blends a field into the accumulator with a track weight: `mix(d, f, w)`. That is
only meaningful when both fields occupy the same space (concentric solids), because
the average of two distances is not a distance. So the gyroid morphs from the
Menger sponge (both centred, solid), and the orbs scene is entered by a fast cut.
Orbs morph into the sun at the end, again concentric.

| bars  | tunnel | menger | gyroid | orbs  | sun   | pillars | floor |
|-------|--------|--------|--------|-------|-------|---------|-------|
| 0-3   | u      | x      | x      | x     | x     | x       | x     |
| 3-7   | x      | u      | x      | x     | x     | x       | u     |
| 7-8   | x      | u      | mwg   | x     | x     | x       | u     |
| 8-9   | x      | x      | u      | x     | x     | x       | u     |
| 9-12  | x      | x      | x      | u     | x     | x       | u     |
| 12-13 | x      | x      | x      | u     | x     | u       | u     |
| 13-15 | x      | x      | x      | u     | msun  | u       | u     |

## Tracks

Camera and scene motion. `keys` are bar:value, `expr` is GLSL over `t`, `steps`
cycles on the 16th grid.

| name  | kind  | values | options |
|-------|-------|--------|---------|
| dolly | keys  | 0:2.0\|3:1.9\|3.5:6.4\|7:5.8\|7.5:5.4\|8:5.2\|8.5:6.0\|12:6.4\|12.5:7.8\|15:7.2 | ease=smooth |
| yaw   | keys  | 0:0.0\|3:0.0\|3.5:0.9\|7:2.2\|7.5:2.6\|8:3.0\|8.5:4.1\|12:5.2\|12.5:5.6\|15:6.4 | ease=smooth |
| pitch | keys  | 0:-0.02\|3:-0.02\|3.5:-0.14\|7:-0.10\|7.5:-0.10\|8:-0.08\|8.5:-0.05\|12:-0.08\|12.5:-0.04\|15:-0.02 | ease=smooth |
| fov   | keys  | 0:1.5\|3:1.5\|3.5:1.95\|7:1.85\|7.5:1.8\|8:1.75\|8.5:1.7\|12:1.75\|12.5:1.65\|15:1.85 | ease=smooth |
| fog   | keys  | 0:0.02\|3:0.02\|3.5:0.07\|7:0.05\|7.5:0.05\|8:0.04\|8.5:0.03\|12:0.05\|12.5:0.08\|15:0.06 | ease=smooth |
| hue   | expr  | 0.25*sin(t*0.42) | |
| foldn | keys  | 0:2\|3:2\|3.5:2\|8:2\|8.5:8\|12:8\|12.5:6\|15:6 | ease=smooth |
| wg    | keys  | 0:0\|7:0\|7.7:1\|8:1 | ease=smooth |
| sun   | keys  | 0:0\|13:0\|13.8:1\|15:1 | ease=smooth |
| bloom_gain | keys | 0:0.45\|3:0.45\|3.5:0.7\|8:0.8\|8.5:0.6\|12:0.9\|12.5:0.75\|15:1.1 | ease=smooth |
| chroma_amt | keys | 0:0.02\|3:0.02\|3.5:0.09\|7:0.05\|7.5:0.12\|8:0.06\|8.5:0.12\|12:0.05\|12.5:0.1\|15:0.06 | ease=smooth |
| glitch_amt | keys | 0:0.0\|3:0.0\|3.4:0.22\|7:0.04\|7.4:0.3\|8:0.02\|8.4:0.02\|12:0.02\|12.4:0.28\|15:0.06 | ease=smooth |

## Effects

The chain is fixed for the whole show but each knob is a track, so the treatment
shifts with the scenes: bloom opens up for the palette scenes, glitch and chroma
come in for the transitions.

| effect | key       | value |
|--------|-----------|-------|
| bloom  | threshold | 0.55  |
| bloom  | strength  | bloom_gain |
| bloom  | radius    | 2.5   |
| chroma | amount    | chroma_amt |
| crt    | curvature | 0.10  |
| glitch | chance    | glitch_amt |
| glitch | amount    | 0.05  |