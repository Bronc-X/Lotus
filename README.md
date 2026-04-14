# AGENTRULES

> A universal, cross-platform, "out-of-the-box" rule repository for all major AI coding agents.

Write rules once, deploy everywhere. This repository maintains a "Single Source of Truth" (`core/AGENTS.md`) for your engineering workflows, quality gates, and AI agent skills, and provides auto-install scripts to inject them into the global configuration of every modern AI coding platform.

## Supported Platforms

The installer automatically configures global settings for:

- ✅ **Claude Code** (`~/.claude/CLAUDE.md` and `.claude/skills/`)
- ✅ **Antigravity / Gemini CLI** (`~/.gemini/GEMINI.md` and `.gemini/antigravity/skills/`)
- ✅ **OpenCode CLI** (`~/.config/opencode/AGENTS.md`)
- ✅ **Windsurf Cascade** (`~/.windsurf/rules/global.md`)
- ✅ **Codex CLI** (`~/.codex/AGENTS.md`)
- ✅ **Aider** (`~/.aider.conf.yml`)
- ✅ **Cursor** (via project templates)
- ✅ **GitHub Copilot** (via project templates in `.github/`)

## Quick Start

### 1. Global Installation (Configure all your IDEs)

Run the installer to inject the core rules and skills into all your tools globally:

**Windows (PowerShell):**
```powershell
.\install.ps1 -Global
```

**macOS / Linux:**
```bash
./install.sh --global
```

### 2. New Project Initialization

When starting a new project, use the installer to automatically copy the right template, tech stack definitions, and path-specific rules:

**Windows:**
```powershell
# Inside your empty new project folder
C:\path\to\AGENTRULES\install.ps1 -Project nextjs
```

**macOS / Linux:**
```bash
/path/to/AGENTRULES/install.sh --project nextjs
```

*(Currently available templates: `nextjs`, `vite`, `html`)*

### 3. The Auto-Init Prompt (Day-0 Universal Start)

If you are starting a new project on a **brand-new computer, cloud server, or different terminal**, just paste the following prompt to your AI coding agent. It will securely fetch your rules from GitHub, install them globally on the new machine, configure the local project, and clean up after itself:

> "This is a brand new project directory. Please execute the following initialization steps locally:
> 1. Clone `https://github.com/Bronc-X/AGENTRULES.git` into a temporary directory in the system.
> 2. Determine my OS. Run the installer inside the temporary repo to apply the `nextjs` template to my current directory (Windows: `install.ps1 -Project nextjs`, Mac/Linux: `install.sh --project nextjs`).
> 3. To make sure you retain our workflows globally on this new machine, also run the global install flag (Windows: `install.ps1 -Global`, Mac/Linux: `install.sh --global`).
> 4. Once finished, delete the temporary cloned repository.
> 5. Carefully read the newly generated `AGENTS.md` and `.agents/rules/` in my current directory to understand my coding standards and design language. Let me know when you are ready."

## Architecture (Hub-and-Spoke)

```text
AGENTRULES/
├── core/                ← 🔶 Single Source of Truth
│   ├── AGENTS.md        (Universal workflows, review processes, quality gates)
│   └── CONVENTIONS.md   (Clean code guidelines)
├── skills/              ← 🔶 Universal Skills (@gstack, @feynman, etc.)
├── templates/           ← 🔶 Project templates (Tech stacks, color palettes)
└── install scripts      ← 🤖 Auto-generates platform-specific adapters
```

## Included Skills

Once installed globally, you can invoke these skills by mentioning them (`@name`) in your agent's chat prompt in **any project**:

1. `@gstack`: Developer workflows and persona switching (PM, Architect, Coder, QA).
2. `@vibe`: Vibe Coding mode. Delegate technical aesthetics entirely to AI, prioritizing visual elegance and silent iteration without asking boilerplate questions.
3. `@feynman`: Complex topic breakdown explaining the core "gears".
4. `@polanyi-tacit`: Decoding defensive code and organizational debt.
5. `@auto-build`: Silent compilation verification.

## Customization

1. **Edit Global Rules:** Modify `core/AGENTS.md` and run the installer again with the global flag. It will overwrite the platform-specific files.
2. **Edit Project Templates:** Open `templates/nextjs/.agents/rules/` to customize the design system and tech stack boilerplate for your future apps.
3. **Add Skills:** Drop standard Markdown files into `skills/` and re-run the global installer. They will be distributed to Claude, Antigravity, and other compatible platforms.
