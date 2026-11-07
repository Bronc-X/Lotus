# domino-25s — one phone is one pixel (25.6 s, accepted v8, 2026-09-27)

> This folder ships the film only. Its source (the composition, the Blender scene, the score, the sound sources) is not
> part of the public release; files named below describe how it was made.
>
> The film: `domino.mp4`

The user pointed at HTX's iPhone 18 Pro review (何同学, YouTube BIqvBPVcz7Y, the domino segment 18–41 s): 「你挑战一下这种…
不要考虑口播，只有动画+音效+音乐卡点」. The film is an original in that genre, not a shot-for-shot copy, and the phones have
no logo.

**Concept A 「分辨率」**: one phone is one pixel. The same picture — a smiling classic Mac drawn in code — resolves as the
chain grows: 1 → 3×3 → 10×10 → 32×32 (dark until the drop) → 100×100, and the film ends on the one phone left standing,
showing the whole picture, which winks and goes dark on the last hit. 12,346 phones.

Made with a coding agent driving Blender (the model) and three.js (12,346 instances, the chain as a pure function of
time), rendered frame by frame with shutter motion blur. It was cut to *Call Me (Instrumental)* — Ariel Shalom, an
Artlist Original — but the track is licensed, not shipped: `domino.mp4` plays on the foley and the film's own notes alone.

## Beat sheet (film time; grid 140 BPM, `beat(n) = 0.029 + n·60/140`)

| t | beat | picture | music (Call Me, instrumental) |
|---|---|---|---|
| 0–1.74 | 0–4 | macro orbit on one phone | song bar 64, full from frame one |
| 1.74–2.60 | 4–6 | it tips in slow motion, screen lights one blue pixel | bar 65 beats 1–2: silent |
| 2.60 | 6 | lands on the 3×3 (a small shake); the 3×3 spreads slowly | the hit that ends the silence |
| 3.46 | 8 | the S-line launches | bar 66 downbeat |
| 6.89 | 16 | the 10×10 is struck; crane to ~45° | bar 68 |
| 7.8–10.3 | 18–24 | swoop onto the trunk, FPV ride on the hero front, banking at splits 1–2 | |
| 8.60–12.03 | 20–28 | splits 1 → 32, each generation surging into the next beat | |
| 10.3–12.2 | 24–28.5 | stepped pull-back, one step a split, onto the 32 lines' set-up | |
| 12.56–13.60 | | the 32 lines fill the 32×32, screens dark | bar 71 |
| 13.74 | 32 | **drop**: 1,024 screens light at once (shake 9) | cut to bar 88, the heaviest section |
| 13.6–16.7 | | the chase: one line, the front outrunning a low camera | |
| 16.74 | 39 | the field is struck, circular front through 10,000 | |
| 16.7–21.4 | | surf the front low, climb to a 35° reveal; the Mac winks on beats 48, 50 | |
| 22.31 | 52 | dive to the survivor | music cut dead, hall tail |
| 23.6 / 24.89 | 55 / 58 | it winks; its screen goes dark on the last hit | alone |

## Versions — what each note changed

- **Model** (3 rounds, Blender MCP). Approved: 「可以了 我觉得模型问题搞定了」.
- **v1** (eye picture, Mixkit track by statistics, no foley): 「音乐完全不对…一点都没起调…没有任何音效…眼珠子…很丑，换成apple经
  典的那个微笑吧…俯拍啥也看不出来」.
- **v4** (smiling Mac, no top-down, foley even with music): 「很好了，但是音乐还是不对…中间有段会枯燥的…音效…不够清脆，听着闷」.
- Four auditions → 「都不行 全都错了」 → Shazam of the reference → **Call Me**.
- **v5** (picture freezes on beats 12–14 and 36–38, crisper samples; placeholder music): 「两三个停顿很奇怪，太刻意了…新的碰撞
  声我没听出来…像青蛙在叫，不脆」.
- **v6** (Call Me; freezes gone; modal ticks + swarm; splice to song bars 15–17 for their stutters; 7 dB density duck):
  「7-12s…没啥节奏变动…前面起调后面越来越低，到10s以后都没啥音乐节奏节拍了」.
- **v7** (bars 64–71 → 88; gentle ducking; alternating set-ups per split; surging fronts): 「牛逼」, then 8–12 s
  「左右摆来摆去…有点生硬了」.
- **v8** (FPV ride then stepped pull-back): 「牛逼，可以了」.

## Numbers

- Render: 768 frames, 4,382 captures, 119 s on 6 workers with `--gpu`; peak 589 px/frame at 30 fps under the shutter.
- verify (with `--ref`, reference-relative rest / audio): all PASS — still 0.01 (reference 0.004), audio quiet 0.072,
  peak −4.3 dBFS after AAC, continuity 1.00, framing: the front in frame 0.2–16.8 s, the survivor wholly in 23.6–25.6 s.
- Mix: buses fx −19.5 / music −17.6 LUFS; master −16 LUFS, ceiling −4.6 dBTP (the louder track read −2.9 dBFS after
  AAC at −4.0). Foley periodicity in the dense stretches 0.07–0.15, > 2 kHz share 0.87–0.90.

## Files

| file | what |
|---|---|
| `comp.html` | the film; loads `vendor/three.bundle.js`, `assets/p18.glb.js`, `assets/studio_env.hdr.js`, `../../lib/motion.js` |
| `vendor/three-entry.js` | what the IIFE bundle exports |
| `blender/` | `bmcp.py` (the MCP socket client), `reset.py`, `p18_model.py` (the measured model, three LODs), `export_glb.py`, `lookdev.py` |
| `dump_events.py` → `events.json` | the comp's `__events()` |
| `score.py` → `mix.wav` | foley + the film's own notes + master; adds the track only if `music/call_me.m4a` is present |
| `domino.mp4` | v8, 1080p30 |
| `drafts/stills_v8_tree.png` | the FPV ride and pull-back, 8.3–12.8 s |
