# infra-25s — every image starts as heat (25.5 s, accepted v6, 2026-10-12)

> This folder ships the film only. Its source (the composition, the score, the sound sources) is not part of the public
> release; files named below describe how it was made.
>
> The film: `infra.mp4`

A reply film. @rajzmotion posted an After Effects launch film for a fictional AI creative platform with "Let me know when
Opus 5.5 can do this" (x.com/rajzmotion/status/2109273645654888831); the ask was 「做一个比它这个更好的，30秒的」. Same
genre, an original concept: his sentence is typed into a prompt bar and sent as the hook, then the film is the
platform answering a prompt of its own.

**Concept: every image starts as heat.** "A moka pot espresso for a café menu" arrives as a thermal false-colour
field, resolves block by block (12×8 → 24×16 → 48×32 → 96×64 → photo), and cools into a photograph, the steam last.
The reference's motion vocabulary (bracket type, a checklist that works, hard-cut variant flashes, a fan of results)
is kept; thermal is its gradient, made literal.

Method, no canvas anywhere:
- thermal = an SVG `feComponentTransfer` table filter on a plain `<img>`;
- cooling = one `luminanceToAlpha` filter per image, its intercept set per seek, so cold pixels become the photo
  first and the steam last;
- the heat blocks are DOM divs read from `photos/steam-hero.blocks.js`;
- the 96×64 stage is `photos/steam-hero-96.png` with `image-rendering: pixelated`.

## Credits

- Photos: one shoot by Shutter Speed (unsplash.com/@shutter_speed_), Unsplash License.
- Music: *New Bass 02* by Lily J, Mixkit free licence.
- Fonts: Inter, Instrument Serif, Geist Mono (OFL).

## Beat sheet (film time; grid 117 BPM, `beat(k) = 3.597 + k·60/117`; track bars at k ≡ 0 mod 4)

| t | beat | picture | sound |
|---|---|---|---|
| 0–1.03 | −5 | the hook: his sentence in the bar at 1.8×, a hand clicks send | click, marimba A4 |
| 1.08–2.0 | | his glyphs heat right → left and rise as steam | hiss, panned with the heat |
| 1.9–3.44 | | the prompt types at 22 cps, the camera at 3× riding the caret, newest glyphs hot | keys, four samples, jittered |
| 3.597 | 0 | send → an iris of heat from the button, the bar drops | the one sub, air, crotale; the track's first full bar |
| 4.11–5.65 | 1–4 | { every } { image } { starts } { as heat }: braces spring to each width, four corner squares on their own springs | marimba A3 C4 D4 A4 |
| 6.16–7.70 | 5–8 | the squares fly to the card's corners; blocks hottest first; hits at 24×16, 48×32, 96×64, photo | glass hits, the last one big (crotale + vibes) |
| 7.96–10.78 | 9–14 | the field folds into the card; *Cooling* checklist ticks while the photo cools, steam last | a hiss that settles; glass ticks, confirmation |
| 11.80 | 16 | { In▢fra }: the card lands in the slot between "In" and "fra" | vibes C4, drop |
| 12.83–13.34 | 18–19 | the slot flickers three variants as heat | glitch ×3 |
| 13.53–15.52 | 20– | burst to full bleed: 12 hard-cut flashes, heat for the first half of each, photo for the second, on sixteenths | clicks |
| 15.65–17.70 | 24–28 | the fan of seven; the camera rides a cooling wave far → near; "you ask" / "it brews" | marimba run up the pentatonic |
| 18.01–19.49 | 28–31 | dive into the steam 1.3 → 7× while it reheats | Shepard riser, air |
| 20.01 | 32 | the tagline types, bracketed, glyphs landing hot | — |
| 22.06 | 36 | the wordmark "Infra" drops | marimba spread, vibes |
| 23.28 | 38 | "made with Claude Opus 5.5 · onetake" types in a small bar | — |
| 24.1–25.5 | 40 | end rest | the track fades out |

## Versions — what each note changed

- **3D studio** (a three.js room, window, table and monitor, four lookdev rounds):
  「这质感太差了 劣质的3d场景 没必要吧。就沿用参考视频的那个动效风格吧，用它那个风格热成像做更好的动效」. The film became 2D,
  in the reference's style, thermal.
- 「不要用canvas 如果需要图片的地方 你去搜索照一张吧」: real photos, and every effect is a CSS/SVG filter on them.
- **v2** (30 s, silent): 「节奏不行啊 过于迟缓了…细节还不如那个参考的」. Measured: 62 % still against the reference's
  8.5 %, 9 cuts against 39. **v3** rewrote the beat sheet into quick beats with a detail layer on every section, at
  25.5 s: 「保持 25.5 秒，直接渲染」.
- **Music:** six fresh auditions (no vocals) → 「用 C，对拍然后做音效」. The picture was put on the track's grid.
- **v4** (grid + sound): 「好像声音听着有点混乱」. Measured: the track's kicks sat 141 ms after the grid, so every on-grid
  sound flammed. **v5** started the track at 13.361 s instead of 13.22: 「还是那样」.
- The second cause was the spectrum, not the timing: the foley was 72 % under 300 Hz (six sub hits plus the rooms),
  the bass-heavy track 87 %, so both blurred into one low thud. **v6:**
  - only the iris keeps its sub;
  - the foley is high-passed at 220 Hz, lifted 5 dB from 3 kHz and sits about 4 LU under the track;
  - the glass patter, the steam glints and the per-letter keys are gone.

  「可以了这个」.

## Numbers

- Render: 765 frames, 3,854 captures, 499 s on 8 workers (no `--gpu` needed: no WebGL).
- verify with `--ref` (picture of v4 = v6):
  - cadence CV 0.35, still 0.431 (reference 0.085), cuts 33 (39), bursts 6 (10), continuity 1.00 over 4 boundaries;
  - peak 474 px/frame at the iris, under a 180° shutter.
  - The audio leg failed on quiet (0.007): the track and the hall tails never leave a silent stretch.
- v6 mix with the track: −16.0 LUFS, −4.0 dBTP; foley −25.5 LUFS against the track's −21.2. The foley's 300 Hz–8 kHz
  share went from 28 % to 53 %.
