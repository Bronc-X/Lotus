---
name: gstack
description: 需 gstack 调研、评审、调试、QA 或发布流程时打开总入口。
---

# Official gstack

Lotus no longer ships a local snapshot of gstack as the source of truth.

The real gstack runtime is now the official upstream project:

- Repo: `https://github.com/garrytan/gstack`
- Managed install path: `~/.gstack/repos/gstack`
- Installed by: `install.ps1 -Global` / `install.sh --global`

## What this means

- If you are using Claude, Codex, or OpenCode, Lotus will install the official gstack skills globally and keep them updateable.
- Lotus still owns the global `AGENTS.md` / `CLAUDE.md` rule injection and the project templates.
- This file exists only as a compatibility note inside the Lotus repo. It is **not** the gstack source of truth anymore.

## Source of Truth

Upstream remains the source of runtime binaries and tool mechanics. Lotus maintains concise Codex invocation adapters in `adapters/gstack/`; their task scope and routing replace upstream prompt scaffolding for the covered entrypoints. Do not preload both versions. Standalone upstream updates may restore generated prompts; rerun the Lotus skill sync to reapply adapters.
