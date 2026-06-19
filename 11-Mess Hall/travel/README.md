# GenTech Travels — Travel Dashboards

Universal travel dashboard template. Each traveler gets their own folder.

## Structure

```
travel/
├── README.md          ← you are here
├── jordan/            ← Jordan's trips
│   └── philippines-2026.json
└── vanito/            ← Vanito's trips
    └── (future trips)
```

## How It Works

1. **JSON drives everything** — trip data lives in `{name}/{trip-name}.json`
2. **Dashboard renders it** — `travel-dashboard.html` loads JSON and displays visually
3. **Agent updates it** — conversation → JSON updates → dashboard re-renders
4. **Multiple trips per person** — just add more JSON files

## Dashboard

Live: https://protojay4789.github.io/Gaming/travel-dashboard.html

Currently loads from `travel-jordan.json` (repo root). Future: load from vault via agent.

## Data Schema

Each trip JSON has:
- `trip` — name, traveler, dates, status
- `legs[]` — destination segments (PH, Thailand, etc.)
- `flights[]` — route, cost, booking status
- `budget` — total, categories with allocated/spent
- `days[]` — day-by-day itinerary with activities
- `checklist[]` — pre-trip tasks with completion status
- `tips[]` — travel tips for the destination

## Adding a New Trip

1. Copy an existing JSON as template
2. Update all fields
3. Tell the agent "plan my trip to X" and it generates the JSON
4. Dashboard auto-loads on next refresh

---
*GenTech Travels — Dashboard v0.1*
