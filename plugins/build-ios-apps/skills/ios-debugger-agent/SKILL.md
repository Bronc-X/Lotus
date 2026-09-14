---
name: ios-debugger-agent
description: 使用 XcodeBuildMCP 构建、运行或排查 iOS 模拟器中的应用。
---

# iOS debugger
Use available XcodeBuildMCP tools or the project's existing Xcode commands on a macOS host. Inspect exposed tool schemas rather than assuming a fixed prefix.
- Resolve the requested project/workspace, scheme, and simulator. Reuse a suitable booted simulator; boot an available suitable one when running the app is in scope. Ask only when device choice materially affects the result.
- Set session defaults to that project and device. Build only when needed; launch an existing build for a launch-only request.
- Inspect build errors and fix task-scoped failures without repeated approval. Do not treat a failed build as a launched app.
- Inspect the current UI before interaction and refresh observations after layout changes. Prefer labels or IDs over guessed coordinates.
- Capture logs only for the relevant app and stop captures when finished.
For diagnosis-only requests, return evidence and proposed remediation; do not edit the app. For requested fixes, verify the original symptom after rebuilding and inspect relevant regressions.
