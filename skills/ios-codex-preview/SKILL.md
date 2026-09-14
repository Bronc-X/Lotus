---
name: ios-codex-preview
description: 在可用的 macOS/Xcode 环境搭建或修复 iOS 模拟器网页预览。
---

# iOS Codex preview
Requires macOS, Xcode, and a reachable Simulator host. On Windows without such a host, report the missing environment; do not pretend local Simulator execution is possible.
For helper installation and lifecycle commands read [references/preview-setup.md](references/preview-setup.md). For a failing preview read [references/troubleshooting.md](references/troubleshooting.md).
Reuse the current project, scheme, bundle ID, simulator and helpers. Start only the preview components the request needs.
A working preview needs a fresh simulator frame, not just an HTTP response. When hot reload is requested, verify a change in a disposable fixture or a reversible task-scoped edit; do not leave arbitrary product text changes.
On Intel Macs use the bundled compatibility preview when serve-sim fails on architecture. On Apple Silicon prefer an already working native flow.
Only stop or disable helpers identified as owned by this preview task. Do not kill unrelated mirrors, watchers, or LaunchAgents.
Report the URL, relevant health results, and how to stop the helper. Do not claim runtime verification when only installation or static checks were possible.
