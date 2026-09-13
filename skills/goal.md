---
name: goal
description: 用户要求创建、查看、完成或标记受阻的长期 Codex goal 时使用。
risk: medium
source: lotus
date_added: "2026-05-23"
---

# Goal

Use only when the user explicitly invokes `/goal` or asks to set, view, pause, resume, or clear a persistent Codex goal.

This skill is a Lotus top-level wrapper for Codex's native Goal mode. It does not reimplement persistence. When native Goal mode is available, route to the built-in `/goal` behavior and help the user shape the objective so Codex can continue across turns until the goal is satisfied or stopped.

## Native Commands

- `/goal <objective>` sets or replaces the active goal.
- `/goal` shows the current goal.
- `/goal pause` pauses active goal work.
- `/goal resume` resumes a paused goal.
- `/goal clear` removes the current goal.

If `/goal` is unavailable, enable the Codex feature in `~/.codex/config.toml`:

```toml
[features]
goals = true
```

Or, in Codex CLI environments that support it:

```bash
codex features enable goals
```

After changing feature flags, restart Codex or open a new session so slash commands are rescanned.

## Goal Shape

When setting a goal, prefer this structure:

1. **Objective**
   - State the desired user-visible outcome.
   - Include the exact bug, feature, migration, or cleanup target.

2. **Initial Context**
   - Name the files, directories, docs, issues, commands, or logs to inspect first.
   - Call out constraints such as frameworks, ownership boundaries, and files that must not change.

3. **Validation**
   - Define commands, tests, screenshots, browser checks, API calls, or artifacts that prove success.
   - Include both target validation and lightweight regression checks when risk is meaningful.

4. **Progress Checkpoints**
   - Ask Codex to keep a short running summary of what changed, what was verified, and what remains.
   - For long tasks, checkpoint after each meaningful milestone.

5. **Stop Conditions**
   - Stop when validation passes and the result has been checked for overfitting or hidden failures.
   - Stop and ask the user when requirements are ambiguous, the environment blocks validation, or continuing would require broad scope changes.

## Example

```text
/goal Fix the checkout total rounding bug.

First inspect src/checkout, src/pricing, and the failing checkout-total test.
Do not change payment gateway behavior.
Validate with npm test -- checkout-total and npm run build.
Keep progress notes after each iteration.
Stop when the failing case passes, related rounding cases still pass, and no assertions were weakened.
```

## Relationship To Other Lotus Skills

- Use `/agent-training-loop` when the user wants an explicit reproduce-detect-execute-check repair loop for a known bug.
- Use `/goal` when the user wants a persistent objective that may span multiple turns, tasks, or checkpoints.
- A goal may include instructions to apply `/agent-training-loop`, TDD, review, or other Lotus skills as sub-workflows.

## Hard Rules

- Do not claim native persistence if the Codex Goal feature is unavailable.
- Do not replace a precise user goal with a vague one.
- Do not continue beyond the user's stop conditions.
- Do not mark the goal complete without validation evidence.
