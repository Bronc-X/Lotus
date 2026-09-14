---
name: gstack
description: 用户明确使用 gstack 或询问其工作流选择时路由。
---

# Lotus gstack adapter
This is a Lotus-maintained instruction adapter, not an upstream gstack snapshot. Runtime binaries remain upstream-managed.
Route only the requested work:
- Product discovery or scope tradeoffs: office-hours.
- Complex root-cause investigation: investigate.
- Browser inspection: browse.
- Requested test-and-fix: qa.
- Read-only change review: review.
- Explicit commit, push, PR, or release: ship.
Load only the selected sibling adapter (gstack-<name>/SKILL.md under the same skills parent), not the entire suite.
For a specialized upstream workflow not covered here, locate its installed skill and read it only when requested or necessary. Installation, telemetry, upgrades, and external writes are not implied by this router.
