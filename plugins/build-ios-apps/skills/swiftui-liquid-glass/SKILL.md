---
name: swiftui-liquid-glass
description: 实现或审查明确采用 iOS 26+ Liquid Glass 的 SwiftUI 界面。
---

# SwiftUI Liquid Glass
Use native Liquid Glass APIs for the requested surface; do not convert unrelated UI or add glass merely because an app uses SwiftUI.
Read [references/liquid-glass.md](references/liquid-glass.md) for API patterns and examples. Verify uncertain availability against the installed SDK and Apple documentation.
- Match the project's deployment target and provide fallback when older OS versions are supported.
- Group related glass surfaces with GlassEffectContainer where needed.
- Apply glass effects after relevant layout/appearance modifiers; make only genuinely interactive surfaces interactive.
- Use glassEffectID and namespaces when a requested transition needs morphing, not as a universal requirement.
Preserve existing behavior and design intent. For review-only work report findings; for implementation inspect the affected rendering and interaction on supported targets.
