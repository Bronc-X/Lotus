---
name: ai-progress-workspace
description: Build AI products whose progress UI is driven by real tool events and structured artifact changes.
---

# AI progress workspace

Use this skill when the product needs a central editable artifact and a truthful view of long-running AI work. Do not use it for decorative loaders or ordinary request/response chat.

## Route

- For event names, persistence, replay, cancellation, and failure semantics: read [references/event-contract.md](references/event-contract.md).
- For choosing an editor or canvas and wiring tools to artifacts: read [references/workspace-implementation.md](references/workspace-implementation.md).

Load both only when implementing the end-to-end system.

## Invariants

- Display only observable work: a job, tool call, API operation, artifact mutation, failure, retry, approval, or completion event.
- Never present private model reasoning or invented exact percentages as telemetry.
- Give jobs, events, artifacts, and tool calls stable IDs. Persist enough state to restore after refresh and replay missed events.
- Insert model output into the workspace through validated structured data, not unparsed prose.
- Long-running work needs cancellation, recoverable failure states, and idempotent retry behavior appropriate to its side effects.
- Prefer the existing application stack and the simplest orchestration model that satisfies the workflow.

Completion means a real job updates the progress surface and editable artifact, refresh/replay works, cancellation and a forced failure behave safely, invalid artifacts are rejected, and all affected paths pass after fixes and rechecks.
