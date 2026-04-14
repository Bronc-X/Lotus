# Project-Specific Rules

> Universal workflow rules are inherited from the global rules file.
> This file contains constraints for pure HTML/JS projects.

## Tech Stack

- Core: HTML5, CSS3, ES6+ JavaScript
- No build tools, no bundlers. Raw files only.
- Libraries loaded via CDN.

## Development Constraints

- Ensure all JS is contained within `main.js` or specific modules, not inline.
- Use CSS Variables (`:root`) for color theming.
- Must remain operable locally via plain `file://` protocol or simple `python -m http.server`.
