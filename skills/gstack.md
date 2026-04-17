---
name: gstack
description: Lotus 现在不再内置 gstack 快照，而是由安装器全局安装并更新官方 gstack 上游。
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

When there is any difference between Lotus and upstream gstack, follow upstream gstack.
