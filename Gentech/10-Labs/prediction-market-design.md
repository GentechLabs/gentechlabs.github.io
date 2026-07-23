# Prediction Market — Fed Decision Betting
## Architecture Design Document

> **Purpose:** Design a decentralized prediction market for Federal Reserve interest rate decisions, with x402 payment integration for agent-to-agent betting.

---

## 1. Market Concept

### What
A prediction market where users (human + AI agents) bet on FOMC (Federal Open Market Committee) interest rate decisions:
- **Rate Change** — Hike, Hold, Cut (binary + ternary outcomes)
- **Basis Points** — Exact change in bps (25, 50, 75, etc.)
- **Direction** — Hawkish vs Dovish language in statement
- **Timing** — Which meeting (8 per year)

### Why x402
- Agents can place bets via HTTP 402 — no wallet popup needed
- Gasless settlement via Q402 or CDP facilitator
- Automated payout on resolution via oracle

### Target Users
- DeFi traders hedging rate exposure
- AI agents running automated macro strategies
- Retail users via simple web UI

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Market List  │  │ Bet Slip     │  │ Portfolio/History │   │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘   │
│         │               │                    │              │
│         └───────────────┼────────────────────┘              │
│                         │ HTTP/WS                           │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                    API Gateway (x402)                         │
│  ┌──────────────────────┴──────────────────────────────┐    │
│  │              x402 Payment Middleware                  │    │
│  │  HTTP 402 → Payment → Verify → Settle → Response     │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
│  ┌──────────────────────┴──────────────────────────────┐    │
│  │              Prediction Market Engine                 │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │    │
│  │  │ Market   │  │ Order    │  │ Settlement       │   │    │
│  │  │ Factory  │  │ Book     │  │ Engine           │   │    │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                   Smart Contracts (Base)                      │
│  ┌──────────────────────┴──────────────────────────────┐    │
│  │  MarketFactory.sol                                   │    │
│  │  - Create markets                                   │    │
│  │  - Manage outcomes                                  │    │
│  │  - Fee configuration                                │    │
│  └──────────────────────┘                               │    │
│  ┌──────────────────────┐  ┌──────────────────────────┐ │    │
│  │  Market.sol          │  │  ConditionalTokens.sol   │ │    │
│  │  - Outcome shares    │  │  - ERC1155 tokens        │ │    │
│  │  - Betting pool      │  │  - Split/merge           │ │    │
│  │  - Resolution        │  │  - Payout distribution   │ │    │
│  └──────────────────────┘  └──────────────────────────┘ │    │
│  ┌──────────────────────┐  ┌──────────────────────────┐ │    │
│  │  Oracle.sol          │  │  x402Adapter.sol          │ │    │
│  │  - UMA integration   │  │  - Payment verification  │ │    │
│  │  - Fed data feed     │  │  - Gasless settlement    │ │    │
│  │  - Dispute period    │  │  - Agent wallet support  │ │    │
│  └──────────────────────┘  └──────────────────────────┘ │    │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Smart Contract Design

### MarketFactory.sol
```solidity
// Creates and manages prediction markets
contract MarketFactory {
    struct MarketConfig {
        string question;           // "Will Fed cut rates at [date]?"
        string[] outcomes;         // ["Hike 25bps", "Hold", "Cut 25bps"]
        uint256 resolutionTime;    // Unix timestamp
        uint256 tradingDeadline;   // Last time to place bets
        address oracle;            // UMA Oracle address
        uint256 feeBps;            // Protocol fee in basis points
    }
    
    function createMarket(MarketConfig calldata) returns (address market);
    function getMarkets(bool active) view returns (address[]);
    function setProtocolFee(uint256 newFeeBps);
}
```

