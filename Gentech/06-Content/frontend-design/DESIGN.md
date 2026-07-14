---
version: alpha
name: GenTech Multi-Chain Agent Vault
description: >
  A unified agent vault interface that morphs its visual identity per chain.
  Solana feels like electric neon over deep ocean. Avalanche feels like
  ember heat over volcanic rock. Same components, different soul.
chains:
  solana:
    name: Solana
    icon: solana-logo
    accentGradient: "linear-gradient(135deg, #8B5CF6 0%, #06B6D4 100%)"
  avalanche:
    name: Avalanche
    icon: avalanche-logo
    accentGradient: "linear-gradient(135deg, #E84142 0%, #991B1B 100%)"
colors:
  # ── Base neutrals (shared) ──
  ink: "#0A0B0D"
  charcoal: "#13151A"
  slate: "#1E212B"
  mist: "#94A3B8"
  frost: "#E2E8F0"
  snow: "#F8FAFC"

  # ── Solana palette ──
  solana-bg: "#05081A"
  solana-surface: "#0B1029"
  solana-surface-elevated: "#111A3E"
  solana-primary: "#8B5CF6"
  solana-secondary: "#06B6D4"
  solana-accent: "#A855F7"
  solana-glow: "#3B82F6"

  # ── Avalanche palette ──
  avax-bg: "#080808"
  avax-surface: "#141414"
  avax-surface-elevated: "#1F1F1F"
  avax-primary: "#E84142"
  avax-secondary: "#B91C1C"
  avax-accent: "#F87171"
  avax-glow: "#EF4444"

typography:
  display:
    fontFamily: "Space Grotesk"
    fontSize: 3.5rem
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.03em"
  h1:
    fontFamily: "Space Grotesk"
    fontSize: 2.5rem
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  h2:
    fontFamily: "Space Grotesk"
    fontSize: 1.75rem
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  body-lg:
    fontFamily: "Inter"
    fontSize: 1.125rem
    fontWeight: 400
    lineHeight: 1.6
  body-md:
    fontFamily: "Inter"
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Inter"
    fontSize: 0.75rem
    fontWeight: 600
    letterSpacing: "0.08em"
    textTransform: uppercase

rounded:
  none: 0px
  sm: 6px
  md: 12px
  lg: 16px
  xl: 24px
  full: 9999px

spacing:
  0: 0px
  1: 4px
  2: 8px
  3: 12px
  4: 16px
  5: 24px
  6: 32px
  7: 48px
  8: 64px
  9: 96px

shadows:
  solana-glow-sm: "0 0 12px rgba(139, 92, 246, 0.25)"
  solana-glow-md: "0 0 24px rgba(139, 92, 246, 0.35)"
  solana-glow-lg: "0 0 48px rgba(59, 130, 246, 0.3)"
  avax-glow-sm: "0 0 12px rgba(232, 65, 66, 0.25)"
  avax-glow-md: "0 0 24px rgba(232, 65, 66, 0.35)"
  avax-glow-lg: "0 0 48px rgba(239, 68, 68, 0.3)"

components:
  button-primary:
    backgroundColor: "{colors.solana-primary}"
    textColor: "{colors.snow}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "14px 28px"
  button-primary-hover:
    backgroundColor: "{colors.solana-accent}"
    shadow: "{shadows.solana-glow-md}"
  button-secondary:
    backgroundColor: transparent
    textColor: "{colors.frost}"
    border: "1px solid {colors.mist}"
    rounded: "{rounded.md}"
    padding: "14px 28px"
  button-secondary-hover:
    borderColor: "{colors.solana-primary}"
    textColor: "{colors.solana-primary}"
  card:
    backgroundColor: "{colors.solana-surface}"
    textColor: "{colors.frost}"
    rounded: "{rounded.lg}"
    padding: "24px"
    border: "1px solid rgba(139, 92, 246, 0.08)"
  card-elevated:
    backgroundColor: "{colors.solana-surface-elevated}"
    shadow: "{shadows.solana-glow-sm}"
    rounded: "{rounded.lg}"
    padding: "24px"
  input:
    backgroundColor: "{colors.solana-surface}"
    textColor: "{colors.frost}"
    border: "1px solid {colors.slate}"
    rounded: "{rounded.md}"
    padding: "12px 16px"
  input-focus:
    borderColor: "{colors.solana-primary}"
    shadow: "{shadows.solana-glow-sm}"
  badge:
    backgroundColor: "rgba(139, 92, 246, 0.12)"
    textColor: "{colors.solana-primary}"
    rounded: "{rounded.full}"
    padding: "4px 12px"
    typography: "{typography.label}"
---

## Overview

GenTech Agent Vault is a cross-chain interface for autonomous agent
infrastructure. The UI adapts its entire color temperature and glow
signature based on the active chain — not just an accent swap, but a
complete atmospheric shift.

