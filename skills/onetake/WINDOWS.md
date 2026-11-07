# Local Windows setup

Source: https://github.com/feitangyuan/onetake
Installed revision: 415758128aa45cc54340df40d8109363447f582e

Core Python dependencies are isolated in `.venv/`. Node, FFmpeg and FFprobe are available through PATH. The PowerShell launcher uses UTF-8 mode because upstream files contain Unicode and Windows may otherwise default to GBK.

Playwright is pinned to 1.62.0 to reuse the existing Chromium revision 1234 browser installation. `requirements-local.lock.txt` records the installed Python package versions.

Run from any directory, keeping composition/output paths relative to the current working directory:

```powershell
$onetake = Join-Path $env:USERPROFILE '.codex/skills/onetake'
& "$onetake/scripts/run.ps1" look.py list
& "$onetake/scripts/run.ps1" render.py comp.html --out draft.mp4
& "$onetake/scripts/run.ps1" verify_promo.py draft.mp4 --comp comp.html
node "$onetake/scripts/test_motion.js"
```

All upstream `python3 scripts/...` examples should use this launcher, or `.venv/Scripts/python.exe -X utf8`, on this machine. Do not use the system Python, which lacks these dependencies.

Optional narration is separate: Kokoro TTS and faster-whisper plus their model files are not installed by this setup. The upstream TTS command supports English/Japanese; other voices or Chinese narration require a suitable external voice workflow. Existing audio can be supplied to the renderer with `--sfx`.

The public release is licensed under PolyForm Noncommercial 1.0.0. Commercial use requires the author's separate authorization. No Pro purchase or credential setup was performed.

Validation on 2026-10-16: upstream motion-library tests all passed; `pip check` passed; all 110 upstream files were compared with the pinned source revision (only SKILL.md has the documented local runtime note); all six looks loaded; the synthetic sound demo generated ten events at -8 dBFS; an actual 640x360, 30 fps, one-second MP4 rendered with two workers, 180-degree shutter and 120 captures, with no page errors, from a path containing spaces and Chinese characters. This is a functional smoke test, not a 4K performance benchmark.
