# 🎙️ Creative Spec: AAE Trading Arena (ElevenHacks #6)

## 🎯 Vision
Transform the Autonomous AI Economy (AAE) from a protocol into an immersive, audio-driven educational experience. Instead of a static tutorial, we build a "Trading Simulator" inside Zed that uses ElevenLabs voices to coach users through historical market scenarios.

## 🧠 The Educational Engine: "Scenario Mode"
We aren't just simulating trades; we are simulating *history*. 

### 1. Historical Crash Simulations (e.g., "The Oct 10th Event")
- **The Setup:** The UI mimics a real-time chart of a known crash.
- **The Action:** Users must react to the volatility (hedge, exit, or hold).
- **The Voice Layer:** 
    - **The Narrator (Desmond):** "The floor is falling out! Panic is hitting the order books! What's the move?"
    - **The Coach (YoYo):** "Look at the volume. This isn't a dip; it's a liquidation cascade. You need to protect your capital *now*."

### 2. Pattern Recognition Training
- **The Setup:** The simulator pauses at key technical formations (Head and Shoulders, Higher Lows, Bullish Breakouts).
- **The Action:** User identifies the pattern via code/command.
- **The Voice Layer:**
    - **The Dev (DMOB):** "Wait, the data is converging. I'm seeing a classic Head and Shoulders forming on the 4-hour. You seeing this?"
    - **Feedback:** Correct identification triggers a "Win" audio cue and an explanation of *why* it's a signal.

## 🎭 Persona & Voice Mapping
| Persona | Voice Profile | Role | Tone |
| :--- | :--- | :--- | :--- |
| **Desmond** | High-Energy / Hype | The MC | Urgent, exciting, keeps the momentum. |
| **YoYo** | Cold / Analytical | The Strategist | Calm, authoritative, focuses on risk/reward. |
| **DMOB** | Fast / Techy | The Analyst | Obsessed with data, slightly chaotic, alerts to "glitches" in the chart. |

## 🛠️ Zed Integration
- **Interaction:** Users "trade" by typing commands or modifying a small JSON state file in Zed.
- **Output:** Changes in the file trigger the ElevenLabs API to play the corresponding persona's reaction in real-time.

## 🔊 Sonic Brand Goals (Sync with Vanito)
- **Ambience:** Low-hum of a trading floor, distant shouting, ticker-tape sounds.
- **Cues:** Distinct "Siren" for crashes, "Ding" for correct pattern identification.
