---
name: workflow
description: 将用户要求固化的已验证执行记录整理为可复用工作流或 Skill。
---

# Workflow

Distill a real successful execution into a reusable path. Plans, prompts, and unverified drafts may produce a `DRAFT`, but they are not evidence of a proven workflow.

## Route

- To reconstruct and simplify the executed path: read [references/distillation-method.md](references/distillation-method.md).
- To create a workflow pack or Codex Skill: read [references/package-contract.md](references/package-contract.md).
- To claim `VERIFIED`, irreducible, shortest, or optimal: read [references/validation.md](references/validation.md).

Load only the references needed for the requested output and claim level.

## Invariants

- Freeze the accepted result, scope, and evidence before optimizing the path.
- Preserve correctness, permissions, safety, privacy, traceability, reproducibility, and diagnosable failure behavior.
- Separate stable invariants from project defaults, conditional branches, local details, and detours.
- Do not promote a one-off failure into a universal rule without repeatable evidence.
- Removing steps can prove irreducibility only within the tested scope. “Shortest” requires comparison with other passing candidates; do not claim global optimality.
- A workflow does not grant deployment, publication, deletion, production mutation, or other permissions absent from the original task.

The bundled scripts can create and validate a workflow pack. Preview untrusted validation commands before execution; the runner is not a sandbox.

Completion means a real success case is bound to the workflow, relevant negative cases and gates work, a fresh execution can follow the package, failures have been fixed and rechecked, and the evidence level is reported without overstating optimization.
