# Education Layer — Tutors

> GenTech Labs · June 2026
> Layer 6 of the Agent Pass Suite

---

## Vision

**"I want to learn X" → Agent builds you a personalized learning dashboard.**

The Education layer turns any topic into a structured, visual learning experience. Agent detects what you want to learn, curates resources, tracks progress, and quizzes you. Not another course platform — a personal tutor that adapts to your pace and connects learning to your real goals.

**Origin story:** Cara at work mentioned her son has trouble learning. Needs something visual and engaging. This is the Tutors layer — built for kids, useful for everyone.

---

## Core Features

### 1. Topic Detection & Curriculum Generation
- User says: "I want to learn Solidity" or "How does DeFi work?"
- Agent generates a structured curriculum: modules, prerequisites, estimated time
- Adapts to user's level (beginner/intermediate/advanced)
- Pulls from curated resource pools (docs, videos, interactive tools)

### 2. Learning Dashboard
- Visual progress tracker (modules completed vs total)
- Active module card with key concepts
- Quiz/test section for self-assessment
- Resource links (official docs, tutorials, videos)
- Notes section (agent-captured from conversations)

### 3. spaced Repetition & Quizzes
- Agent generates quizzes from learned material
- Spaced repetition schedule (review at intervals)
- Flashcard mode for key concepts
- Track mastery per topic

### 4. Cross-Layer Learning Connections
- "You're learning Solidity → here's how it connects to your AgentBridge contracts"
- "You're cooking Filipino food → want to learn the science behind adobo?"
- Learning feeds into other layers naturally

### 5. Milestone Tracking
- Complete modules → earn badges
- Streak tracking (days learning in a row)
- Portfolio of completed courses
- Shareable certificates (agent-generated)

---

## Architecture

```
┌─────────────────────────────────────────┐
│            USER REQUEST                  │
│  "I want to learn [topic]"              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         CURRICULUM ENGINE               │
│  • Topic decomposition                  │
│  • Resource curation                    │
│  • Difficulty calibration               │
│  • Prerequisite mapping                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         DASHBOARD RENDERER              │
│  • JSON template + data (same engine)   │
│  • Progress bars, quiz cards, badges    │
│  • Mobile-first, single scroll          │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         MEMORY LAYER                    │
│  • What user has learned                │
│  • Quiz scores and mastery levels       │
│  • Spaced repetition schedule           │
│  • Cross-layer connections              │
└─────────────────────────────────────────┘
```

---

## JSON Data Format

```json
{
  "learner": {
    "name": "Jordan",
    "level": "beginner",
    "joined": "2026-06-12",
    "streak": 3,
    "totalHours": 12
  },
  "courses": [
    {
      "id": "solidity-basics",
      "title": "Solidity Fundamentals",
      "topic": "Smart Contracts",
      "status": "in-progress",
      "progress": 45,
      "modules": [
        {
          "id": "mod-1",
          "title": "Variables & Types",
          "status": "completed",
          "completedAt": "2026-06-10"
        },
        {
          "id": "mod-2",
          "title": "Functions & Modifiers",
          "status": "active",
          "resources": [
            { "type": "doc", "title": "Solidity Docs — Functions", "url": "..." },
            { "type": "video", "title": "Cyfrin — Functions 101", "url": "..." }
          ]
        }
      ],
      "quizzes": [
        {
          "moduleId": "mod-1",
          "score": 85,
          "attempts": 2,
          "lastTaken": "2026-06-10"
        }
      ],
      "badges": ["first-module", "quiz-master"]
    }
  ],
  "milestones": [
    { "title": "First Course Started", "date": "2026-06-08", "icon": "🎓" },
    { "title": "10 Modules Completed", "date": "2026-06-12", "icon": "📚" }
  ]
}
```

---

## Dashboard Sections (top to bottom)

1. **Header** — Learner name, streak, total hours, badges earned
2. **Active Course Card** — Current module, key concepts, continue button
3. **Progress Overview** — All courses with progress bars
4. **Quiz Section** — Recent scores, retake options, mastery levels
5. **Milestones** — Achievement badges, streak calendar
6. **Resource Library** — Saved docs, videos, tools across all courses
7. **Cross-Layer Connections** — "Your learning connects to..."

---

## Revenue

Free tier: 2 courses, 5 quizzes/day
Agent Pass ($20/mo): Unlimited courses, unlimited quizzes, spaced repetition, certificates
Individual: $5/mo for Education Pro

---

## Connections to Other Layers

| Layer | Connection |
|-------|-----------|
| 🍳 Cookbook | "Want to learn the science of fermentation?" → baking bread chemistry |
| 🎮 Gaming | "Learn POE2 build optimization" → math behind damage calculation |
| 💰 Finance | "Learn DeFi yield" → understand your own positions |
| 📓 Journal | Learning reflections, what you discovered today |
| ✈️ Travel | "Learn basic Tagalog" → preparing for PH trip |
| 🏆 Milestones | Course completions become milestones |

---

## Origin

- **Jun 12, 2026:** Jordan mentions Cara at work wants something visual for her son to learn. Education layer added to GenTech Suite vision.
- First user: Cara's son (pending)
- Second user: Jordan (Solidity learning)
- Third user: Christel (English/Tagalog, cooking techniques)

---

*GenTech Tutors — Learning that adapts to you.*
