---
name: goal
description: 用户明确要求管理持久 Codex goal 时使用。
metadata:
  risk: medium
  source: lotus
  date_added: "2026-05-23"
---

# Goal
Use only for an explicitly requested persistent goal, not ordinary tasks that happen to have an objective.
Use the native goal tools or commands actually exposed by the current host. Inspect their schema before creating or updating state; do not assume pause, clear, or feature flags exist.
Record the observable objective, scope, completion evidence, and user-specified limits. Set a token budget only when the user provides one.
Mark complete only after the outcome and required checks pass. Mark blocked only under the host's stated conditions. Do not invent persistence, replace an unfinished goal, or change global settings to enable a missing feature without a setup request.
Report current state and any genuine missing capability concisely.
