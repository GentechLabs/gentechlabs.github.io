---
name: interactive-travel-visualization
description: "Build agent-curated interactive travel maps using mapcn components and vault-sourced POI data."
intent: Create beautiful, story-driven travel visualizations (not just raw maps) where agents pre-select interesting spots and narrate them
category: creative
primary_tools:
  - mapcn
  - obsidian
secondary_tools:
  - google-workspace (optional photos)
critical_dependencies: []
common_patterns:
  - vault-to-map
  - agent-curated-pois
  - layered-routes
fragments: []
setup_needed: false
---

# Interactive Travel Visualization

## Purpose

Transform travel research (vault notes) into **interactive, agent-narrated maps** that are more engaging than Google Maps/Street View. Each map point is curated by agents with context, photos, and recommendations — not just raw geotags.

**Differentiators from Google Maps:**
- Pre-filtered highlights only (no clutter)
- Agent commentary embedded in popups
- Curated routes designed for experience, not just navigation
- Day-by-day layer toggles
- Sentiment heatmaps (loved vs meh spots)
- Connected to vault — click a pin, read full travel note

---

## Stack

- **Map engine:** `mapcn` (React components on top of MapLibre GL / Leaflet)
- **Data source:** Obsidian vault markdown files (`04-Entertainment/Travel/`)
- **Frontend:** Next.js (or static HTML if quick demo)
- **Tiles:** OpenStreetMap (free) or MapTiler (styled)
- **Hosting:** Vercel/Netlify (free tier for demo)

---

## Data Model

Each vault travel note becomes a map **POI (Point of Interest)**:

```markdown
---
location: Angeles City, Pampanga
coords: [15.0536, 120.5983]
tags: [food, street food, local]
rating: 5
photos: [img1.jpg, img2.jpg]
agent_notes: |
  "Best halo-halo in town. Go before 11 AM or they sell out.
  2-min walk from Robinsons mall. Cash only."
visited: 2026-09-15
---
Full travel narrative...
```

**Automated extraction script:**
```python
import frontmatter
import yaml

note = frontmatter.load("Travel/Philippines-Angeles.md")
poi = {
  "title": note.metadata.get("location"),
  "coords": note.metadata.get("coords"),
  "tags": note.metadata.get("tags", []),
  "rating": note.metadata.get("rating", 3),
  "agent_notes": note.metadata.get("agent_notes", ""),
  "link": f"gentech://travel/{note_path}"
}
```

---

## Component Structure (mapcn)

```jsx
import { Map, MapMarker, MapPopup, MapArc } from '@mapcn/react'

<TravelMap>
  <Map center={[lat,lng]} zoom={13}>
    {/* Day 1 route */}
    <MapArc points={day1_coords} color="#ff6b6b" />
    {day1_pois.map(poi => (
      <MapMarker coords={poi.coords} color={ratingColor(poi.rating)}>
        <MapPopup>
          <h3>{poi.title}</h3>
          <p>{poi.agent_notes}</p>
          <img src={poi.photos[0]} />
          <Link to={poi.link}>Full vault note →</Link>
        </MapPopup>
      </MapMarker>
    ))}
  </Map>
  <LayerToggle layers={['food','sights','hotels']} />
  <DayFilter days={[1,2,3,4]} />
</TravelMap>
```

---

## Agent Curation Layers

Agents add value by pre-selecting and annotating:

| Layer | Agent | What they add |
|---|---|---|
| **Food** | Desmond | "Must-try dishes, vibe rating, photo ops" |
| **Tech hubs** | DMOB | "Co-working spots, internet speed tests" |
| **DeFi hotspots** | YoYo | "Cafe with crypto meetups, local exchange liquidity" |
| **Hidden gems** | Gentech | "Local secrets,Instagrammable angles" |

---

## Deployment Pattern

1. **Vault as source of truth** — all travel notes live in Obsidian
2. **GitHub Action** — on note update, regenerate map data JSON
3. **Static site deploy** — Next.js reads `map-data.json` → renders map
4. **Share link** — `gentech.travel/map/philippines-2026`

**Zero-maintenance:** Once set up, new vault notes automatically appear on map.

---

## Quick Start (Day 1)

1. Create `04-Entertainment/Travel/Philippines-Draft.md` with frontmatter coords
2. Clone `gentech-travel-viz` repo (template provided in `templates/`)
3. Add 5 sample POIs from vault
4. Run `npm install && npm run dev`
5. Share localhost URL in HQ

**Deliverable by EOD:** `06-Content/Travel/philippines-map-demo.mp4` screen recording of interactive map.

---

## Next Steps

- Add real-time updates via webhook when vault changes (Obsidian plugin)
- Add 360° Street View embedding at each pin (agent-curated angles only)
- Add conversational agent overlay: "Hey Gentech, show me the best food spots" → map filters automatically

---

*Related:* `mapcn` (UI components), `obsidian` (data source), `hackathon-submission-package` (for travel-tech hackathons)*