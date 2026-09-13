---
name: test-driven-development
description: Use red-green-refactor when the user or project explicitly requires test-first implementation.
---

# Test-driven development

Use this skill only when test-first work is requested or mandated by the project. Do not force it onto documentation, configuration-only changes, exploratory spikes, or work whose observable behavior cannot yet be specified.

For choosing test level, seams, and boundaries, read [references/test-design.md](references/test-design.md). Ordinary red-green-refactor work can proceed from the contract below.

## Contract

1. Define one observable behavior and the smallest test that proves it.
2. Run the test and confirm it fails for the expected reason. A syntax, fixture, or environment failure is not a valid red state.
3. Implement the smallest production change that makes the behavior pass.
4. Run the focused test, then relevant neighboring checks.
5. Refactor only while tests remain green.

Do not weaken assertions, encode the implementation instead of behavior, edit unrelated tests, or treat flaky infrastructure as a product failure. If the current design has no testable seam, create the smallest useful seam without broad restructuring.

Completion means the new test failed for the intended reason, the implementation passed it, relevant regression checks pass, and failures caused by the change were fixed and rechecked.
