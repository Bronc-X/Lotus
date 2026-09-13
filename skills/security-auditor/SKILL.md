---
name: security-auditor
description: Audit a codebase or change for authentication, authorization, secrets, injection, dependency, configuration, or data-protection risks.
---

# Security auditor

Use this for an explicit security review, vulnerability investigation, or security-sensitive change. Ordinary coding tasks that merely touch configuration or dependencies do not automatically require a full audit.

Read [references/audit-guide.md](references/audit-guide.md) for the checklist relevant to the requested system and threat surface. Do not apply every checklist category when it cannot affect the task.

## Contract

- Establish assets, trust boundaries, attacker capabilities, entry points, privileged actions, and sensitive data before rating findings.
- Prefer evidence from code paths, configuration, dependency metadata, tests, and reproducible behavior. Separate confirmed findings from hypotheses.
- Rank findings by exploitability and impact in the actual deployment, not by generic severity alone.
- Do not print secrets, exploit production systems, broaden access, or perform destructive proof-of-concept actions.
- When the user asks for fixes, apply the smallest effective remediation, run relevant security and regression checks, fix failures, and recheck.

Completion means the scoped surface was examined, findings contain evidence and actionable remediation, requested fixes are verified, and residual risk or untested assumptions are explicit.
