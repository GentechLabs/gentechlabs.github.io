# AdaptiveFolio — Demo Video Script

**Duration:** 2:30–3:00 minutes
**Format:** Screen recording + voiceover (Loom, YouTube, or Vimeo)
**Submission:** Agora Agents Hackathon — RFB 04 Adaptive Portfolio Manager

---

## Opening (0:00–0:15)

**[Screen: Landing page at protojay4789.github.io/adaptive-folio]**

"AdaptiveFolio is an AI-powered portfolio manager that detects market regimes and automatically rebalances your portfolio using USDC settled on Arc."

## The Problem (0:15–0:30)

**[Screen: Show regime detection panel]**

"Portfolio management requires constant rebalancing, regime detection, and cross-chain coordination — tasks that are tedious for humans. AdaptiveFolio does this autonomously."

## How It Works (0:30–1:30)

**[Screen: Regime detection in action]**

"Here's how it works. The AI continuously monitors market conditions across multiple signals — momentum, trend, volume conviction, and correlation. Right now it's detecting a sideways market with 90% confidence."

**[Screen: Show allocation shifting]**

"Based on the regime, it shifts allocation. Risk-on? More SOL and ETH. Risk-off? More USDC and stables. This happens automatically — no manual rebalancing needed."

**[Screen: Show drift detection + rebalance action]**

"When portfolio drift exceeds the threshold, AdaptiveFolio generates a rebalance action. In this demo, it's simulated — but on Arc, this settles in under a second for about one cent in USDC."

## Arc Settlement (1:30–1:50)

**[Screen: Show Arc settlement code/config]**

"Settlement happens on Arc — Circle's stablecoin-native L1. USDC is the gas token, so there's no token approval needed. Sub-second finality, ~$0.01 per transaction. This is what makes autonomous rebalancing practical."

## Live Demo (1:50–2:20)

**[Screen: Interactive demo showing real-time data]**

"The live demo pulls real market data from CoinGecko. You can see current prices, regime detection, and allocation recommendations updating in real-time. It works on mobile too."

## Close (2:20–2:45)

**[Screen: GitHub repo + live demo URL]**

"AdaptiveFolio — 38 tests passing, fully open source, live at protojay4789.github.io/adaptive-folio. Built for the Agora Agents Hackathon. Thank you."

---

## Recording Tips

1. **Use Loom** — easiest for screen recording + voiceover
2. **Keep it under 3 minutes** — judges review many submissions
3. **Show the live demo working** — real data, not mockups
4. **Mention Arc + USDC** — hits the Circle tool usage judging criterion
5. **Sound confident** — "We built this" energy

## Key Points to Hit

- [x] Regime detection (multi-signal AI)
- [x] Automatic rebalancing
- [x] Arc settlement (USDC, sub-second, ~$0.01)
- [x] Live demo with real data
- [x] Open source (38 tests)
- [x] Goal-based allocation (conservative/moderate/aggressive)
