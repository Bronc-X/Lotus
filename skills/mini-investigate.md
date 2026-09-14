---
name: mini-investigate
description: 修复范围清楚、可局部验证的小型软件 Bug。
metadata:
  risk: medium
  source: lotus
  date_added: "2026-06-02"
---

# Minimal bug fix
Find evidence for the cause, apply the smallest sufficient correction, and recheck the original symptom.
- Use existing reproduction steps, logs, tests, or a focused runtime check. Ask only for missing information that cannot be obtained safely.
- Preserve verified conclusions, but revisit them when new evidence contradicts them.
- A diagnosis request is read-only; implement only when the user asks for a fix.
- Keep changes related to the failure. File count is not a stop condition; expand investigation when evidence shows cross-module causes, not by imposing an arbitrary template.
- Do not weaken assertions, swallow errors, or hide symptoms. A narrow supporting refactor is acceptable when needed for the requested fix.
- Validate the affected behavior and relevant neighboring paths. If the environment cannot reproduce it, distinguish static evidence from runtime verification.
Report cause, correction, checks, and any remaining uncertainty without mandatory context cards or per-step reports.
