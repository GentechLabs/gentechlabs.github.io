# Dashboard Template Spec v1.0

**Date:** Jun 10, 2026
**Status:** Active spec

## Overview
A dashboard template is a JSON file that defines:
- **meta** — title, subtitle, data source, refresh interval
- **theme** — colors, fonts, layout
- **sections** — ordered list of dashboard sections
- **tabs** — optional tab navigation
- **footer** — brand text, version, timestamp

## Template Schema

```json
{
  "meta": {
    "title": "Dashboard Title",
    "subtitle": "Optional subtitle",
    "dataUrl": "path/to/data.json",
    "refreshMs": 30000,
    "version": "v1.0",
    "brand": "GENTECH",
    "badge": "Optional badge text"
  },
  "theme": {
    "mode": "dark | light",
    "colors": {
      "--bg": "#0a0a0f",
      "--panel-bg": "#12121a",
      "--panel-border": "#1e1e2e",
      "--text": "#d4d4d4",
      "--text-dim": "#6b6b7b",
      "--gold": "#c9a84c",
      "--accent": "#7eb8ff",
      "--danger": "#ff4444",
      "--success": "#44ff88",
      "--radius": "12px",
      "--header-gradient": "linear-gradient(...)"
    },
    "fonts": {
      "heading": "Cinzel, serif",
      "body": "Crimson Text, serif"
    },
    "container": {
      "maxWidth": "1200px"
    }
  },
  "sections": [
    {
      "id": "section-id",
      "title": "Section Title",
      "icon": "📊",
      "type": "stats | progress | grid | cards | timeline | checklist | table | custom",
      "visible": true,
      "dataSource": "dot.path.to.data",
      "layout": {},
      "cardTemplate": {},
      "progressConfig": {},
      "checklistConfig": {},
      "timelineConfig": {},
      "animation": {}
    }
  ],
  "tabs": [
    {
      "id": "tab-id",
      "label": "Tab Label",
      "icon": "🎮",
      "sections": ["section-id-1", "section-id-2"]
    }
  ],
  "footer": {
    "brand": "GENTECH",
    "version": "v1.0",
    "showTimestamp": true
  }
}
```

## Section Types

### stats
Renders a grid of stat boxes from a data object.
```json
{
  "type": "stats",
  "dataSource": "portfolio",
  "cardTemplate": {
    "fields": [
      { "key": "totalValue", "label": "Total Value", "format": "money" },
      { "key": "change24h", "label": "24h Change", "format": "percent" }
    ]
  }
}
```

### progress
Renders animated progress bars.
```json
{
  "type": "progress",
  "dataSource": "progress",
  "progressConfig": {
    "items": [
      { "label": "Campaign", "valueKey": "campaign", "color": "gold" },
      { "label": "Build", "valueKey": "build", "gradient": "linear-gradient(90deg, #c9a84c, #7eb8ff)" }
    ]
  }
}
```

### grid
Renders items in a responsive grid.
```json
{
  "type": "grid",
  "dataSource": "skills",
  "layout": { "gridMinWidth": "280px" },
  "cardTemplate": {
    "className": "skill-card",
    "fields": [
      { "key": "name", "className": "skill-name" },
      { "key": "type", "className": "skill-type" }
    ]
  }
}
```

### cards
Renders items as horizontal scrollable cards.
```json
{
  "type": "cards",
  "dataSource": "trip.legs",
  "layout": { "scrollX": true, "scrollSnap": true },
  "cardTemplate": {
    "className": "leg-card",
    "fields": [
      { "key": "destination", "className": "leg-dest" },
      { "key": "arrive", "format": "date", "label": "Arrive" }
    ]
  }
}
```

### timeline
Renders a vertical timeline with today marker.
```json
{
  "type": "timeline",
  "dataSource": "trip.days",
  "timelineConfig": {
    "dateKey": "date",
    "titleKey": "title",
    "typeKey": "type",
    "todayMarker": true,
    "scrollToToday": true
  }
}
```

### checklist
Renders interactive checkboxes with localStorage persistence.
```json
{
  "type": "checklist",
  "dataSource": "checklist",
  "checklistConfig": {
    "storageKey": "my-checklist-state",
    "groupBy": "category",
    "showProgress": true
  }
}
```

### table
Renders a data table.
```json
{
  "type": "table",
  "dataSource": "transactions",
  "cardTemplate": {
    "fields": [
      { "key": "date", "label": "Date", "format": "date" },
      { "key": "type", "label": "Type" },
      { "key": "amount", "label": "Amount", "format": "money" }
    ]
  }
}
```

### custom
For sections that need custom rendering. Pass a `render` function or `html` string.

## Field Formats
- `text` — plain text (default)
- `money` — `$1,234`
- `percent` — `45%`
- `date` — `Jun 10, 2026`
- `badge` — `<span class="badge">value</span>`
- `tags` — array of `<span class="tag">item</span>`
