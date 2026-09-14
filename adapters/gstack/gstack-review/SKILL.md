---
name: review
description: 审查用户指定的代码差异或 PR，查找可证实的缺陷与回归风险。
---

# Change review
Resolve the intended diff/base and read enough surrounding code to assess behavior. Prioritize correctness, security boundaries, data integrity, and missing regression coverage over style preferences.
Review only: do not edit code, commit, push, or merge unless the user also requests it.
Each actionable finding should identify the affected code, triggering conditions, impact, and a useful correction. Separate confirmed problems from hypotheses.
Use relevant checks when they can establish a finding; do not require every audit or a fixed number of findings. If none are found, say so and state meaningful untested areas.
Consult project-specific migration, deployment, or authorization rules only when the diff touches those surfaces.
