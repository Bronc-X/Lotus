# Coding Conventions

> This file is referenced by Aider via `.aider.conf.yml` and can be used by any tool that supports a `CONVENTIONS.md` file.
> Full workflow rules are in `AGENTS.md`.

## General

- Use TypeScript strict mode where applicable
- Prefer `const` over `let`; never use `var`
- Use async/await over raw Promises
- Every `catch` block must have user-visible feedback (no silent failures)

## Naming

- Files: `kebab-case.ts` for utilities, `PascalCase.tsx` for React components
- Variables/functions: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Interfaces/Types: `PascalCase`, prefixed with `I` only when disambiguating

## Error Handling

- Every loading state has a corresponding loaded/error state
- Every list/table has an empty state message
- Every button click has visual feedback (loading/disabled/animation)

## Code Hygiene

- No `console.log` in production code
- No `TODO` / `FIXME` / `HACK` in committed code
- No hardcoded file paths or API keys
- No `any` type in TypeScript

## DRY

- Extract to a component/function after 3+ repetitions
- Shared utilities go in `lib/` or `utils/`
- Shared UI patterns go in `components/ui/`

## Testing

- Run `npm run build` before every commit
- Run `npm test` if test suite exists
- Check for residual debug code before PR

## Accessibility

- All interactive elements have hover and focus styles
- All grid layouts degrade gracefully on narrow screens
- All images have alt text
