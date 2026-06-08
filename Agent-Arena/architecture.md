# Agent Arena — Architecture

## Access Model (May 2026)

Four paths to participation — no gatekeeping, every user type has a lane:

| Path | Description | Target User |
|------|-------------|-------------|
| **Freemium** | Limited daily uses, taste the platform | Casual tinkerers |
| **Pay-per-use** | Micropayments (x402), flexible but stacks | Moderate users |
| **Subscription** | Unlimited access, premium convenience | Power users |
| **Earn it** | Grind reputation, unlock through participation | Grinders / zero-spend |

### Flywheel
1. Play Agent Arena → build rep
2. Build rep → unlock free campaigns on EarnFi
3. Free campaigns → promote your agent/strategy
4. Promotion → more players → deeper ecosystem

### Rep Incentives
- Higher borrowing limits (Agent Arena)
- Better matchmaking brackets
- Lower interest rates on loans
- EarnFi campaign rewards (high rep → free, medium → discounted, low → full price)

### Key Insight
Nobody *has* to spend money. They might *want* to once they see what's possible. Conversion happens naturally, not forced.

### Payment Infrastructure
- x402 micropayments (Ampersend / PayAI)
- Pay.sh integration
- WURK for human verification
- Multi-chain: Solana, Base, Arc
