# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Upgrade Guide

**Upgrading is safe and non-destructive:**
1. `git pull` (or re-clone) the latest Lotus
2. Re-run `./install.ps1 -Global` (Windows) or `./install.sh --global` (macOS/Linux)
3. Done — your existing projects are untouched

**What gets updated:** Global rules (`~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`, etc.) and global skills.
**What is NOT touched:** Project-level files (anything in your project's `.agents/`, `AGENTS.md`, `.cursor/rules/`). These were created by `--project` and are yours to manage.

---

## [1.1.3] - 2026-04-19

### Changed

- Lotus now force-syncs official gstack skills into the real Codex, OpenCode, and Cursor global skills directories after upstream setup, instead of relying on host setup side effects alone
- Global install validation now checks a full set of core official gstack skills (`office-hours`, `investigate`, `plan-eng-review`, `qa`, `review`, `ship`) so partial installs fail loudly

### Fixed

- Re-running Lotus global install now self-heals stale or half-updated Codex/OpenCode/Cursor gstack skill directories for both new installs and mid-stream upgrades

## [1.1.2] - 2026-04-19

### Added

- Scheduled GitHub Actions workflow that watches official `garrytan/gstack` upstream and opens a review PR when upstream `main` changes
- Tracked upstream state file at `.github/upstream/gstack.json` so Lotus can compare against the last acknowledged upstream snapshot

### Changed

- README now makes the install boundary explicit: cloning Lotus alone does not activate rules, skills, or upstream gstack auto-updates
- README now explains the difference between Lotus repo updates and official gstack runtime auto-updates on a user's machine

## [1.1.1] - 2026-04-19

### Added

- GitHub Actions release workflow that creates a GitHub Release automatically when a `v*.*.*` tag is pushed
- README guidance asking users to click Watch on GitHub to follow frequent updates and release notices

### Changed

- Global install now asks for confirmation before overwriting existing host-level global rule/config files, then backs them up to `.bak` before replacing them
- README now reflects the current global-install behavior more clearly, including automated global setup expectations and current host coverage

### Fixed

- Global install no longer reports success when official gstack setup failed to fully install runtime skills
- Cursor global gstack skills are now synced from the official upstream-generated `.cursor/skills` output into the real host global skills directory

## [1.1.0] - 2026-04-18

### Added

- Managed official `garrytan/gstack` upstream installation during global setup
- Auto-update bootstrap for the upstream gstack runtime under `~/.gstack/repos/gstack`
- Clear separation between Lotus global rules/project templates and upstream gstack runtime ownership

### Changed

- Global install now keeps Lotus as the global rules and template layer while delegating gstack runtime setup to the official upstream project
- Lotus-only skills continue to be installed globally without copying Lotus's stale `gstack` runtime snapshot into host tool skill folders
- Documentation now explains the new upstream-managed global workflow for Claude, Codex, and OpenCode

### Fixed

- Resolved the long-standing mismatch where Lotus shipped an outdated local `gstack` snapshot instead of the official runtime
- Restored the intended "one-command global install, permanently effective" workflow while keeping the runtime aligned with upstream updates

## [1.0.0] - 2026-04-15

### 🎉 Initial Release

**Core Protocol:**
- GStack Engineering Protocol v1.0 (`core/AGENTS.md`)
- Intent Router: 4 scenarios (Feature / Bug / UI / Refactor)
- Quality Gates: Coding + Design checklists
- Universal review commands

**Task-level Skills (7):**
- `@gstack` — Full engineering workflow with 5 role personas
- `@feynman` — Feynman technique for zero-jargon explanation
- `@polanyi-tacit` — Tacit knowledge archaeology in codebases
- `@auto-build` — Automated `npm install` → `npm run build`
- `@powerup` — 10-level interactive tutorial system
- `@insights` — Usage habit analysis and optimization report
- `@subagent` — Multi-agent task orchestration

**In-context Skills (2):**
- `@btw` — Side-channel quick Q&A without interrupting main task
- `@loop` — In-session periodic task runner

**Platform Support:**
- Codex CLI/App (with auto-format conversion, BOM-free UTF-8)
- Claude Code
- Antigravity / Gemini CLI
- Cursor (`.mdc` global rules)
- Windsurf Cascade
- OpenCode CLI
- Aider

**Project Templates:**
- Next.js
- Vite
- HTML

**Installers:**
- `install.ps1` (Windows)
- `install.sh` (macOS/Linux)
- Auto-backup of existing configs (`.bak` files)