### Market.sol
```solidity
// Individual prediction market
contract Market {
    using ConditionalTokens for CT;
    
    // ERC1155 shares: outcomeId => balance
    mapping(uint256 => uint256) public totalShares;
    mapping(address => mapping(uint256 => uint256)) public shares;
    
    // Core functions
    function buy(uint256 outcomeId, uint256 amount) payable;
    function sell(uint256 outcomeId, uint256 shares) payable;
    function splitPosition(uint256 amount);  // Mint all outcome shares
    function mergePosition(uint256[] calldata amounts);  // Burn back to collateral
    
    // Resolution
    function resolve(uint256 winningOutcome) onlyOracle;
    function redeem(uint256 outcomeId) returns (uint256 payout);
    
    // x402 integration
    function payViaX402(bytes calldata paymentProof, uint256 outcomeId, uint256 amount);
}
```

### Oracle.sol
```solidity
// Fed decision oracle — reads from UMA or custom data feed
contract FedOracle {
    struct FedDecision {
        uint256 meetingDate;
        uint256 rateChange;  // in basis points
        string statement;    // "Hike", "Hold", "Cut"
        uint256 timestamp;
    }
    
    function proposeOutcome(uint256 marketId, uint256 outcome) onlyBonded;
    function disputeOutcome(uint256 marketId, uint256 proposedOutcome) onlyBonded;
    function getLatestFedDecision() view returns (FedDecision memory);
}
```

### x402Adapter.sol
```solidity
// Gasless payment adapter for agent betting
contract X402Adapter {
    // Verify x402 payment proof and credit shares
    function verifyAndCredit(
        bytes calldata paymentProof,
        address market,
        uint256 outcomeId,
        uint256 amount
    ) external returns (bool);
    
    // Settle via Q402 or CDP facilitator
    function settlePayment(
        address payee,
        uint256 amount,
        bytes calldata facilitatorProof
    ) external;
}
```

---

## 4. x402 Integration Flow

```
Agent → POST /api/market/1/buy
  Headers: { "Content-Type": "application/json" }
  Body: { "outcomeId": 0, "amount": "10.00" }
  
  ← 402 Payment Required
  Headers: { "Payment-Required": "<base64>" }
  Body: {
    "accepts": [{
      "scheme": "exact",
      "network": "eip155:8453",
      "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  // USDC on Base
      "amount": "10000000",  // $10 USDC
      "payTo": "0x..."
    }]
  }

Agent → POST /api/market/1/buy (with payment)
  Headers: {
    "Payment-Signature": "<base64>",
    "Content-Type": "application/json"
  }
  Body: { "outcomeId": 0, "amount": "10.00" }
  
  ← 200 OK
  Headers: { "Payment-Response": "<base64>" }
  Body: {
    "shares": 10,
    "outcomeId": 0,
    "txHash": "0x...",
    "position": { "market": 1, "outcome": "Hike 25bps", "shares": 10 }
  }
```

---

## 5. Pricing Model

| Action | Price | Notes |
|--------|-------|-------|
| View markets | Free | Public data |
| Place bet | $0.01 + 0.5% fee | Per transaction |
| Cancel bet | $0.005 | Before trading deadline |
| Redeem winnings | Free | After resolution |
| API access (agents) | $0.001/call | x402 pay-per-call |
| Market creation | $5.00 | Bond, refunded if resolved honestly |

---

## 6. UI/UX Mockups

