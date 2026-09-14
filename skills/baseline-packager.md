---
name: baseline-packager
description: 把用户要求保留的已验证行为固化为可重跑的回归基线。
metadata:
  risk: medium
  source: lotus
  date_added: "2026-05-11"
---

# Baseline packager
Bind a passing behavior to a repeatable check when the user requests a regression baseline.
- Identify the protected behavior and actual passing evidence. Do not freeze an unverified result.
- Reuse existing tests or add the smallest behavior-level fixture, snapshot, or script. Use browser automation only for browser behavior.
- Provide one independently runnable command that returns nonzero on failure, and document when relevant changes should run it.
- Keep fixtures deterministic and free of secrets. Do not weaken assertions to bless a regression.
Run the baseline and inspect its result. Report its coverage and limitations; creating a Git tag or changing CI is optional and must be within the request.
