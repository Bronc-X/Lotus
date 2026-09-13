---
name: swiftui-view-refactor
description: Refactor large SwiftUI views and clarify data flow or Observation ownership without changing behavior.
---

# SwiftUI view refactor

Refactor toward small, explicit view types while preserving layout and behavior. Follow the project’s existing architecture; do not introduce a view model merely to mirror local state or wrap environment dependencies.

For a substantial view split, Observation ownership change, or MV/MVVM decision, read [references/refactor-guide.md](references/refactor-guide.md) and [references/mv-patterns.md](references/mv-patterns.md). Small ordering or extraction changes need only the relevant guide section.

Prefer dedicated subviews for meaningful sections, explicit inputs and bindings, thin view actions, stable view identity, and business logic in existing services or models. Match `@State`, `@StateObject`, `@ObservedObject`, and `@Observable` ownership to the deployment target and current architecture.

Completion means behavior remains unchanged, the refactored code builds, relevant tests or previews pass, and failures caused by the refactor have been fixed and rechecked.