### Market List Page
```
┌─────────────────────────────────────────────────────┐
│  🔮 Fed Prediction Markets                          │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  FOMC July 29-30, 2026                      │   │
│  │  Will the Fed cut rates?                    │   │
│  │                                             │   │
│  │  [Hike 25bps]  $0.15  ████░░░░ 15%         │   │
│  │  [Hold]        $0.55  ██████████░░ 55%     │   │
│  │  [Cut 25bps]   $0.30  ██████░░░░ 30%       │   │
│  │                                             │   │
│  │  Volume: $124K  |  Traders: 342  |  3d left │   │
│  │  ┌──────────────────────┐                    │   │
│  │  │  Place Bet →         │                    │   │
│  │  └──────────────────────┘                    │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  FOMC September 17, 2026                    │   │
│  │  Rate change magnitude?                     │   │
│  │  [0bps] $0.40 | [25bps] $0.35 | [50bps]... │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Bet Slip (Mobile)
```
┌─────────────────────┐
│  Bet Slip           │
│                     │
│  Market: FOMC Jul   │
│  Outcome: Cut 25bps │
│  Current Price: $0.30│
│                     │
│  ┌─────────────────┐│
│  │ Amount: $ 10.00 ││
│  └─────────────────┘│
│  Shares: 33.33      │
│  Fee: $0.05         │
│  Max Payout: $33.33 │
│                     │
│  Pay with:          │
│  ○ Wallet (MetaMask)│
│  ● x402 (gasless)   │
│  ○ Q402 (trial)     │
│                     │
│  ┌─────────────────┐│
│  │  Place Bet $10  ││
│  └─────────────────┘│
└─────────────────────┘
```

### Portfolio View
```
┌─────────────────────────────────────────────┐
│  My Positions                               │
│                                             │
│  Active: 3 markets                          │
│  Total at risk: $450                        │
│  Unrealized P&L: +$120                     │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  FOMC Jul 29 — Cut 25bps           │   │
│  │  Shares: 50 @ $0.30 = $15.00       │   │
│  │  Current value: $30.00 (+100%)     │   │
│  │  [Sell] [Add]                      │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │  FOMC Sep 17 — Hold               │   │
│  │  Shares: 100 @ $0.55 = $55.00      │   │
│  │  Current value: $44.00 (-20%)      │   │
│  │  [Sell] [Add]                      │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## 7. Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Blockchain** | Base (L2) | Low fees, x402 native, USDC |
| **Smart Contracts** | Solidity + Foundry | Industry standard, fast tests |
| **Oracle** | UMA Optimistic Oracle | Battle-tested, dispute mechanism |
| **Payment** | x402 v2 + Q402 | Gasless, agent-friendly |
| **Backend** | FastAPI + x402 middleware | Already have the pattern |
| **Frontend** | React + Tailwind | Familiar, fast iteration |
| **Indexer** | The Graph / Ponder | Real-time market data |
| **Agent API** | MCP server | Agent discovery + betting |

---

## 8. Implementation Phases

### Phase 1 — Core Contracts (Week 1)
- [ ] MarketFactory.sol — create + manage markets
- [ ] Market.sol — betting, shares, resolution
- [ ] ConditionalTokens.sol — ERC1155 split/merge
- [ ] Oracle.sol — UMA integration
- [ ] Tests: forge test

### Phase 2 — x402 Integration (Week 2)
- [ ] x402Adapter.sol — payment verification
- [ ] FastAPI backend with x402 middleware
- [ ] Bet placement via HTTP 402 flow
- [ ] Q402 gasless settlement option

### Phase 3 — Frontend (Week 3)
- [ ] Market list + detail pages
- [ ] Bet slip with x402/Q402 payment options
- [ ] Portfolio + history
- [ ] Agent API endpoints

### Phase 4 — Agent Integration (Week 4)
- [ ] MCP server for agent betting
- [ ] Automated macro strategies
- [ ] Fed data feed monitoring
- [ ] Cron-based position management

---

## 9. Risk & Mitigation

| Risk | Mitigation |
|------|-----------|
| Oracle manipulation | UMA's dispute bond + voter system |
| Smart contract bugs | Foundry fuzz tests + audit |
| Low liquidity | Bootstrap pool + incentives |
| Regulatory uncertainty | Non-custodial, no KYC, US only? |
| Agent spam | x402 pay-per-call pricing floor |

---

## 10. Next Steps

1. **Fork Polymarket's CTF contracts** — Gnosis Conditional Token Framework
2. **Deploy MarketFactory on Base Sepolia** — test with fake USDC
3. **Wire x402 middleware** — reuse from GenTech gateway
4. **Build minimal UI** — market list + bet slip
5. **Test agent flow** — Hermes places bet via x402
