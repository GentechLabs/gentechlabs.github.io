# Gentech Dashboard — Universal Engine (Rebrand from Pals)

**Date:** Jun 10, 2026
**Status:** Active brainstorm
**Owner:** Jordan

## The Insight
Gentech Pals was originally gaming companions (POE2 builds, character dashboards). But the real product is the **universal dashboard engine** — same pattern works for gaming, travel, DeFi, education, health, social, business.

**Pals = feature. Dashboard = product.**

## Architecture
- **Template = JSON + Theme + Components**
- JSON defines data structure
- Theme defines look (colors, gradients, fonts)
- Components define what you can render (charts, lists, grids, timelines)
- Renderer is shared across all templates

## Core Pattern (every dashboard)
1. Data In (API, file, manual entry)
2. Process (calculate, aggregate, categorize)
3. Render (theme + components)
4. Persist (save state, vault sync)

## Templates (easy → difficult)
1. **Gaming (POE2)** ✅ — character builds, passive tree, gear
2. **Travel** ✅ — itinerary, budget, packing, tips
3. **DeFi** — portfolio, yields, LP tracking, gas
4. **Education** — course progress, certs, skill trees
5. **Health/Fitness** — workouts, nutrition, sleep
6. **Social Analytics** — followers, engagement, content
7. **Home Automation** — devices, energy, security
8. **Business Metrics** — revenue, expenses, customers

## Revenue Model
- Agent Pass ($15/mo) — unlimited templates, real-time data, custom themes
- Free tier — 1 template, 3 AI updates/day
- Template marketplace — community-created templates
- x402 pay-per-render — agents pay per dashboard load

## AAE Integration
- Dashboard Registry as ERC-8183 skills
- Agents discover and load templates
- Renderer spec (standard JSON schema)
- Templates become marketplace items

## Next Steps
- Extract renderer from existing dashboards
- Define template spec (JSON schema)
- Build DeFi template (prove pattern works for finance)
- Create component library (charts, lists, grids, timelines)
- Dashboard Registry (ERC-8183 skills)
