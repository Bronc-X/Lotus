---
name: agent-training-loop
description: 用户明确调用 agent-training-loop 时，循环修复可复现 Bug，直到通过或达到停止条件。
risk: medium
source: lotus
date_added: "2026-05-11"
---

# Agent training loop

Use only when explicitly invoked. Iterate on one reproducible objective without weakening its validation.

Before editing, identify the failing behavior, the command or observation that measures it, the allowed change area, and the stop conditions. Tests are part of the contract; change them only when evidence shows the contract itself is wrong.

For each iteration:

1. Reproduce the current failure.
2. Use the new signal to choose the smallest plausible change.
3. Apply the change and rerun the same validation.
4. When it passes, run relevant neighboring checks and inspect for hardcoded data, weakened assertions, swallowed errors, or fixture pollution.

Continue autonomously while each iteration produces new evidence and remains within scope. Stop when validation passes, the configured iteration limit is reached, two consecutive attempts add no new signal, requirements are contradictory, or the environment cannot exercise the behavior. Default to five iterations when the user gives no limit.

Report the final result and concise evidence, not a narrative of every internal step. Completion requires the target and relevant regression checks to pass after any fixes.
