# Shadcn preset refactor workflow

## Goal

Apply a shadcn/create preset to an existing frontend without damaging business logic, routes, data flow, or user edits. Treat the preset as a design-system input, not a license to rewrite the app.

## Required Inputs

- Project path. If omitted, use the current working directory.
- shadcn/create preset code, for example `b2D0wqNxT`.
- Scope if provided: whole app, only theme, only font, only a target route, or a local UI lab.

If the preset code is missing, ask for it before changing files.

## Safety Contract

- Preserve existing functionality, routing, API calls, state management, auth, and business copy unless the user explicitly requests changes.
- Never run destructive git commands such as `git reset --hard` or `git checkout --`.
- Never overwrite unrelated user edits. Work with dirty files instead of reverting them.
- Use `shadcn apply` for preset migration. Use manual edits only for integration gaps or UI polish.
- Use `shadcn add --dry-run` before adding new blocks/components when the change is not already implied by the current code.
- Do not use `--overwrite` unless the user explicitly approves or the diff has been inspected and the file is clearly generated shadcn UI code.

## Workflow

### 1. Preflight

1. Identify the package manager from lockfiles: `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`, `bun.lockb`.
2. Inspect project shape: framework, `package.json`, `components.json`, Tailwind config, CSS entry files, app routes/pages.
3. Run:

```bash
git status --short
npx shadcn@latest preset decode <preset>
npx shadcn@latest info
```

On Windows PowerShell, quote registry namespaces such as `'@shadcn'`.

If `shadcn info` fails because the project is not initialized, decide whether this is still a compatible React/Tailwind project. If compatible, initialize with the preset. If not compatible, explain the blocker before editing.

### 2. Baseline

Before applying the preset, capture enough evidence to prove behavior is preserved:

- Current git diff summary.
- Existing `components.json`, global CSS, Tailwind config, and `components/ui` state if present.
- For visible apps, current screenshots of the primary route(s) when a dev server can run.
- Existing build/lint/test commands from `package.json`.

If the repo is not under git, create a timestamped backup under `.codex/shadcn-preset-refactor/` for touched config/CSS/UI files before applying the preset.

### 3. Apply Preset

For an initialized shadcn project:

```bash
npx shadcn@latest apply <preset>
```

For only theme or font when requested:

```bash
npx shadcn@latest apply <preset> --only theme
npx shadcn@latest apply <preset> --only font
npx shadcn@latest apply <preset> --only theme,font
```

For a compatible project that has not been initialized:

```bash
npx shadcn@latest init -p <preset>
```

Prefer the repository's package manager equivalent when obvious, for example `pnpm dlx shadcn@latest ...`.

### 4. Add Missing UI Only When Needed

If the redesign needs shadcn blocks or components, search first:

```bash
npx shadcn@latest search '@shadcn' -t block -q dashboard
npx shadcn@latest search '@shadcn' -t ui -q select
npx shadcn@latest docs chart select combobox tabs --json
```

Preview additions before writing:

```bash
npx shadcn@latest add <component-or-block> --dry-run
```

Then add only the required items:

```bash
npx shadcn@latest add button card input select tabs chart sidebar
```

Do not add all components by default.

### 5. Integrate Without Breaking Product Code

- Keep existing route structure and component boundaries where possible.
- Replace visual shells, layout, tokens, and presentational components before touching data logic.
- Move toward shadcn components gradually: buttons, inputs, cards, navigation, tables, charts.
- Keep loading, empty, error, and disabled states visible after the redesign.
- Preserve accessibility labels, form names, keyboard navigation, and validation messages.
- For dense SaaS/admin/productivity UIs, prefer functional layouts over landing-page composition.

### 6. Verify

Run the cheapest credible checks available:

```bash
npm run build
npm run lint
npm test
```

Use the actual package manager and only run scripts that exist. If a dev server is needed, start it and inspect the key route(s) in a browser:

- Desktop and mobile viewport.
- No obvious text overflow or overlapping controls.
- Sidebar/navigation still works.
- Forms and key buttons still respond.
- Charts/tables render when present.
- Dark/light mode still looks intentional if supported.

### 7. Review Diff

After applying:

```bash
git diff --stat
git diff -- components.json
git diff -- <global-css-file>
```

Inspect any changed `components/ui/*` files before finalizing. If the preset touched custom user-modified UI primitives in a risky way, summarize the risk and either adapt carefully or ask before overwriting.

## Final Response

Report:

- Preset code and decoded design choices.
- Whether the project was already shadcn-initialized.
- Main files changed.
- Validation commands and results.
- Any residual risks or manual follow-ups.

Use plain language. Do not emit git stage/commit/push directives unless the host explicitly requires them.
