# mapcn — Interactive Map Components for Travel & Dashboards

**Date evaluated:** 2026-05-03
**Source:** https://github.com/AnmolSaini16/mapcn
**License:** MIT (per repo footer)
**Tech:** React + TypeScript (likely, based on structure)

## What It Is

A zero-config React component library for building beautiful interactive maps. Provides pre-built UI blocks: markers, popups, layers, controls, etc. Works with any map provider (Mapbox, Google Maps, OpenStreetMap).

## Why It Matters to GenTech

### Travel Agent Vision
Jordan's idea: "Agents don't just book — they **show** you the destination." Instead of pinch-to-zoom Street View, the agent presents an interactive, curated view.

**Integration points:**
- Hotel neighborhood walkthrough (pre-built 3D/pano layer)
- Restaurant/attraction markers with agent annotations
- Route previews ("your airport transfer will pass through...")

### Strategy Dashboards
Visualize:
- LP positions by geography (Uniswap v4 pools across chains)
- Market data by region
- Agent operational coverage map

## Fit Assessment

| Criterion | Assessment |
|-----------|------------|
| Direct utility now | Medium — travel agent is still at idea stage |
| Hackathon boost | High — adds visual "wow" factor to any demo with location data |
| Cost | Free + MIT license |
| Dependencies | Requires map provider API key (Mapbox ~$0.50/1000 loads, or free OSM) |
| Maintenance | Actively maintained (73 commits, recent feature additions) |
| Complexity | Low — plug-and-play React components |

## Integration Path

1. **Add to vault:** `03-Projects/Integrations/mapcn/` with component examples
2. **Prototype:** Build a "Travel Preview" component that shows:
   - Hotel location
   - Nearby attractions (pre-set POIs)
   - Agent voice-over button ("Tell me about this area")
3. **Consume in frontend:** Integrate into travel agent dashboard (Desmond's domain)
4. **Provider choice:** Start with OpenStreetMap (free) → upgrade to Mapbox if we need satellite/3D

## Cost Considerations

- Mapbox free tier: 50,000 map loads/month → enough for prototype
- If we scale, budget ~$20–50/mo for active usage
- Alternative: MapLibre GL (open-source Mapbox clone) + OSM tiles = completely free

## Verdict

🔧 **Integrate** — Add to component library, build travel preview POC.  
Low cost, high visual impact, aligns with travel + dashboard projects.

## Next Steps

- Desmond: Create `03-Projects/Integrations/mapcn/` with README and sample component
- DMob: Research OSM tile hosting (self-host vs third-party)
- Yoyo: Wire into Hermes skill for "show me around <location>" command
