# Project-Specific Rules

> Universal workflow rules and quality gates are inherited from the global rules file.
> This file contains only project-specific constraints.
> See: https://github.com/Bronc-X/Lotus

## Tech Stack

- Vite + React + TypeScript
- TailwindCSS (Styling)
- Zustand (State management)

## Design Language

- Refer to `.agents/rules/design-system.md` for exact color values and constraints.
- Avoid raw CSS unless necessary; use utility classes.

## Development Constraints

- Build commands: `npm run dev`, `npm run build`
- For code changes, run the narrowest relevant check; include `npm run build` when compilation or bundling may be affected.
