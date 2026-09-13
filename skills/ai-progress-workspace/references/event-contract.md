# Event contract

Use a small stable vocabulary such as:

```ts
type JobEvent =
  | { type: "job.started"; jobId: string; at: string }
  | { type: "tool.started"; jobId: string; callId: string; name: string; at: string }
  | { type: "tool.completed"; jobId: string; callId: string; name: string; at: string }
  | { type: "artifact.created"; jobId: string; artifactId: string; kind: string; data: unknown; at: string }
  | { type: "artifact.patch"; jobId: string; artifactId: string; patch: unknown; at: string }
  | { type: "step.failed"; jobId: string; stepId: string; error: string; recoverable: boolean; at: string }
  | { type: "job.completed"; jobId: string; at: string };
```

Adapt names to the existing system rather than creating duplicates. Preserve ordering with a monotonic sequence. Store job state and events transactionally when a mismatch would make the UI lie.

SSE is a good default for one-way progress. Use WebSockets only for bidirectional live control or collaboration. Support reconnect from the last received sequence or event ID. A completed event should be emitted only after required artifact writes succeed.

Retries must identify whether a tool call is safe to repeat. Reuse the prior result or an idempotency key for external mutations. Cancellation should stop immediately when safe or record the checkpoint at which it will stop.
