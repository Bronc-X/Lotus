---
name: gsap
description: 实现或排查项目中明确采用 GSAP 的动画。
metadata:
  source: official-wrapper
  upstream: https://github.com/greensock/gsap-skills
  date_added: "2026-07-03"
---

# GSAP
Use for GSAP work, not every JavaScript animation or frontend change.
Preserve the existing framework, design system, and package manager. Add GSAP or plugins only when the requested animation needs them.
- Use timelines for coordinated sequencing; use ScrollTrigger only for scroll-linked behavior.
- In component frameworks, create animations after mount and clean up with context revert or kill on unmount. Avoid server-side DOM access.
- Use the project's GSAP React integration when present; register only required plugins.
- Favor transform/opacity, avoid repeated layout reads/writes, and respect reduced-motion settings.
- Consult the installed version and official API documentation for uncertain plugin or framework details rather than relying on a fixed API list.
Verify the affected animation, cleanup, and relevant responsive or reduced-motion behavior. Do not redesign unrelated UI.
