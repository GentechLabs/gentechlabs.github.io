# GenTech Cookbook — Architecture

> GenTech Labs · June 2026
> Layer 1 of the Agent Pass Suite

---

## Vision

**Pinterest for food with persistent memory and agent-powered ingredient adaptation.**

Solve the universal problem: people want to cook new dishes but don't know how with what they have. The Cookbook remembers what you've made, adapts recipes to your local ingredients, and connects you with a global community of home cooks.

**The Christel Problem (origin story):**
She's in the Philippines, wants to cook for Jordan in Cincinnati. Filipino grocery stores don't carry the same ingredients. The Cookbook adapts the recipe to local availability while preserving the flavor profile.

---

## Core Features

### 1. Recipe Generation (Agent-Powered)
- User describes what they want: "baked potato with toppings"
- Agent generates recipe based on available ingredients
- Suggests substitutions for unavailable items
- Considers dietary restrictions, cooking skill level, kitchen equipment

### 2. Ingredient Adaptation Engine
- User selects their region/location
- Agent maps recipe ingredients to locally available alternatives
- Preserves flavor profiles across substitutions
- Tracks which substitutions worked (learns from feedback)

### 3. Persistent Memory
- Remembers every dish made
- "What did I make last week?" → pulls it up
- "How did the sweet potato substitution work?" → remembers feedback
- Suggests improvements based on history
- Never forgets a recipe, even if user cancels (archived, not deleted)

### 4. Social Discovery
- Share your creations (photo + recipe)
- Browse what others are making in your region
- "People near you are making..."
- Rate, comment, remix variations
- Follow cooks with similar taste

### 5. Flavor Graph
- Agent learns flavor combinations that work
- "People who like X also enjoy Y"
- Suggests new dishes based on taste profile
- Cross-cultural flavor bridges ("This Filipino dish is similar to this Mexican dish")

### 6. Meal Planning (Premium Feature)
- Weekly/monthly meal plans based on preferences
- Auto-generate grocery lists
- Budget-aware suggestions
- Nutritional tracking (optional)

---

## Architecture Layers

```
┌─────────────────────────────────────────────────┐
│                   UI Layer                       │
│  React Native (iOS/Android) + Web (Next.js)     │
│  Pinterest-style grid, recipe cards, memory feed│
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│                API Gateway                       │
│  REST/GraphQL, Auth, Rate Limiting               │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│              Agent Layer (Core)                  │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐              │
│  │  Recipe Gen  │  │ Ingredient  │              │
│  │   Agent      │  │  Adapter    │              │
│  └──────┬──────┘  └──────┬──────┘              │
│         │                │                      │
│  ┌──────▼────────────────▼──────┐              │
│  │      Flavor Graph Engine     │              │
│  │  (learns from all users)     │              │
│  └──────────────┬───────────────┘              │
│                 │                               │
│  ┌──────────────▼───────────────┐              │
│  │      Memory Layer            │              │
│  │  (per-user persistent memory)│              │
│  └──────────────┬───────────────┘              │
└─────────────────┼──────────────────────────────┘
                  │
┌─────────────────▼──────────────────────────────┐
│              Data Layer                         │
│                                                 │
│  PostgreSQL — user data, recipes, memory        │
│  Redis — sessions, rate limiting, caching       │
│  S3 — recipe images, user photos                │
│  Vector DB — flavor embeddings, similarity      │
└─────────────────────────────────────────────────┘
```

---

## Agent Workflow

### Recipe Generation Flow
```
User: "I want to make baked potatoes"
    ↓
Agent checks user's location → "Manila, Philippines"
    ↓
Agent queries ingredient database → "Sweet potatoes more common than russet"
    ↓
Agent generates recipe with substitutions:
  - Russet → Sweet potato
  - American cheddar → Quickmelt cheese
  - Sour cream → All-purpose cream
    ↓
Agent presents recipe with explanation
    ↓
User cooks, rates, provides feedback
    ↓
Agent remembers: "Sweet potato + quickmelt = good substitution"
```

### Memory Recall Flow
```
User: "What did I make last Tuesday?"
    ↓
Agent queries memory → "You made baked sweet potatoes with garlic butter"
    ↓
Agent suggests: "Want to try smoked paprika this time?"
    ↓
User: "Yes"
    ↓
Agent generates variation, remembers the tweak
```

