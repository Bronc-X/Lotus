# Project-Specific Rules

> Universal workflow rules and quality gates are inherited from the global rules file.
> This file contains only project-specific constraints.
> See: https://github.com/Bronc-X/Lotus

## Tech Stack

- Next.js (App Router) + React
- Framer Motion (animation)
- Lucide React (icons)
- localStorage (lightweight persistence)

## Design Language

- For visual or interaction work, use `.agents/rules/design-system.md`.
- Do not load the design guide for backend-only, data-only, or documentation tasks.

## Backend Integration Mode

- Frontend should call your own backend or route handlers, not third-party AI vendors directly
- During scaffolding or early product development, use a backend-owned mock service before wiring a real provider
- Mock responses must keep the same schema and business shape you expect from the eventual real backend
- No direct browser-side calls to OpenAI, Gemini, Notion, or similar external services
