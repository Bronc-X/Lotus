---
name: subagent
description: 用户明确要求并行委派时拆分独立子任务并汇总。
---

# Subagent

Delegate only work that is independent enough to avoid duplicate reading and conflicting edits. Keep the main task’s scope, permissions, and safety boundaries unchanged.

- Give each sub-agent one bounded deliverable, the minimum context it needs, and a concise return format.
- Use parallel agents for independent research, logs, modules, or reviews; keep coupled decisions and overlapping files with one owner.
- Do not ask multiple agents to inspect the same evidence unless the user explicitly wants independent review.
- Treat returned claims as inputs to verify. The primary agent owns integration, conflict resolution, validation, and the final answer.
- Stop or redirect an agent whose work becomes redundant or leaves scope.

Completion means delegated outputs have been received or explicitly accounted for, integrated without overwriting unrelated work, and validated as part of the parent task.
