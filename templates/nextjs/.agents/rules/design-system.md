# Design System

## Color Palette

- Background: `#FAF9F6` (warm white) / `#FFFFFF`
- Primary border: `#E5E1D8`
- Highlight border (hover): `#D97706`
- Brand / CTA: `#D97706` (amber orange)
- Card background: `#F3F1ED`

## Text Hierarchy

| Level | Color | Usage |
|---|---|---|
| Heading | `#111111` | Page titles, key info |
| Body | `#444444` | Paragraphs, descriptions |
| Secondary | `#666666` | Labels, captions |
| Muted | `#888888` | Placeholder, disabled |

## Buttons

- Primary: `bg-[#D97706] text-white`, hover darkens
- Secondary: `bg-[#F3F1ED] text-[#444] border-[#E5E1D8]`

## Motion

- Engine: Framer Motion
- Allowed: `opacity`, `y`, `x`, `scale` (restrained)
- Spring config: natural feel
- Forbidden: flashy rotations, 3D flips, particle effects

## Cards & Containers

- Never use pure black backgrounds
- Maintain breathing room (generous padding/gap)
- Consistent border radius: `8px` or `12px`
