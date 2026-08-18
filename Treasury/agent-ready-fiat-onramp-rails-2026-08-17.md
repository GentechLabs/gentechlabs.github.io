# Agent-Ready Fiat On-Ramp Rails — the front door for the Agentic Treasury

**Date:** 2026-08-17
**Source:** MoonPay Agents launch (Feb 24, 2026) + Transak programmatic on-ramps + market scan
**Owner:** The Steward (Agentic Treasury)

## Why this matters
The Agentic Treasury's story is "**deposit USDC, self-manages**." The missing piece
is the **fiat → crypto front door**: a user should be able to on-ramp dollars →
USDC → straight into the treasury in one flow, and the agent handles the rest
(deploy, yield, rebalance). These rails close that loop.

**Key distinction:** these are **user-facing on-ramps** (KYC-gated), NOT rails the
treasury itself uses to move capital. They are the front door for new deposits.

## The landscape — how many are agent-ready?

### 🥇 Agent-native (MCP/CLI — built FOR agents)
| Rail | Agent support | Notes |
|---|---|---|
| **MoonPay Agents** | CLI + MCP server | Non-custodial wallets, x402 support, `moonpay-virtual-account` (fiat on-ramp w/ KYC), `moonpay-deposit`, `moonpay-swap-tokens`, `moonpay-trading-automation` (DCA/limit/stop-loss). Explicitly built for "treasury agents." **Primary pick.** |

### 🥈 Programmatic API (agent-callable, not MCP-native)
| Rail | Coverage | Notes |
|---|---|---|
| **Transak** | 150+ countries, 75+ chains | "AI agents On/Off-Ramps that live inside your wallet." Whitelabel API, UPI/Pix. |
| **Coinbase Onramp** | US + 90 countries | Headless API, **zero-fee USDC on/off-ramp**, guest checkout. Strong US fit. |
| **Ramp Network** | 150+ countries, EU/UK strong | MiCAR-authorized, 0.49% SEPA, clean SDKs. |
| **Kado** | 170+ countries | Stablecoin-native, cheapest off-ramp (~1.5% flat). |
| **Stripe Crypto Onramp** | US/EU only | 1.5% flat, no off-ramp. |
| **Alchemy Pay** | 173 countries, 300+ methods | Zero-fee USDC on-ramp, RWA platform. |

### 🥉 All-in-one (wallet + onramp + orchestration)
| Rail | Notes |
|---|---|
| **Crossmint** | Only provider bundling wallets + onramps + offramps + compliance in one API. 50+ chains. |

## Recommendation
- **Primary:** MoonPay Agents — the only truly agent-native rail (MCP/CLI), built for treasury agents.
- **Alternates:** Transak (broad emerging-market reach), Coinbase Onramp (zero-fee USDC, US fit).
- **Watch:** Crossmint (all-in-one), Kado (stablecoin-native off-ramp).

## Status
- Research complete. No integration wired yet — this is the on-ramp layer spec.
- Next: wire MoonPay as the first on-ramp rail when we build the deposit flow.

## Related rails (same folder)
- `MoneyGram-Ramps-Solana-rail-2026-08-11.md` — cash↔crypto retail rail (reference)
- `Agent-Network-Rails-Scanner-2026-08-06.md`
- `GTA-acquisition-rails-avax-solana-2026-08-05.md`
