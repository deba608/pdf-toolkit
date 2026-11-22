---
version: alpha
name: vite.dev
description: Vite's next-generation frontend tooling design language — an ultra-fast, modern developer tool system built on a deep dark charcoal and obsidian canvas, with a signature electric indigo brand CTA (#646cff), vibrant purple-to-cyan gradient accents (#bd34fe to #41d1ff), crisp translucent borders, and clean Inter typography.

colors:
  primary: "#646cff"
  primary-hover: "#747bff"
  primary-active: "#535bf2"
  primary-soft: "rgba(100, 108, 255, 0.14)"
  accent-purple: "#bd34fe"
  accent-cyan: "#41d1ff"
  gradient-hero: "linear-gradient(120deg, #bd34fe 30%, #41d1ff)"
  canvas: "#1b1b1f"
  canvas-alt: "#161618"
  canvas-elv: "#202127"
  canvas-soft: "#252529"
  border: "rgba(82, 82, 89, 0.48)"
  border-subtle: "rgba(82, 82, 89, 0.28)"
  border-soft: "#2e2e32"
  text-1: "rgba(255, 255, 245, 0.86)"
  text-2: "rgba(235, 235, 245, 0.60)"
  text-3: "rgba(235, 235, 245, 0.38)"
  on-primary: "#ffffff"
  on-dark: "#ffffff"
  danger: "#f43f5e"
  danger-bg: "rgba(244, 63, 94, 0.12)"
  success: "#10b981"
  success-bg: "rgba(16, 185, 129, 0.12)"
  warning: "#f59e0b"
  warning-bg: "rgba(245, 158, 11, 0.12)"

typography:
  display-xl:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: 48px
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: -1.2px
  display-lg:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: 28px
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: -0.5px
  heading-lg:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: 20px
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: -0.2px
  heading-md:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: 16px
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: -0.1px
  body-md:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0
  button-md:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: 13px
    fontWeight: 500
    lineHeight: 1.0
    letterSpacing: 0
  caption:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.45
    letterSpacing: 0
  code:
    fontFamily: "ui-monospace, 'JetBrains Mono', 'Fira Code', Menlo, Monaco, Consolas, monospace"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0

rounded:
  xs: 4px
  sm: 6px
  md: 8px
  lg: 12px
  xl: 16px
  full: 9999px

spacing:
  xxs: 2px
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  xxl: 32px

components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button-md}"
    rounded: "{rounded.md}"
    padding: 8px 18px
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-secondary:
    backgroundColor: "{colors.canvas-soft}"
    textColor: "{colors.text-1}"
    border: "1px solid {colors.border}"
    typography: "{typography.button-md}"
    rounded: "{rounded.md}"
    padding: 8px 16px
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.text-2}"
    rounded: "{rounded.md}"
  text-input:
    backgroundColor: "{colors.canvas-elv}"
    textColor: "{colors.text-1}"
    border: "1px solid {colors.border-subtle}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: 8px 12px
  card-feature:
    backgroundColor: "{colors.canvas-elv}"
    border: "1px solid {colors.border-subtle}"
    rounded: "{rounded.lg}"
    padding: 24px
  sidebar-nav:
    backgroundColor: "{colors.canvas-alt}"
    textColor: "{colors.text-2}"
    borderRight: "1px solid {colors.border-subtle}"
---

# Vite Design Language (vite.dev)

## Overview
Vite's design language is built for blazing speed and developer delight. Grounded in a sleek dark theme aesthetic, the interface balances deep charcoal backgrounds with electric violet/indigo branding (`#646cff`) and a vibrant multi-stop gradient (`#bd34fe` purple to `#41d1ff` cyan). 

Key visual attributes:
- **Dark Charcoal Foundations:** Surfaces layer from deep obsidian (`#161618`) to workspace charcoal (`#1b1b1f`) and elevated container cards (`#202127`).
- **Signature Vite Gradient:** Diagonal 120deg gradient transitioning from electric purple (`#bd34fe`) to bright cyan (`#41d1ff`) used in brand marks and highlight accents.
- **Electric Indigo CTA:** Primary actions shine in `#646cff` with smooth hover states to `#747bff`.
- **Translucent Hairlines:** Fine container borders (`rgba(82, 82, 89, 0.48)`) delineate components with minimal visual noise.
- **Refined Typography:** Modern Inter sans typography with deliberate weight contrasts and monospace code touches.

## Palette Reference
- `canvas`: `#1b1b1f` (Primary window surface)
- `canvas-alt`: `#161618` (Sidebar, toolbars, and preview workbench)
- `canvas-elv`: `#202127` (Card panels and modal containers)
- `canvas-soft`: `#252529` (Inputs, secondary buttons, and chips)
- `primary`: `#646cff` (Vite brand CTA)
- `primary-hover`: `#747bff`
- `primary-active`: `#535bf2`
- `primary-soft`: `rgba(100, 108, 255, 0.14)` (Tints, selection highlights, active nav items)
- `accent-purple`: `#bd34fe` (Vite lightning purple)
- `accent-cyan`: `#41d1ff` (Vite lightning cyan)
- `text-1`: `rgba(255, 255, 245, 0.86)` (High-emphasis text)
- `text-2`: `rgba(235, 235, 245, 0.60)` (Secondary text & subtitles)
- `text-3`: `rgba(235, 235, 245, 0.38)` (Placeholders & hints)
- `border`: `rgba(82, 82, 89, 0.48)` (Component borders)
- `border-subtle`: `rgba(82, 82, 89, 0.28)` (Separators)
