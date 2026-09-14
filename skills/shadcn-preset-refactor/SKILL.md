---
name: shadcn-preset-refactor
description: 将指定 shadcn preset 应用于现有前端，保留业务行为。
---

# Shadcn preset refactor

Treat the preset as a design-system input, not permission to rewrite the application.

Read [references/full-workflow.md](references/full-workflow.md) before applying a preset to an existing project. A review or feasibility question can use only the relevant section.

Preserve business logic, routes, data flow, analytics, accessibility, and unrelated dirty files. Inspect the preset output in a disposable location, map its tokens and primitives to the existing system, then migrate the smallest coherent surface. Do not use destructive Git commands to recover from conflicts.

Completion means the selected surface uses the intended preset, existing behavior remains intact, relevant builds and tests pass, the rendered result is inspected at affected viewports, and failures have been fixed and rechecked.
