# Project-Specific Rules

> Universal workflow rules and quality gates are inherited from the global rules file.
> This file contains only project-specific constraints.
> See: https://github.com/Bronc-X/AGENTRULES

## Tech Stack

- Next.js (App Router) + React
- Framer Motion (animation)
- Lucide React (icons)
- localStorage (lightweight persistence)

## Design Language

- Background: warm white (`#FAF9F6`) or pure white
- Primary border: `#E5E1D8`, hover: `#D97706`
- Text hierarchy: `#111` > `#444` > `#666` > `#888`
- Brand highlight / CTA: `#D97706` (amber orange)
- Secondary button: `bg-[#F3F1ED] text-[#444] border-[#E5E1D8]`
- Cards: `bg-[#F3F1ED]` or white, never pure black
- Animation: only `opacity`/`y`/`x` + spring via Framer Motion

## AI Engine

- All AI interactions go through a Mock engine
- No external API calls (OpenAI/Gemini/Notion etc.)
- Mock engine returns high-fidelity business data
