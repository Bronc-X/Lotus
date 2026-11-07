---
name: gstack
description: gstack 统一入口：按需求路由产品规划、网页检查、故障排查、测试、代码审查和交付工作流。
---

# Lotus gstack adapter
This is a Lotus-maintained instruction adapter, not an upstream gstack snapshot. Runtime binaries remain upstream-managed.
This is the only top-level entry for the suite. Child adapters remain installed as internal references. Read the selected child file directly; do not require its presence in the skill picker, ask the user to invoke a hidden child, or re-enable child entries.
Route only the requested work:
- Product discovery or scope tradeoffs: office-hours.
- Complex root-cause investigation: investigate.
- Browser inspection: browse.
- Requested test-and-fix: qa.
- Read-only change review: review.
- Explicit commit, push, PR, or release: ship.
Load only the selected sibling adapter (gstack-<name>/SKILL.md under the same skills parent), not the entire suite.
For a specialized upstream workflow not covered here, locate its installed skill and read it only when requested or necessary. Installation, telemetry, upgrades, and external writes are not implied by this router.
