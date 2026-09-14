---
name: swiftui-performance-audit
description: 诊断 SwiftUI 卡顿、过度更新、主线程负载或渲染性能问题。
---

# SwiftUI performance audit
Identify the symptom and affected flow from available code and evidence. Distinguish device vs Simulator and Debug vs Release measurements.
## Route
- Code-level investigation: [code smells](references/code-smells.md).
- Missing runtime evidence or capture setup: [profiling intake](references/profiling-intake.md).
- A formal audit report: [report template](references/report-template.md).
- Instruments-specific questions: [Instruments](references/optimizing-swiftui-performance-instruments.md).
- Hangs: [hang analysis](references/understanding-hangs-in-your-app.md).
- Update behavior: [SwiftUI performance](references/understanding-improving-swiftui-performance.md) or [WWDC23](references/demystify-swiftui-performance-wwdc23.md).
Read only the relevant guide. Capture the requested local profile when tools allow; ask the user only for evidence unavailable to the agent.
Tie findings to invalidation, identity, layout, main-thread work, image cost, or animation. A code smell is a hypothesis until supported by runtime evidence.
An audit does not authorize edits. When fixes are requested, change the responsible path and repeat comparable measurements. Do not claim improvement from incomparable captures or unmeasured intuition.
