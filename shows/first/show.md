# show - first

The clock comes from `bpm`, `bars`, `fps` and `size`. A bar is four beats; a step is
a 16th note. `Sections` rows are bar ranges, columns are fields, cells are
composition operators (`u`, `u<k>`, `s<k>`, `i<k>`, `x`). Row order is semantic.

bpm: 120
bars: 8
fps: 30
size: 960x540

## Stage

Camera and shading. A value may be a number, a track name, or arithmetic over
tracks - so the camera can move with the music.

| key        | value                    |
|------------|--------------------------|
| distance   | dolly                    |
| yaw        | spin                     |
| pitch      | -0.12                    |
| fov        | 1.75                     |
| target     | 0\|0.05\|0                |
| fog        | 0.075                    |
| exposure   | 1.35                     |
| background | 0.015\|0.018\|0.028     |
| light      | 0.55\|0.8\|0.35          |

## Fields

Composition order. The first field of every section is the base surface.

| field |
|-------|
| core  |
| ring  |
| floor |

## Materials

A field's base colour. Missing rows get a deterministic golden-angle colour.

| field | color            |
|-------|------------------|
| core  | 1.0\|0.42\|0.16  |
| ring  | 0.20\|0.72\|1.0  |
| floor | 0.10\|0.16\|0.30 |

## Sections

| bars | core | ring   | floor  |
|------|------|--------|--------|
| 0-2  | u    | x      | u      |
| 2-4  | u    | u0.30  | u      |
| 4-6  | u    | u0.18  | u0.4   |
| 6-8  | u    | u0.45  | u0.25  |