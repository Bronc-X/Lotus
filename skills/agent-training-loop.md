---
name: agent-training-loop
description: 用户明确要求迭代修复可复现 Bug 时，按新证据推进并验证。
metadata:
  risk: medium
  source: lotus
  date_added: "2026-05-11"
---

# Agent training loop

Use when explicitly requested by name or as an iterative bug-repair workflow. Iterate on one reproducible objective without weakening its validation.

Before editing, identify the failing behavior, the command or observation that measures it, the allowed change area, and the stop conditions. Tests are part of the contract; change them only when evidence shows the contract itself is wrong.

For each iteration:

1. Reproduce the current failure.
2. Use the new signal to choose the smallest plausible change.
3. Apply the change and rerun the same validation.
4. When it passes, run relevant neighboring checks and inspect for hardcoded data, weakened assertions, swallowed errors, or fixture pollution.

Continue while iterations produce useful evidence within scope and the user's limits. Reassess when attempts stop adding signal; stop for a genuine evidence, environment, or authority blocker. Do not impose an arbitrary default iteration cap or weaken validation to finish.

Report the final result and concise evidence, not a narrative of every internal step. Completion requires the target and relevant regression checks to pass after any fixes.
