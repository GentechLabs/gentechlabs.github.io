# GenTech Cookbook — Substitution Engine

**Date:** 2026-08-03
**Purpose:** For any Filipino dish, map every ingredient to what's buyable in Cincinnati, OH — the substitute is the point, price is secondary.

---

## The vision (from Jordan)

> *"I want chicken adobo. But that comes from the Philippines. How would I make that here in Cincinnati, Ohio? What ingredients would I get? What are the equivalents?"*

The Cookbook is a **Filipino family recipe tracker** (Christel's dishes). The missing piece was the **ingredient intelligence** layer — knowing the US/Cincinnati equivalent of each Filipino ingredient, and where to buy it. This is NOT a grocery-price problem. Kroger API was only ever a nice-to-have for prices; the substitute knowledge is the core value.

---

## What exists already

- **Cookbook dashboard data:** `Cookbook/cookbook-dashboard-data.json`
  - 6 dishes: Chicken Adobo (new), Beef Caldereta, Chicken Tinola, Pork Sinigang, Fried Eggplant w/ Bagoong, Fried Bread Rolls
  - Each dish carries ingredients, method, family context, and a `substitutions` array (now filled — 19 substitution entries)
- **Shopping list:** `Cookbook/shopping-list.html` (that's Jordan arrival-prep, not grocery)
- **Nanopay variant:** `cookbook-nanopay` project — pay-per-recipe x402 platform (Lepton Agents Hackathon)

## What I built

**Substitution engine:** `Cookbook/substitution-engine.json`
- 15 Filipino ingredients mapped → US/Cincinnati equivalent + where + approx price
- 4 store tiers: **Kroger** (Jordan's local), **Jungle Jim's** (Filipino staples — the key store), **CAM** (Asian grocer), **online** (Amazon/Weee!)
- Philosophy: exact price is secondary; **knowing the substitute is what matters**. Approximate/average prices suffice.

### Example mappings

| Filipino ingredient | US/Cincinnati substitute | Where |
|---|---|---|
| Cane vinegar (sukang maasim) | Rice vinegar (unseasoned) or white vinegar + sugar | Kroger |
| Tamarind (sampalok) | Tamarind paste or Knorr/Mama Sita's sinigang mix | Jungle Jim's / CAM |
| Bagoong alamang | Thai shrimp paste (kapi) — Barrio Fiesta brand | CAM / Jungle Jim's |
| Sili leaves (chili leaves) | Baby spinach or moringa (malunggay) | Kroger / Asian grocer |
| Sayote (chayote) | Chayote IS in US produce | Kroger |
| Maggi Sarap | Maggi liquid, MSG (Accent), or chicken bouillon | Kroger |
| Liver spread (nergubes) | Liver pâté from deli | Kroger |
| Ube | Ube halaya jam or ube extract | Jungle Jim's / CAM |
| Banana ketchup | No good sub — buy UFC brand | Jungle Jim's / CAM / online |

**Key insight:** **Jungle Jim's International Market** (Fairfield / Union Township) is the answer to most Filipino staples in Cincinnati — Mama Sita's, Maggi, bagoong, cane vinegar, ube. That's the concrete "how do I make this here" answer.

---

## Architecture

```
User: "I want chicken adobo in Cincinnati"
  ↓
Recipe match (adobo) → ingredient list
  ↓
Substitution engine → each ingredient → {equivalent, where (Kroger/JJ's/CAM/online), approx $}
  ↓
Shopping list: "Buy at Kroger: chicken, soy sauce, bay leaves, rice vinegar, garlic (~$15)
                Buy at Jungle Jim's: Silver Swan soy sauce (optional authentic)"
```

## Status / Next

- [x] Substitution engine (15 ingredients)
- [x] Filled 5 existing dishes' empty substitution fields
- [x] Added Chicken Adobo (Jordan's example) — 5 subs
- [ ] Wire into the Cookbook dashboard UI (render substitutions per dish)
- [ ] Hook the nanopay pay-per-recipe path to the substitution data
- [ ] Extend ingredient coverage (more dishes: kare-kare, pinakbet, ginataan, halo-halo)
- [ ] Optional: average-price lookup (Walmart/Instacart scrape) — secondary, not needed for v1

## Note (Kroger API)

Kroger developer portal has been unreliable for Jordan (can't log in / create account). We are NOT using anyone else's API key (ToS + security). The Cookbook does NOT need Kroger prices — the substitution knowledge is self-contained. Kroger stays a "nice-to-have price source, try portal again later," never a blocker.
