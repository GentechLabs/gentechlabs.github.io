# Agent Repairathy — Design Doc

**Date:** 2026-05-23
**Status:** 🟢 Building
**Slogan:** "I've built the agents to help repair you, to help get you back on track."

## Problem
Mental health apps are $50B market by 2028. 100M+ users. But existing solutions (Ash, AVA CALM) are generic chatbots. No one is doing voice-first, personalized wellness with real accountability.

## Solution
Agent Repairathy — an AI wellness companion that does daily check-ins, tracks emotional baselines, nudges habits, and provides real talk (not corporate therapy speak).

## Positioning
- NOT therapy (legal risk: Illinois/Nevada banned AI psychotherapy)
- IS wellness coaching / emotional accountability
- Think: "tough love friend who actually cares" not "therapist robot"

## Voice Strategy
- **Good Cop** (Uncle Iroh / Christel): Warm, supportive, wise
- **Bad Cop** (Optimus Prime / Steve Harvey): Real talk, accountability, roast when needed
- **Context-aware switching**: Bad cop when you're slacking, good cop when you're struggling

## Core Features

### 1. Daily Check-In
- "How are you feeling?" → voice response
- Track mood on 1-10 scale
- Compare to baseline (is this normal for you?)
- Flag concerning patterns

### 2. Journaling (Voice-First)
- Talk to your agent, it transcribes + summarizes
- AI extracts themes, patterns, triggers
- Weekly summary: "You mentioned work stress 5 times this week"

### 3. Habit Tracking
- Define 3-5 habits (exercise, sleep, meditation, etc.)
- Daily accountability nudges
- Streak tracking with voice celebrations
- "You've exercised 4 days in a row — Optimus Prime is proud"

### 4. Emotional Baseline
- Track mood over time (7-day rolling average)
- Detect deviations: "Your mood has been 30% lower this week"
- Suggest actions based on patterns

### 5. Accountability Partner
- Agent checks in at scheduled times
- If you miss a check-in: gentle roast
- If you're slacking: real talk
- If you're thriving: celebration

## Revenue Model
- Free tier: 1 check-in/day, basic tracking
- Premium ($9.99/mo): Unlimited check-ins, voice conversations, weekly reports
- Family ($19.99/mo): 3 accounts, shared accountability

## Integration Points
- Agent Arena: Wellness agents as a game layer
- EarnFi: Earn rep for healthy habits
- WURK: Human wellness coaches as a job category

## Legal Positioning
- "Wellness coaching" not "therapy"
- "Accountability partner" not "mental health treatment"
- Clear disclaimers: "Not a substitute for professional help"
- Avoid clinical language (diagnosis, treatment, prescription)

## Hackathon Fit
- QVAC (privacy-first local AI) — runs on device
- Google Cloud Rapid Agent — Gemini-powered
- Arbitrum Open House — Agentic track
