---
name: codex-history-bridge
description: 查找本地 Codex 旧对话，或诊断恢复时的 provider 与配置错误。
---

# Codex history bridge

Treat history discovery, task loading, provider selection, and a successful model reply as separate outcomes. Switching providers does not download history; task IDs and local storage locate messages, while provider configuration controls future requests.

## Route the request

1. Start with the bundled read-only inspector:

   ```text
   python "<skill-dir>/scripts/inspect_history.py"
   python "<skill-dir>/scripts/inspect_history.py" --query "project or task ID" --limit 12
   python "<skill-dir>/scripts/inspect_history.py" --provider custom --limit 12
   ```

2. For locating, opening, or diagnosing missing local history, read [references/history-discovery.md](references/history-discovery.md).
3. Only when the user asks to continue a task through ChatGPT or a third-party provider, read [references/provider-switching.md](references/provider-switching.md).
4. After a configuration change or requested resume, read [references/verification.md](references/verification.md).

Do not load switching guidance for a read-only history search. This skill does not handle other chat applications or cloud-history import.

## Boundaries

- Do not print credentials or chat bodies during inventory. Search IDs, titles, working directories, provider metadata, and only the smallest relevant history segment.
- Do not rebuild databases, rewrite task records in bulk, hijack the built-in `openai` provider, or copy ChatGPT authentication into a third-party provider.
- A provider name is not proof of its vendor. Compare the task’s recorded provider, the current definition, and the user’s requested destination.
- Configuration changes require a private byte-for-byte backup with SHA-256. Restore only the relevant provider/default fields so newer unrelated settings survive.
- If the user has already selected the provider and scope, make the scoped local change and verify it without asking again. Ask only when the destination, credentials, or external effect is genuinely unresolved.

Completion means the requested history was found or its absence was evidenced, the task loads through the intended provider when requested, configuration parses, affected behavior is rechecked after fixes, and the report states whether an actual model reply was verified.
