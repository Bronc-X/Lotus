# Lotus

> Global Agent Rules — Lotus.
> Before, every new project meant repetitive prompt imports, skill setups, and wasted time — forgetting that *building* is the only reason to open your editor.
> Now, you have Lotus. Write your engineering "Constitution" once, and deploy it everywhere.
> Lotus: the smart Docker for managing your Agents globally.

Lotus continuously leverages the **latest, safest, and most stable global agent management mechanisms**. By applying these rules to your local AI tools' global configurations, Lotus governs the behavior of your AI agents across **all** your projects simultaneously — without ever needing to write repetitive prompt instructions or perform tedious per-project setups.

Lotus now treats **official [garrytan/gstack](https://github.com/garrytan/gstack)** as the source of truth for the gstack runtime. Global install does two things in one shot:

1. Inject Lotus global rules into each agent's global config.
2. Clone or update official gstack into `~/.gstack/repos/gstack`, run upstream setup for supported hosts, and enable auto-updates.

**Platform Compatibility:**

| Platform | Auto-Inject Global? | Notes |
|---|---|---|
| Claude Code | ✅ Fully automatic | `~/.claude/CLAUDE.md` + official gstack runtime |
| Antigravity / Gemini CLI | ✅ Fully automatic | `~/.gemini/GEMINI.md` auto-loaded |
| Codex CLI | ✅ Fully automatic | `~/.codex/AGENTS.md` + official gstack runtime |
| OpenCode | ✅ Fully automatic | `~/.config/opencode/AGENTS.md` + official gstack runtime |
| Aider | ✅ Fully automatic | `~/.aider.conf.yml` |
| Windsurf | ⚠️ Manual paste | See steps below |
| Cursor | ⚠️ Manual paste | See steps below |

<details>
<summary>📋 Windsurf Manual Setup (click to expand)</summary>

1. Open Windsurf
2. Click the **Customizations icon** in the top-right
3. Navigate to **Rules**
4. Click the **"+ Global"** button
5. Copy and paste the full contents of `core/AGENTS.md`
6. Save — Cascade will now auto-load these rules for every session
</details>

<details>
<summary>📋 Cursor Manual Setup (click to expand)</summary>

1. Open Cursor
2. Open **Cursor Settings**
3. Navigate to **General** → find the **"Rules for AI"** input box
4. Copy and paste the full contents of `core/AGENTS.md`
5. Save — all AI conversations in every project will now carry these rules

> 💡 For project-level rules, create a `.cursor/rules/` folder in your project root with `.mdc` rule files. Lotus's `install.ps1 -Project` command will auto-generate these for you.

</details>

## 🧬 First Principles: Why Lotus Works

Stop chasing every flashy AI news headline. The anxiety is unnecessary.

At its core, every LLM—GPT, Claude, Gemini—is fundamentally doing one thing: converting your text into **high-dimensional vector embeddings**, processing them through transformer attention layers, and **predicting the most probable next token**. Understanding this single mechanism changes everything:

1. **Accuracy = Attention Precision**: The quality of AI output depends on how precisely the model's attention mechanism can lock onto your intent within the vector space. Lotus solves this by injecting **highly structured, unambiguous rules** that give the attention layers clear, high-signal targets. Vague prompts scatter attention; Lotus-formatted rules focus it like a laser.
2. **Context Window = The Only Bottleneck**: Every model has a finite context window. The real skill is not "knowing more prompts"—it's **managing what goes into that window**. Lotus uses a Hub-and-Spoke architecture to keep the global rules lean and universal, while project-specific details are layered separately, ensuring you never waste precious context tokens on redundant instructions.
3. **Persistence > Repetition**: Without Lotus, you re-explain your standards in every new chat session. With Lotus, your rules are **pre-loaded at the OS level** before the conversation even starts. The AI reads your constitution first, every time, automatically.

## ✨ Why Choose Lotus?

- 🧠 **Mindset Over Scripts**: Lotus teaches your AI *how to think* like a Senior Architect, PM, and QA. It enforces the "[GStack](https://github.com/garrytan/gstack) Workflow" (CEO Review -> Eng Review -> Code -> Global Review. Thanks to [GStack](https://github.com/garrytan/gstack) for the inspiration).
- 🌍 **Write Once, Run Everywhere**: A Single Source of Truth (`core/AGENTS.md`) automatically adapts and installs into Claude Code, Antigravity, Cursor, Windsurf, Copilot, and more.
- 🚧 **Zero Silent Failures**: Built-in quality gates guarantee your generated code includes proper user feedback, loading states, and aesthetic consistency.
- ⚡ **Seamless Wake-Up Calls (`@` and `/`)**: Summon specific expert personas and architectural overviews dynamically mid-chat using platform-native triggers.
- 🗑️ **Anti-Plugin Bloat**: 95% of plugins and skills on the market become stale junk within weeks. Lotus takes the opposite approach—every skill is **hand-curated, battle-tested, and minimally sufficient**. We only ship what survives real production workflows.
- 🔄 **Continuously Updated, Frontier-Tracked**: Lotus is a **living protocol**, not a static config dump. We actively track bleeding-edge releases from **Claude Code, Codex CLI, and top-tier open-source agent frameworks**, and fold the safest, most proven patterns back into `core/AGENTS.md` so your rules never go stale.
- 🧘 **Anti-Anxiety by Design**: New frameworks every week? Another "game-changing" plugin? Relax. LLMs are vector-based word predictors. The only things that actually matter are **vector precision** (clear rules) and **context management** (lean instructions). Lotus handles both. You handle building your product.

## 🚀 Zero-Foundation Quick Start (For Beginners)

Never used terminal commands? No problem.
If you are starting a new project or setting up a brand-new computer, simply **copy and paste the following prompt** directly into your AI assistant (e.g., Cursor, Claude, Antigravity) and it will handle the entire installation for you!

> "This is a brand new project. Please execute the following initialization steps locally:
> 1. Clone `https://github.com/Bronc-X/Lotus.git` into a temporary directory in the system.
> 2. Determine my OS. Run the installer inside the temporary repo to apply the `nextjs` template to my current directory (Windows: `install.ps1 -Project nextjs`, Mac/Linux: `install.sh --project nextjs`).
> 3. To make sure you retain our workflows globally on this new machine, also run the global install flag (Windows: `install.ps1 -Global`, Mac/Linux: `install.sh --global`).
> 4. Once finished, delete the temporary cloned repository.
> 5. Carefully read the newly generated `AGENTS.md` and `.agents/rules/` in my current directory to understand my coding standards and design language. Let me know when you are ready."

*(Note: Change `nextjs` to `vite` or `html` depending on your project type).*

### What about future new projects?

Once globally installed, Lotus core rules (workflows, quality gates) are **already active** in all your AI tools — **no wake-up needed**.

For Codex, that means Lotus writes to `~/.codex/AGENTS.md`, and Codex automatically loads those rules in every local repository you open. This is an inheritance mechanism, not a file sync, so you will **not** see a new `AGENTS.md` appear in each project unless you also run a project template install.

For Claude, Codex, and OpenCode, Lotus also manages the official gstack runtime at `~/.gstack/repos/gstack`. That runtime is global, updateable, and no longer copied from a stale Lotus snapshot.

If you want to add **project-level templates** (design systems, tech stack constraints) to a new project, just run once inside the project folder:

```powershell
# Windows
C:\Dev\Lotus\install.ps1 -Project nextjs
```
```bash
# macOS / Linux
~/Dev/Lotus/install.sh --project nextjs
```

That's it. Global rules are always on; project templates layer on top as needed.

## 🔌 Manual Installation

### Step 0: Clone Lotus to a permanent home

Pick a directory where Lotus will live permanently (you'll `git pull` here for updates):

**Windows (PowerShell):**
```powershell
git clone https://github.com/Bronc-X/Lotus.git C:\Dev\Lotus
```
**macOS / Linux:**
```bash
git clone https://github.com/Bronc-X/Lotus.git ~/Dev/Lotus
```

### Step 1: Global Installation (Configure all your IDEs)

This injects Lotus rules into the global config of every supported AI tool on your machine.

It also installs the **official gstack upstream** into `~/.gstack/repos/gstack`, runs upstream setup for Claude/Codex/OpenCode, and enables gstack auto-update so the skill runtime stays current.

For Codex specifically, the global install target is `~/.codex/AGENTS.md`. Local project folders remain untouched after this step. If you want a visible project-level `AGENTS.md` plus `.agents/rules/`, run Step 2 inside that project as well.

**Requirements for official gstack runtime:** `git`, `bash`, `bun`, and `node` on Windows.

> ⚠️ **Safe by design**: If you already have existing config files (e.g., `CLAUDE.md`, `GEMINI.md`, `.aider.conf.yml`), the installer will automatically create `.bak` backups before overwriting. You can always restore them.

**Windows (PowerShell):**
```powershell
C:\Dev\Lotus\install.ps1 -Global
```
**macOS / Linux:**
```bash
~/Dev/Lotus/install.sh --global
```

### Step 2: New Project Initialization (Optional)

Inside your empty new project folder, inject your preferred technology stack template:

**Windows (PowerShell):**
```powershell
cd C:\Users\YourName\Projects\MyNewApp
C:\Dev\Lotus\install.ps1 -Project nextjs
```
**macOS / Linux:**
```bash
cd ~/Projects/MyNewApp
~/Dev/Lotus/install.sh --project nextjs
```

*(Available templates: `nextjs`, `vite`, `html`)*

## 🎯 Tool Wake-Up Mechanisms (Skills)

You do not need to memorize complicated prompts; just remember a few simple commands. You can dynamically **wake up** specific expert personas exactly when you need them.

> 💡 **Why so few?** We deliberately keep the skill count small. Every skill here has survived months of real-world iteration across dozens of production projects. If a skill doesn't consistently deliver value, it gets **removed**, not "deprecated". Quality over quantity, always.

**How to Wake Them Up:**
The trigger syntax depends on whether you are using a visual IDE or a command-line agent:
* **For GUI IDEs (Cursor / Windsurf)**: Use the slash command `/name` (e.g., `/gstack`).
* **For CLI Agents (Claude Code / Antigravity / Aider)**: Use the mention format `@name` (e.g., `@gstack`).

### Available Wakes:

#### Lotus Core Skills (Cross-Platform)

1. **[`@gstack` / `/gstack`](https://github.com/garrytan/gstack)**
   * **What it does**: Lotus now delegates this to the official gstack upstream runtime it installs globally. Use the upstream workflow and specialist skills such as `/office-hours`, `/plan-eng-review`, `/review`, `/investigate`, `/qa`, and `/ship`.
2. **[`@test-driven-development` / `/test-driven-development`](https://github.com/Bronc-X/Lotus/blob/main/skills/test-driven-development.md)**
   * **What it does**: Forces strict Red-Green-Refactor constraints. The AI is forbidden from writing business logic until it writes a failing test. The ultimate anti-hallucination tool.
3. **[`@frontend-design` / `/frontend-design`](https://github.com/Bronc-X/Lotus/blob/main/skills/frontend-design.md)**
   * **What it does**: Vercel Labs-grade UI/UX boundaries. Blocks generic "AI aesthetic" layouts, forces explicit design stances (e.g. Brutalist, Editorial), and applies the Design Feasibility & Impact Index (DFII) before writing CSS/React.
4. **[`@debugging-strategies` / `/debugging-strategies`](https://github.com/Bronc-X/Lotus/blob/main/skills/debugging-strategies.md)**
   * **What it does**: Replaces raw guessing with a scientific debugging loop. Forces the AI to state hypotheses, write probing code to disprove them, and only apply fixes once the root cause is proven.
5. **[`@security-auditor` / `/security-auditor`](https://github.com/Bronc-X/Lotus/blob/main/skills/security-auditor.md)**
   * **What it does**: Deep DevSecOps review. Scans for OWASP Top 10 vulnerabilities, auth leaks, prototype pollution, and weak crypto. Run this before opening a PR.
6. **[`@feynman` / `/feynman`](https://github.com/Bronc-X/Lotus/blob/main/skills/feynman.md)**
   * **What it does**: Forces the AI to use the Feynman Technique. It will break down and explain complex bugs or mechanisms using absolute layman terms before attempting a fix.
7. **[`@polanyi-tacit` / `/polanyi-tacit`](https://github.com/Bronc-X/Lotus/blob/main/skills/polanyi-tacit.md)**
   * **What it does**: Wakes up a deeply analytical mode. The AI deliberately looks for architectural compromises, "defensive" code blocks, and unspoken organizational debt hidden behind the scenes.
8. **[`@auto-build` / `/auto-build`](https://github.com/Bronc-X/Lotus/blob/main/skills/auto-build.md)**
   * **What it does**: Silently performs `npm install`, runs `npm run build`, and checks for compilation errors without asking for your permission.
9. **[`@btw` / `/btw`](https://github.com/Bronc-X/Lotus/blob/main/skills/btw.md)**
   * **What it does**: Side-channel quick question mode. Ask a quick question mid-task without interrupting your main workflow. The AI answers in 3-5 sentences, modifies zero files, and seamlessly returns to the primary task.

#### Adapted from Claude Code Native Commands (Lotus ports to other platforms)

10. **[`@powerup` / `/powerup`](https://github.com/Bronc-X/Lotus/blob/main/skills/powerup.md)**
   * **When to use**: You're new to AI coding, or feel you're only using 10% of your AI's capabilities.
   * **What it does**: Think of it as the "Duolingo" for Claude Code — **10 structured lessons** covering everything from advanced prompt caching to background tasks.
11. **[`@insights` / `/insights`](https://github.com/Bronc-X/Lotus/blob/main/skills/insights.md)**
   * **When to use**: You want to see what habits you can optimize.
   * **What it does**: Generates a retrospective HTML report of your past month's coding habits, friction points, and debugging loops.
12. **[`@loop` / `/loop`](https://github.com/Bronc-X/Lotus/blob/main/skills/loop.md)**
   * **When to use**: You have recurring check tasks (e.g., poll deployment status every 5 minutes).
   * **What it does**: Sets up an in-session recurring task alarm clock. Session-scoped, safe, and controllable.
13. **[`@subagent` / `/subagent`](https://github.com/Bronc-X/Lotus/blob/main/skills/subagent.md)**
   * **When to use**: Complex tasks needing parallel execution.
   * **What it does**: Manage independent Subagents each with their own context window to prevent main-thread context overflow.

## 🏗️ Architecture (Hub-and-Spoke)

```text
Lotus/
├── core/                ← 🔶 Core Truth (Universal workflows, quality gates)
├── skills/              ← 🔶 Wake-up Skills (@gstack, @feynman, etc.)
├── templates/           ← 🔶 Tech stacks (Next.js, Vite) & Design languages
└── install scripts      ← 🤖 Auto-generates platform-specific IDE adapters
```

## 🛡️ Safety

Lotus touches your global IDE config files. We take this seriously:

- **Auto-Backup**: Before overwriting any existing file (`CLAUDE.md`, `GEMINI.md`, `.aider.conf.yml`, etc.), the installer automatically creates a `.bak` backup in the same directory. Nothing is silently lost.
- **Read-Only Rules**: Lotus only writes static Markdown files to config directories. It does **not** install executables, daemons, browser extensions, or background processes.
- **No Network Calls**: The install scripts run entirely offline. No telemetry, no analytics, no outbound requests. The only network operation is `git clone` / `git pull`, which you control.
- **Fully Reversible**: To completely uninstall Lotus, simply delete the injected files (e.g., `~/.claude/CLAUDE.md`, `~/.gemini/GEMINI.md`) or restore from the `.bak` backups. There is no registry, no system service, nothing hidden.

## 🔄 Update Philosophy

Lotus is **not a "set and forget" config**. It is a living, evolving protocol.

- **Primary tracking targets**: [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Codex CLI](https://github.com/openai/codex), and battle-tested open-source agent frameworks from top contributors.
- **What we track**: New global rule injection mechanisms, safer permission models, improved context-window strategies, and proven workflow patterns.
- **What we discard**: Hype-driven features, unstable APIs, and anything that adds complexity without measurable value.
- **The first-principles filter**: Before any new pattern is adopted, we ask: *Does this help vectors lock on more accurately? Does this reduce context waste?* If neither, it doesn't go in.
- **How to stay current**: Simply `git pull` and re-run the installer. Your global rules across all IDEs will be refreshed in seconds.

```bash
# Stay up to date in one command
cd /path/to/Lotus && git pull && ./install.sh --global
```
```powershell
# Windows equivalent
cd C:\path\to\Lotus; git pull; .\install.ps1 -Global
```

## 📌 Persistence: Set Up Once, Apply Forever

Once Lotus is installed globally, **every new project you create automatically inherits your rules**. No copy-pasting. No "remember to add the config file". The rules live at the OS-level global config of each AI tool, so they are always active—whether you're starting a fresh Next.js app, debugging a legacy codebase, or pair-programming on a colleague's machine.

On Codex, inheritance means the app reads `~/.codex/AGENTS.md` automatically when you open a local repo. It does **not** mean Lotus copies `AGENTS.md` into every repo on disk.

For supported hosts, the official gstack runtime is also global. Lotus keeps it in `~/.gstack/repos/gstack` and re-runs upstream setup on every global install, so "permanent" means both rules and runtime survive across repos and machine restarts.

For project-specific overrides (design systems, tech stacks), just use `install.ps1 -Project <template>` to layer on top. The global rules remain untouched.
