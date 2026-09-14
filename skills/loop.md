---
name: loop
description: 用户用 loop 或 @loop 要求定期检查任务状态时使用。
---

# Loop
Extract the target, interval, stopping condition, and notification preference from the request.
Use the host's supported monitoring or scheduling mechanism. For an explicitly session-only wait, use supported waits and explain its lifetime; do not promise persistence the host cannot provide.
- Do not create system cron jobs or background daemons as a substitute for an available host mechanism.
- Unchanged state is normal. Do not stop or ask to continue merely because several checks return the same result.
- Notify on completion, meaningful change, actionable failure, or requested updates; remain quiet otherwise.
- Repeated checking does not authorize repeated deployment, publication, purchases, or destructive actions. Preserve the granted scope and verify authorization before external effects.
Stop at the user's condition or cancellation. If scheduling is unavailable, state that limitation instead of claiming the loop was installed.