### Social Discovery Flow
```
User opens Cookbook
    ↓
Agent shows: "5 people near you made pasta dishes today"
    ↓
User browses, finds interesting recipe
    ↓
User taps "Remix" → Agent adapts to their ingredients
    ↓
User cooks, shares back to community
    ↓
Network effect compounds
```

---

## Data Model

### User
```json
{
  "id": "uuid",
  "name": "Jordan",
  "location": "Cincinnati, OH",
  "dietary_restrictions": ["none"],
  "cooking_skill": "intermediate",
  "taste_profile": {
    "spicy": 0.7,
    "savory": 0.9,
    "sweet": 0.4,
    "umami": 0.8
  },
  "subscription": "agent_pass_bundle",
  "usage_today": {
    "recipes_generated": 3,
    "memory_recalls": 1
  }
}
```

### Recipe
```json
{
  "id": "uuid",
  "title": "Garlic Butter Sweet Potatoes",
  "creator_id": "uuid",
  "region": "Philippines",
  "ingredients": [
    {
      "name": "Sweet Potato",
      "quantity": "4 medium",
      "substitutes": ["Russet Potato", "Yam"]
    }
  ],
  "steps": ["..."],
  "flavor_tags": ["savory", "garlic", "butter"],
  "rating": 4.7,
  "remix_count": 23,
  "created_at": "2026-06-11"
}
```

### Memory Entry
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "recipe_id": "uuid",
  "date": "2026-06-11",
  "substitutions_used": [
    {
      "original": "Russet Potato",
      "used": "Sweet Potato",
      "rating": 5,
      "notes": "Even better than original"
    }
  ],
  "feedback": "Family loved it",
  "would_make_again": true
}
```

---

## Ingredient Database

### Structure
- **Base ingredients** (universal): potato, tomato, chicken, rice, etc.
- **Regional availability** (per country/region): what's actually in stores
- **Substitution pairs**: what can replace what, with flavor impact scores
- **Seasonal variants**: what's fresh when

### Data Sources
- USDA FoodData Central (US ingredients)
- Local grocery APIs (where available)
- Community-contributed data (users add local ingredients)
- LLM-generated substitution suggestions (validated by community)

---

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Frontend | React Native + Next.js | Cross-platform, fast iteration |
| API | Node.js + Express | Fast, JSON-native |
| Agents | Python + LangChain | Best LLM integration ecosystem |
| Database | PostgreSQL | Structured data, reliable |
| Cache | Redis | Sessions, rate limiting |
| Vector Store | Pinecone / Weaviate | Flavor embeddings, similarity search |
| Storage | S3 | Images, media |
| Auth | Auth0 / Clerk | Social login, phone verification |
| Payments | Stripe + Circle USDC | Fiat + crypto |
| Hosting | Vercel + Railway | Fast, cheap, scales |

---

## Monetization Integration

### Free Tier
- 3 recipes/day, 1 memory recall/day
- Social: view only
- No meal planning

### Individual ($5/mo)
- 20 recipes/day, 10 memory recalls/day
- Social: share, comment, remix
- Basic meal planning (1 week)

### Agent Pass ($20/mo)
- Unlimited everything
- Advanced meal planning (monthly)
- Priority agent response
- Early access to new features

---

## MVP Scope (Phase 1)

### Must Have
- [ ] Recipe generation agent
- [ ] Basic ingredient adaptation (10 regions)
- [ ] Persistent memory (recipe history)
- [ ] User accounts + auth
- [ ] Web app (mobile-responsive)

### Nice to Have
- [ ] Social sharing
- [ ] Flavor graph
- [ ] Meal planning
- [ ] Mobile app

### Not in MVP
- [ ] Community features (comments, ratings)
- [ ] Grocery list integration
- [ ] Nutritional tracking
- [ ] Multi-language support

---

## Launch Strategy

1. **Week 1-2:** Build MVP (recipe gen + memory + basic auth)
2. **Week 3:** Internal testing (Jordan + Christel + friends)
3. **Week 4:** Beta launch (invite-only, 50 users)
4. **Week 5-6:** Iterate based on feedback
5. **Week 7:** Public launch + Agent Pass pricing
6. **Week 8+:** Add social features, scale infrastructure

---

*Document created: June 11, 2026*
*Owner: Gentech (Jordan + Agent)*
*Status: Architecture approved, ready for Phase 1 build*
