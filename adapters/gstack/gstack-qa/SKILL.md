---
name: qa
description: 按用户要求验证网页流程并修复发现的范围内问题。
---

# Web QA and repair
Establish the target URL, flows, expected behavior, and whether the request includes fixes. Use the available supported browser; read the browse adapter only when its runtime is needed.
Exercise the affected user path and relevant states. Record reproducible failures with enough evidence to locate the cause.
For test-only requests, report findings without changing source. For test-and-fix, make focused corrections and rerun failed cases plus affected regressions.
Use test accounts and disposable data. Do not submit real purchases, send messages, alter production records, or load personal cookies without authorization.
Do not commit each fix automatically or expand to full-site testing unless the scope warrants it.
Report what was exercised, what passed, actual defects, corrections, and any blocked coverage.
