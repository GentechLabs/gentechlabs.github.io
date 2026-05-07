# projects.json — Schema Reference
**Used by:** Jordan Portfolio, static-dashboard-generator skill  
**Source:** `03-Projects/jordan-portfolio/projects.json`

## Top-level Structure
```json
{
  "projects": [ /* array of project objects */ ],
  "generated": "2026-05-04",
  "count": 7
}
```

## Project Object Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Machine ID (kebab-case, e.g., `agent-escrow-solana`) |
| `title` | string | yes | Display name (e.g., `AgentEscrow`) |
| `description` | string | yes | One-sentence summary |
| `tech` | string[] | yes | Array of tech/tag strings (e.g., `["Solana","Rust"]`) |
| `status` | string | yes | One of: `live`, `building`, `research`, `audit` |
| `deadline` | string \| null | no | ISO date string (`YYYY-MM-DD`) or `null` |
| `timeline` | string | yes | Human-readable timeframe (e.g., `May 2026`, `Apr 2026`) |
| `highlight` | boolean | no | `true` to feature; `false` otherwise |
| `vault_path` | string | yes | Relative vault path (e.g., `03-Projects/agent-escrow-solana`) |

## Status Meanings (Categorization)
- `live` → **NOW** category — shipped/in production
- `building` + `deadline` present → **NOW** (hackathon with deadline)
- `building` + no `deadline` → **WIP** (in progress, no firm date)
- `research` → **WIP** (early stage / research)
- `audit` → **NOW** (if shipping) or **WIP** (if in progress)

## Example Entry
```json
{
  "id": "agent-escrow-solana",
  "title": "AgentEscrow",
  "description": "AgentEscrow — GenTech project",
  "tech": ["Solana", "Anchor", "Rust"],
  "status": "building",
  "deadline": "2026-05-11",
  "timeline": "May 2026",
  "highlight": true,
  "vault_path": "03-Projects/agent-escrow-solana"
}
```

## Generator Script Pattern
The `generate.py` script replaces the `<script id="project-data" type="application/json">...</script>` block in `index.html` with fresh JSON. Keep JSON compact or indented as needed; HTML escaping not required for `type="application/json"`.
