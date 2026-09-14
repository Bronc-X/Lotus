---
name: swiftui-ui-patterns
description: 实现 SwiftUI 屏幕的导航、状态归属、布局或交互组件。
---

# SwiftUI UI patterns
Follow the existing app architecture and deployment target. Read a nearby relevant view before introducing new patterns.
## Route
- Component-specific work: [component index](references/components-index.md), then only the chosen component.
- App shell and root dependencies: [app wiring](references/app-wiring.md).
- Navigation or deep links: [navigation](references/navigationstack.md), [deep links](references/deeplinks.md).
- Modal presentation: [sheets](references/sheets.md).
- Loading, cancellation, debounce: [async state](references/async-state.md).
- Preview fixtures: [previews](references/previews.md).
- Scroll reveal interaction: [scroll reveal](references/scroll-reveal.md).
- Large or frequently updating surfaces: [performance](references/performance.md).
## Ownership
Use local State and explicit Binding for view-owned value state. For iOS 17+ reference observation use Observable with ownership at the appropriate parent; support older targets through the existing ObservableObject wrappers.
Use environment for genuinely shared services, explicit inputs for local dependencies, and stable identity in lists. Do not introduce global routers, view models, or AnyView merely to satisfy a template.
Implement only the requested surface. Run the relevant build, preview, or interaction checks after a coherent change; avoid rebuilding after every intermediate edit. Fix failures within scope and report any unavailable runtime verification.
