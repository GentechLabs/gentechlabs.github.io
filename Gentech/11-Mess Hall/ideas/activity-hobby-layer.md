# Activity/Hobby Layer — Animated Achievement Dashboards

> GenTech Labs · June 2026
> Layer 7 of the Agent Pass Suite

---

## Vision

**Any hobby, any activity — tracked with rich, animated visual feedback that makes every achievement feel like a celebration.**

The Activity layer isn't about tracking scores. It's about making scores *feel* like something. When you get a strike in bowling, the screen should explode with animated pins. Bullseye in darts? Dart flies to the board. Perfect game? Confetti rains from the top. The real product isn't data — it's the animated graphics experience that turns mundane hobby tracking into something you actually want to open every day.

**The insight:** Every hobby has a "strike moment" — a thing that feels amazing when it happens. Our job is to animate that moment. Bowling has pins. Darts has bullseyes. Pool has the 8-ball drop. Music has the perfect run. Each activity gets its own visual language, and every achievement triggers a unique animation that makes you *feel* the win.

**Origin story:** Jordan wanted bowling scores with animated pin graphics. Realized the pattern applies to literally any activity with scoring and achievements. The "strike animation" is a universal product pattern — not a bowling feature.

---

## Core Features

### 1. Activity Profiles
- Create a dashboard for any hobby or activity
- Quick-start templates for common activities (bowling, darts, pool, etc.)
- Custom activity creation: define your own scoring system, achievements, and animations
- One dashboard per activity, multiple activities per user
- Agent auto-detects hobby mentions: "Went bowling today" → prompts to log scores

### 2. Animated Achievement Graphics
- CSS/JS keyframe animations triggered by agent data updates
- Each activity has unique animation themes and achievement animations
- Achievement types: strike, spare, bullseye, perfect score, personal best, streak, milestone
- Animations fire in real-time when scores are logged
- Mobile-optimized: lightweight SVG/CSS animations, no heavy libraries
- Accessibility: reduced-motion support, animation toggle in settings

