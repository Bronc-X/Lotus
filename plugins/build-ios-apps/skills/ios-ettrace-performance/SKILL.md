---
name: ios-ettrace-performance
description: Capture and interpret iOS Simulator ETTrace profiles for latency and CPU-heavy stacks.
---

# iOS ETTrace performance

Use this skill for one focused launch or runtime performance flow. Use `ios-debugger-agent` as well only when the task also needs build, install, launch, UI driving, logs, or screenshots.

Read [references/full-workflow.md](references/full-workflow.md) before instrumenting or capturing. The guide contains the version-sensitive setup, dSYM, capture, preservation, analysis, and cleanup commands. Use the bundled scripts for dSYM collection and flamegraph analysis rather than recreating them.

Keep ETTrace wiring temporary unless the user asks to retain it. Do not draw conclusions from an unsymbolicated first-party stack or from stale/raw JSON. One capture should correspond to one stated user-visible flow.

Completion means fresh processed output is preserved, important first-party symbols resolve, hotspots are tied to the measured flow, temporary wiring is cleaned up when required, and comparable checks are rerun after any fix.
