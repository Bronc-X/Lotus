---
name: investigate
description: 定位原因不明、反复出现或跨模块的软件故障。
---

# Root-cause investigation
Use available code, logs, tests, and runtime evidence to explain the failure. Simple localized bugs can use the project's normal fix workflow without this extended investigation.
Identify the observed failure and expected behavior; choose the smallest observation that distinguishes plausible causes. Follow the evidence across modules only as needed.
Diagnosis requests are read-only. For a requested fix, change the responsible path, preserve unrelated work, and verify the original symptom plus affected regressions.
Do not require context cards, plan-mode gates, fixed hypothesis counts, or reports after every step. Continue within scope while evidence advances; ask when a material choice, authority, or unavailable environment genuinely blocks progress.
Return the cause, supporting evidence, applied or proposed correction, and verification limits.
