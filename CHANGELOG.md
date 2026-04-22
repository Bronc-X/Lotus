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

## [1.1.9] - 2026-04-22

### Changed

- Lotus global install now manages only Claude Code and Codex global paths; Gemini, OpenCode, Cursor, Windsurf, and Aider are no longer written during `install.ps1 -Global` / `install.sh --global`
- Managed official gstack setup and host-skill sync now run only for Claude/Codex, matching the narrowed installer scope
- README and `README_CN.md` now present `core/AGENTS.md` as the single source of truth for manual global-rule import in any non-managed host

## [1.1.8] - 2026-04-22

### Added

- New `web-to-design-md` Lotus skill that fuses website reference extraction with a structured website-design consultant workflow, producing `design.md` outputs and optional HTML previews from URLs, docs, screenshots, and pasted requirements

### Changed

- Codex skill conversion now grants `web-to-design-md` the search and file-editing tools it needs to actually inspect references and write design deliverables during global install
- README and `core/AGENTS.md` now position `web-to-design-md` as the pre-build design-planning step that pairs with `frontend-design`

## [1.1.7] - 2026-04-22

### Changed

- Lotus global install now separates official gstack top-level exposure from the full upstream skill set: the default `core` profile exposes only a curated official menu (`gstack`, `office-hours`, `plan-ceo-review`, `plan-design-review`, `plan-eng-review`, `design-review`, `review`, `investigate`, `browse`, `qa`, `ship`)
- Global install now supports official gstack top-level exposure profiles: `core`, `design`, `review`, `deploy`, and `full`
- README and global AGENTS guidance now explicitly explain the difference between user-visible top-level skills and hidden official gstack skills that remain in the upstream repo for AGENTS-based background routing

### Fixed

- Lotus host sync now removes stale official `gstack*` top-level directories that no longer belong to the selected profile, so old menu residue does not survive across upgrades

## [1.1.6] - 2026-04-22

### Changed

- Lotus global install now rewrites official top-level `gstack` skill descriptions to Chinese after upstream generation, so Codex/OpenCode/Cursor slash menus show localized explanations on both fresh installs and upgrades

### Fixed

- Global install now clears the stale Claude-managed `~/.claude/skills/gstack` checkout before rerunning upstream setup, preventing upgrade failures caused by non-idempotent official `gstack` host installs
- Added missing Chinese localization coverage for `gstack-checkpoint` and `gstack-connect-chrome`, so all current top-level official `gstack` skills land with localized descriptions

## [1.1.5] - 2026-04-21

### Changed

- README now includes an explicit post-install verification prompt users can send to an agent to check that host-global rules and top-level gstack skills are truly active
- README now makes the activation boundary explicit: the four Lotus rails become top-level rules through global install plus a fresh host session, not through a later chat prompt

## [1.1.4] - 2026-04-21

### Changed

- `core/AGENTS.md` now leads with four explicit execution rails: Think Before Coding, Simplicity First, Surgical Changes, and Goal-Driven Execution
- README now explains Lotus as an anti-hallucination rules layer in addition to an automation/install system
- Next.js template wording now clarifies backend-owned mock services instead of the vague "Mock engine" phrasing

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
