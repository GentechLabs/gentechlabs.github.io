# 🚚 GenTech Food — Delivery Ordering (dd-cli)

DoorDash CTO Andy Fang just launched `dd-cli` (July 2026) — a CLI for agents
to order DoorDash. GenTech Food connects your food memory to this.

## Flow

1. User says "I'm hungry" or "Order my usual"
2. Agent checks `dishes/` + your food memory
3. Agent asks: cook or deliver?
4. If deliver → query dd-cli for matching restaurants + deals
5. Confirm with user → place order → track

## dd-cli Integration

DoorDash `dd-cli` (limited beta, US/CA macOS):
- `dd search <query>` — find stores/restaurants
- `dd search --deals` — find current deals
- `dd order <store-id> <items>` — place order
- `dd status <order-id>` — track delivery

How we'd use it:
```bash
# User: "Find me something like chicken adobo"
dd search "chicken adobo" --deals

# Returns deals at Filipino restaurants nearby
# Agent picks the best deal based on user history + ratings

# User: "Order it"
dd order <store-id> "Chicken Adobo Combo"
```

## When dd-cli isn't available (waitlist)

Fall back to browser-based ordering:
1. Open DoorDash web
2. Agent navigates the menu
3. User confirms + pays

## Price Competition via WURK

DoorDash takes ~30%. We offset this:
- See `earns.md` — do microtasks to cover delivery fees
- "This $18 order has $5.40 in fees. Do 3 WURK microtasks = free delivery"

## Kroger Alternative

For groceries instead of delivery:
- "Chicken adobo at Kroger: $14 total, pickup in 2 hours — no delivery fee"
- Compare: $18 delivered vs $14 pickup vs free with WURK tasks