**Solana** evokes deep-ocean bioluminescence: midnight blues, electric
violets, and cyan edge lighting. The interface feels like a control deck
aboard a submersible exploring a neon reef.

**Avalanche** evokes volcanic forge heat: obsidian blacks, ember reds,
and molten highlights. The interface feels like operating a smelting
console at the edge of a lava flow.

Both modes share identical layout, spacing, and component structure.
Only color, glow, and gradient tokens change. This preserves muscle
memory while giving each chain a native emotional identity.

## Colors

### Shared Neutrals

- **Ink (#0A0B0D):** Deepest background layer. Used behind gradients and
  on loading states.
- **Charcoal (#13151A):** Secondary deep background for modals and drawers.
- **Slate (#1E212B):** Borders, dividers, inactive track backgrounds.
- **Mist (#94A3B8):** Secondary text, placeholders, disabled states.
- **Frost (#E2E8F0):** Primary text on dark surfaces.
- **Snow (#F8FAFC):** Headlines and high-emphasis text.

### Solana Palette

- **solana-bg (#05081A):** Page background. Almost black with a navy tint.
- **solana-surface (#0B1029):** Card and panel backgrounds.
- **solana-surface-elevated (#111A3E):** Elevated cards, dropdowns, tooltips.
- **solana-primary (#8B5CF6):** Main action color — buttons, active nav,
  progress indicators.
- **solana-secondary (#06B6D4):** Secondary action, links, live status dots.
- **solana-accent (#A855F7):** Hover states, selected tabs, highlights.
- **solana-glow (#3B82F6):** Glow shadows and ambient lighting effects.

### Avalanche Palette

- **avax-bg (#080808):** Page background. True neutral black.
- **avax-surface (#141414):** Card and panel backgrounds.
- **avax-surface-elevated (#1F1F1F):** Elevated cards, dropdowns, tooltips.
- **avax-primary (#E84142):** Main action color — matches Avalanche brand red.
- **avax-secondary (#B91C1C):** Secondary action, darker red for contrast.
- **avax-accent (#F87171):** Hover states, selected tabs, highlights.
- **avax-glow (#EF4444):** Glow shadows and ambient lighting effects.

## Typography

**Space Grotesk** for all display and heading text. Geometric, slightly
technical, modern. Used at tight letter-spacing for headlines.

**Inter** for all body, labels, and UI chrome. Highly legible at small
sizes, neutral personality that does not compete with the color story.

Font loading: Google Fonts via `@import` or `<link>`. Weights needed:
Inter 400, 500, 600; Space Grotesk 600, 700.

## Layout

8-column grid on desktop, 4-column on tablet, 2-column on mobile.
Max content width: 1280px.

Spacing scale is 4px base with exponential-ish growth (4, 8, 12, 16,
24, 32, 48, 64, 96). This gives enough granularity for dense agent
 dashboards without becoming arbitrary.

Cards and panels use generous internal padding (24px) to breathe on
dark backgrounds. Tight packing feels claustrophobic with deep colors.

## Elevation & Depth

Elevation is expressed through **glow**, not shadow. On dark backgrounds,
blue/purple or red glows radiating from active elements create depth
more effectively than black drop-shadows.

- sm: Subtle halo around focused inputs and hovered buttons.
- md: Radiant glow around primary CTAs and active cards.
- lg: Ambient background gradients and hero section lighting.

## Shapes

Corners are moderately rounded (12–16px) for cards and panels. Buttons
use 12px. Badges and pills use full rounding. Nothing is perfectly
square — the slight softness counters the harshness of pure black
backgrounds.

## Components

### Buttons

- `button-primary`: Filled with chain primary color. High emphasis. One
  per view maximum.
- `button-secondary`: Outlined with mist border. For secondary actions
  like "Cancel" or "View Details".

### Cards

- `card`: Default surface. Slight purple/red border tint at 8% opacity.
- `card-elevated`: For featured agents or highlighted vaults. Adds glow
  shadow.

### Inputs

- `input`: Dark surface with slate border. On focus, border transitions
  to chain primary + glow shadow.

### Badges

- `badge`: Pill-shaped labels for agent types, chain tags, status.
  Background is primary color at 12% opacity with solid primary text.

## Do's and Don'ts

- **Do** switch the entire CSS custom property set when the user changes
  chains. The swap should feel instant and total.
- **Do** use `Space Grotesk` sparingly — only headlines and nav. Overuse
  makes the UI feel shouty.
- **Do** animate color transitions with `transition: color 0.2s ease,
  background-color 0.2s ease, box-shadow 0.3s ease`.
- **Don't** mix Solana purples with Avalanche reds in the same view.
  The theme must be pure per chain.
- **Don't** use pure white (#FFFFFF) text. Snow (#F8FAFC) is bright
  enough and reduces eye strain.
- **Don't** add drop-shadows behind cards. Use glow or subtle borders
  instead — black shadows vanish on black backgrounds.
