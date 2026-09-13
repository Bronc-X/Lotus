# Provider switching

Classify the failure before editing: missing provider, TOML parse error, authentication failure, network failure, or incompatible history. Provider aliases address only the first class.

## Before editing

- Inspect the current Codex version, supported configuration fields, and project-level overrides.
- Back up the current configuration byte-for-byte in a private local work directory; record SHA-256, time, and the original provider mapping. The backup may contain credentials and must not enter Git or chat output.
- Preserve complete third-party definitions, including environment-variable references, headers, and protocol fields.
- If an overwritten third-party definition cannot be recovered from a trusted local backup, obtain its endpoint, model, and authentication method from the user. Do not guess or reuse a ChatGPT login token.

## Continue with ChatGPT

Confirm the current login type is ChatGPT and prefer a supported per-task provider override. When an old task references a missing alias, a compatible definition may map that exact alias to the official Codex backend:

```toml
[model_providers.custom]
name = "OpenAI"
base_url = "https://chatgpt.com/backend-api/codex"
wire_api = "responses"
requires_openai_auth = true
supports_websockets = true
```

Apply this to the actual missing name, not automatically to `custom`. It redirects future requests for that alias to the official service and does not preserve a third-party connection. New tasks should continue to use the built-in `openai` provider.

## Continue with a third party

Restore the user-selected or reliably saved provider definition. Changing the default provider does not necessarily change a provider stored on an old task. For tasks recorded as `openai`, use only a provider override supported by the installed task-resume interface and verify whether it persists after reopening.

Do not define `[model_providers.openai]`, edit task databases or rollout messages in bulk, delete encrypted content, or claim permanent migration without reopen evidence. If the installed version cannot switch an existing task safely, preserve the task and explain the limitation; create a new task or fork only when the user asks.
