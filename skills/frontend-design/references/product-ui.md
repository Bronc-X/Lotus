# Product UI

Start from the task, user role, primary decision, and data density. Reuse current tokens, spacing, typography, icons, and interaction patterns. Introduce a new component only when existing components cannot express the behavior clearly.

For dense surfaces, prioritize scan order, alignment, stable column widths, filters, pagination or virtualization, and useful empty/error recovery. For forms and workflows, make validation, progress, save state, cancellation, and destructive actions explicit. For dashboards, tie each metric and chart to a decision; omit decorative analytics.

Responsive behavior should preserve task priority rather than merely stack everything. Decide which content wraps, collapses, scrolls, moves behind disclosure, or remains fixed. Keep touch targets and keyboard navigation usable.

Use motion for continuity, state change, and spatial orientation. Respect reduced-motion preferences and avoid animation that delays frequent work.

Inspect at least the main success path and relevant failure/empty states. Check overflow, truncation, focus order, contrast, disabled behavior, network latency feedback, and console errors.
