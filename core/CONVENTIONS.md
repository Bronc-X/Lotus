# Coding Conventions

Use the repository's existing language, formatter, linter, test commands, naming, and module boundaries. This file supplies fallbacks only when a project has no more specific convention.

## Code

- Prefer the smallest change that preserves nearby behavior and style.
- In TypeScript projects that already use strict mode, keep new code type-safe and avoid unexplained escape hatches.
- Handle errors at the layer that owns recovery or user feedback; do not swallow failures.
- Do not commit credentials, machine-specific absolute paths, stray debug output, or unexplained placeholders.

## User-facing behavior

- New asynchronous paths should expose relevant running, success, failure, and empty states.
- New interactive controls should have usable keyboard/focus behavior and clear disabled or pending feedback where applicable.
- New responsive layouts should be checked at the viewports they claim to support.

## Verification

Run the narrowest existing checks that cover the changed behavior. Add broader builds or tests when the change can affect compilation, integration, packaging, or deployment. Fix failures caused by the change and rerun the affected checks before completion.
