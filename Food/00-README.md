# 🍽️ GenTech Food — Agentic Food Concierge

Your personal food memory + ordering concierge. Remembers what you ate, 
finds ingredients at your store, and orders delivery — all through your agent.

## System

```
Food/
├── README.md              # This file
├── dishes/                # Your food memory (one JSON per dish)
│   ├── chicken-adobo.json
│   └── ...
├── stores.json            # Local stores + inventory knowledge
├── ordering.md            # dd-cli + delivery integration
└── earns.md               # WURK.fun EarnFi work offset
```

## Capabilities

| Feature | What it does | Source |
|---------|-------------|--------|
| **Food Memory** | Save dishes from travel, describe or photo | GenTech vault |
| **Local Ingredients** | Find what you need at YOUR Kroger | Kroger API |
| **Order Delivery** | Order from favorite restaurants via agent | dd-cli |
| **Work Offsets** | Earn delivery fees by doing microtasks | WURK.fun / EarnFi |
| **Coupon Radar** | Find deals + promos for what you want | Kroger API + scrape |

## Agent Prompt

When the user says they want food, the agent should:
1. Check `dishes/` for their favorites
2. If they want to cook → check `stores.json` → Kroger API for pricing + deals
3. If they want delivery → check `ordering.md` for dd-cli flow
4. If they want to offset cost → check `earns.md` for WURK microtasks
5. Cross-reference with their food memory for recommendations