### 3. Score Tracking
- Frame-by-frame, round-by-round, session-by-session recording
- Historical score browser (filter by date, opponent, location)
- Session summaries with highlight reels (animated recap)
- Quick-log: agent detects "just bowled a 200" → auto-fills score card
- Manual entry with smart validation (can't enter 201 in bowling)

### 4. Stats & Trends
- Running averages (last 5, 10, 20 sessions)
- Improvement curves with visual trend lines
- Personal bests with celebration animations
- Distribution charts (score histogram)
- Comparative stats: this month vs last month, this year vs last year
- AI-generated insights: "Your average has improved 12% over the last 3 months"

### 5. Social Sharing
- Animated GIF export of achievement moments (strike animation → shareable GIF)
- Canvas recording for real-time animation capture
- Share to Telegram, Twitter, Instagram Stories
- Leaderboards (opt-in): compete with friends on any activity
- Challenge friends: "Beat my 180 in darts this week"

### 6. Seasonal Leagues
- Track performance over time across multiple sessions
- League tables with rankings, points, win/loss records
- Season reset with archive of past seasons
- Playoff brackets for tournament-style competitions
- Custom league creation: invite friends, set rules, track standings

### 7. Custom Scoring Rules
- Different activities have different scoring systems
- Bowling: 10 frames, strikes (10 + next 2), spares (10 + next 1)
- Darts: 501 countdown, checkout combos, legs/sets
- Pool: 8-ball, 9-ball, straight pool rules
- Archery: 10-zone scoring, end totals, round aggregates
- Custom: define your own point system, win conditions, and bonus rules

---

## Activity Templates (Pre-Built)

### 🎳 Bowling
- **Scoring:** 10 frames, strike = 10 + next 2 rolls, spare = 10 + next 1 roll
- **Stats:** Average, high game, strike %, spare %, frames per game
- **Animations:** Pin explosion (strike), pin scatter (spare), gutter ball (fail), perfect game confetti
- **Templates:** Standard 10-pin, 5-pin, duckpin

### 🎯 Darts
- **Scoring:** 501/301 countdown, double-out, treble multipliers
- **Stats:** Checkout %, average per dart, 180s count, legs won
- **Animations:** Dart flying to board, bullseye glow, 180 explosion, checkout celebration
- **Templates:** 501, 301, Cricket, Around the Clock

### 🎱 Pool/Billiards
- **Scoring:** 8-ball (solids/stripes), 9-ball (sequential), straight pool (14.1)
- **Stats:** Rack wins, runs, safety play %, fouls, ball-in-hand opportunities
- **Animations:** 8-ball drop, ball scatter, scratch warning, rack break
- **Templates:** 8-Ball, 9-Ball, Straight Pool, Cutthroat

### 🏹 Archery
- **Scoring:** 10-zone (X, 10, 9...1), ends of 3-6 arrows, rounds (WA, NFAA)
- **Stats:** Average per arrow, end totals, X-count, round aggregates
- **Animations:** Arrow flight, bullseye hit, gold ring pulse, end completion
- **Templates:** WA 720, NFAA 300, Indoor 600, Practice Rounds

### 🎵 Music
- **Scoring:** Practice session duration, song mastery %, skill progression
- **Stats:** Practice streaks, songs learned, skill level, session frequency
- **Animations:** Note cascade, chord wave, perfect run sparkle, practice streak fire
- **Templates:** Practice Log, Song Mastery, Skill Tracker, Jam Session

### 🏃 Fitness
- **Scoring:** Workout type, duration, intensity, PRs, body measurements
- **Stats:** Workout frequency, total volume, PR tracker, streak calendar
- **Animations:** PR explosion, streak fire, rep counter, finish line
- **Templates:** Strength Training, Running, HIIT, Yoga, Custom Workout

---

## Animated Graphics System

### Architecture
```
┌─────────────────────────────────────────┐
│           SCORE INPUT                    │
│  User logs score → Agent validates      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         ACHIEVEMENT DETECTOR            │
│  • Check against achievement rules      │
│  • Detect milestones, PBs, streaks     │
│  • Fire appropriate animation events    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         ANIMATION ENGINE                │
│  • CSS keyframe animations             │
│  • SVG particle effects                │
│  • Canvas recording for GIF export     │
│  • Reduced-motion fallbacks            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         DASHBOARD RENDERER              │
│  • Updated scores + celebration overlay│
│  • Stats refresh                       │
│  • Social share prompt                 │
└─────────────────────────────────────────┘
```

### Achievement Types & Animations

| Achievement | Trigger | Animation | Duration |
|-------------|---------|-----------|----------|
| 🎳 Strike | All 10 pins on first roll | Pin explosion + flash | 2s |
| 🎳 Spare | All pins on second roll | Pin scatter + sparkle | 1.5s |
| 🎳 Perfect Game | 300 score | Confetti rain + gold banner | 3s |
| 🎯 Bullseye | Double bull (50) | Dart hit + glow ring | 1.5s |
| 🎯 180 | Maximum score throw | Explosion + "180!" text | 2.5s |
| 🎯 Checkout | Game-winning combo | Celebration burst | 2s |
| 🎱 8-Ball Sunk | Winning shot | Ball drop + sparkle | 2s |
| 🎱 Rack Win | Complete rack | Victory flash | 1.5s |
| 🏹 Gold | 10 or X score | Gold ring pulse | 1s |
| 🏹 Perfect End | All Xs in end | Arrow flight + gold | 2s |
| 🎵 Perfect Run | No mistakes in song | Note cascade + glow | 2s |
| 🎵 Streak | Consecutive practice days | Fire animation | 1.5s |
| 🏃 PR | Personal record | Explosion + "NEW PR!" | 2.5s |
| 🏃 Streak | Consecutive workout days | Streak fire | 1.5s |

### Animation Tech Stack
- **CSS Keyframes:** Primary animation method (lightweight, GPU-accelerated)
- **SVG Particles:** Pin explosions, confetti, sparkles (hardware-accelerated)
- **Canvas Recording:** Capture animations as animated GIFs for sharing
- **Web Animations API:** For complex sequenced animations
- **Reduced Motion:** `prefers-reduced-motion` media query support
- **Performance Budget:** Max 50KB animation assets per activity template

### Mobile Optimization
- Animations scale down on mobile (fewer particles, shorter duration)
- Touch-triggered: tap to replay achievement animation
- Offline-capable: animation assets cached locally
- Battery-friendly: animations pause when tab is hidden

---

## JSON Data Format

```json
{
  "user": "Jordan",
  "activity": {
    "type": "bowling",
    "name": "Friday Night Bowling",
    "template": "bowling-10pin",
    "createdAt": "2026-06-12",
    "settings": {
      "scoringSystem": "standard-10pin",
      "animationLevel": "full",
      "shareByDefault": true
    }
  },
  "sessions": [
    {
      "id": "sess-001",
      "date": "2026-06-12",
      "location": "Lucky Strike Lanes",
      "opponents": ["Christel", "Cara"],
      "frames": [
        { "frame": 1, "rolls": [10], "score": 20, "type": "strike" },
        { "frame": 2, "rolls": [7, 3], "score": 15, "type": "spare" },
        { "frame": 3, "rolls": [8, 1], "score": 9, "type": "normal" }
      ],
      "totalScore": 187,
      "result": "win",
      "highlights": ["strike", "spare"]
    }
  ],
  "achievements": [
    {
      "id": "ach-001",
      "type": "strike",
      "title": "Strike!",
      "date": "2026-06-12",
      "animation": "pin-explosion",
      "shared": true,
      "sharedTo": ["telegram"]
    },
    {
      "id": "ach-002",
      "type": "personal-best",
      "title": "New High Game!",
      "value": 212,
      "previousBest": 198,
      "date": "2026-06-14",
      "animation": "confetti-rain",
      "shared": false
    }
  ],
  "stats": {
    "gamesPlayed": 47,
    "average": 168.4,
    "highGame": 212,
    "highGameDate": "2026-06-14",
    "strikePercentage": 28.3,
    "sparePercentage": 41.2,
    "recentForm": [187, 165, 192, 201, 212],
    "improvement": {
      "last30Days": "+12.4%",
      "last90Days": "+8.1%"
    }
  },
  "streaks": {
    "current": 5,
    "longest": 12,
    "type": "weekly-sessions"
  },
  "personalBests": {
    "highGame": { "value": 212, "date": "2026-06-14" },
    "highSeries": { "value": 589, "date": "2026-06-07" },
    "bestStrikePercentage": { "value": 35.0, "date": "2026-05-20" }
  },
  "leagues": [
    {
      "id": "league-001",
      "name": "Summer 2026 Friday League",
      "season": "summer-2026",
      "rank": 3,
      "wins": 8,
      "losses": 4,
      "points": 1620
    }
  ]
}
```

---

## Dashboard Sections (top to bottom)

1. **Header** — Activity name, current streak, average score, rank
2. **Live Session** — Active game/scorecard with real-time score updates
3. **Achievement Feed** — Recent achievements with animation replay buttons
4. **Score History** — Session-by-session scores with trend visualization
5. **Stats Overview** — Key metrics grid (average, high game, streak, improvement %)
6. **Trend Chart** — Score progression over time (line chart with milestones marked)
7. **Personal Bests** — Record board with celebration animations on tap
8. **Leaderboard** — Friends/league rankings (opt-in social)
9. **Season Summary** — League standings, win/loss record, upcoming matches
10. **Social Share** — Quick-share latest achievement as animated GIF

---

## Revenue

- **Included in Agent Pass** ($20/mo): All activity templates, score tracking, basic animations, stats
- **Premium Animation Themes** ($2/mo add-on): Custom animation packs (retro arcade, neon glow, minimalist, seasonal themes)
- **Custom Activity Builder** ($5/mo): Create custom activities with custom scoring rules and animation triggers
- **League Premium** ($3/mo): Advanced league features (brackets, playoff tracking, custom rules)

---

## Connections to Other Layers

| Layer | Connection |
|-------|-----------|
| 🏆 Milestones | Activity achievements become milestones ("First Strike" → milestone) |
| 📱 Social | Share animated achievements to Telegram, Twitter, Instagram |
| 🎓 Education | Learning a new activity → training mode with skill progression |
| 💪 Health/Fitness | Workout tracking with animated progress and PR celebrations |
| 📓 Journal | Activity sessions auto-log to journal ("Bowled 187 tonight") |
| 💰 Finance | Prize money tracking for tournament wins |
| 🎮 Gaming | Esports tournament tracking with the same animation engine |
| 🔮 Predictions | "Will Jordan average 170+ this season?" → prediction market |

---

## Origin

- **Jun 12, 2026:** Jordan wanted bowling scores with animated pin graphics. "When you get a strike in bowling, there's an animation of pins falling. That's the real product."
- Realized the pattern applies to ANY activity with scoring and achievements — darts, pool, archery, music, fitness
- "Strike animation" became a universal product pattern: activity dashboard + animated achievement graphics
- First template: Bowling (because that's where it started)
- Second template: Darts (because "bullseye animation is even cooler")
- Vision expanded to include any hobby: cooking competitions, gaming tournaments, music jam sessions

---

*GenTech Activity — Every hobby deserves a celebration.*
