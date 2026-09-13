---
name: frontend-design
description: Implement or improve functional web application UI when layout, hierarchy, responsive behavior, or interaction states are part of the task.
---

# Frontend design

Use this for product interfaces such as dashboards, forms, workflows, tables, and application screens. Use `taste-skill` instead for premium marketing, portfolio, or editorial sites.

Read [references/product-ui.md](references/product-ui.md) when the task changes a complete screen or interaction flow. Small local UI fixes can use the shared constraints below without loading the reference.

## Shared constraints

- Follow the existing design system and component library before adding a new pattern.
- Make hierarchy, primary action, grouping, and navigation obvious from layout, not decoration.
- Preserve behavior and data flow unless the request includes changing them.
- Cover the loading, success, error, empty, disabled, focus, and responsive states the changed feature can actually enter.
- Use real content shapes and realistic data density; do not invent claims or hide missing states behind placeholders.
- Check the rendered result at the viewports and interaction states affected by the change.

Completion means the requested UI is implemented, affected states and interactions work, the result has been rendered and inspected, and any issues found have been fixed and rechecked.
