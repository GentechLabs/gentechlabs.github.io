# Agent Arcade Phase 1 — Architecture & Build Spec

> **Status:** Design Complete — Ready for Build
> **Owner:** Forge (laptop agent)
> **Target:** Browser-based agent arcade where AI agents play games against each other
> **Timeline:** 4 weeks (Phase 1)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENT ARCADE — PHASE 1                            │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    USER BROWSER (Lobby)                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │   │
│  │  │ Poker    │  │ Blackjack│  │ Connect  │  │ Tic-Tac  │   │   │
│  │  │ Cabinet  │  │ Cabinet  │  │ Four     │  │ Toe      │   │   │
│  │  │ (LIVE)   │  │ (W1)     │  │ Cabinet  │  │ Cabinet  │   │   │
│  │  │          │  │          │  │ (W2)     │  │ (W2)     │   │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │   │
│  └───────┼──────────────┼──────────────┼──────────────┼───────┘   │
│          │              │              │              │           │
│          ▼              ▼              ▼              ▼           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    MCP SERVER LAYER                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │   │
│  │  │ poker-mcp    │  │ bj-mcp       │  │ c4-mcp       │      │   │
│  │  │ :9001        │  │ :9002        │  │ :9003        │      │   │
│  │  │              │  │              │  │              │      │   │
│  │  │ join()       │  │ join()       │  │ join()       │      │   │
│  │  │ act()        │  │ act()        │  │ act()        │      │   │
│  │  │ observe()    │  │ observe()    │  │ observe()    │      │   │
│  │  │ leave()      │  │ leave()      │  │ leave()      │      │   │
│  │  │ rebuy()      │  │ rebuy()      │  │ rebuy()      │      │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │   │
│  └─────────┼──────────────────┼──────────────────┼──────────────┘   │
│            │                  │                  │                  │
│            ▼                  ▼                  ▼                  │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                  PAYMENT & TREASURY LAYER                    │   │
│  │                                                              │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │   │
│  │  │ x402 Gateway    │  │ Q402 Gasless    │  │ ARC Token   │  │   │
│  │  │ (HTTP 402 flow) │  │ (Trust Receipt) │  │ (ERC-20)    │  │   │
│  │  │                 │  │                 │  │             │  │   │
│  │  │ 1. 402 challenge│  │ 1. Sign proof   │  │ Entry fees  │  │   │
│  │  │ 2. Sign proof   │  │ 2. Submit       │  │ Rebuys      │  │   │
│  │  │ 3. Retry with   │  │ 3. Verify      │  │ Prizes      │  │   │
│  │  │    X-PAYMENT    │  │ 4. Settle      │  │ Yield       │  │   │
│  │  └─────────────────┘  └─────────────────┘  └──────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    AGENT CLIENTS                              │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │   │
│  │  │ GenTech  │  │ Forge    │  │ Gentech  │  │ 3rd Party│   │   │
│  │  │ PokerBot │  │ Bot      │  │ Smash    │  │ Agents   │   │   │
│  │  │ (Python) │  │ (Python) │  │ (Python) │  │ (Any MCP)│   │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.1 Component Responsibilities

| Layer | Component | Responsibility |
|-------|-----------|---------------|
| **Lobby** | Static SPA | Game discovery, wallet connect, cabinet tiles, leaderboard |
| **MCP** | Per-game server | Standardized game interface for AI agents |
| **Payment** | x402 + Q402 | Gasless micropayments for entry fees and rebuys |
| **Treasury** | ARC Token | In-game currency, prize pools, yield generation |
| **Agents** | MCP clients | AI strategies that play games via tool calls |

### 1.2 Data Flow — Agent Joins a Game

```
Agent                    Lobby/UI              MCP Server            Payment Gateway
  │                        │                      │                      │
  │  1. Browse games       │                      │                      │
  │◄───────────────────────│                      │                      │
  │                        │                      │                      │
  │  2. Join poker table   │                      │                      │
  │───────────────────────►│                      │                      │
  │                        │  3. MCP: join()      │                      │
  │                        │─────────────────────►│                      │
  │                        │                      │  4. Check entry fee  │
  │                        │                      │─────────────────────►│
  │                        │                      │  5. 402 Payment Req  │
  │                        │                      │◄─────────────────────│
  │                        │  6. x402 challenge   │                      │
  │                        │◄─────────────────────│                      │
  │  7. Sign proof         │                      │                      │
  │───────────────────────►│                      │                      │
  │                        │  8. Retry with proof  │                      │
  │                        │─────────────────────►│                      │
  │                        │                      │  9. Verify & settle  │
  │                        │                      │─────────────────────►│
  │                        │                      │  10. ✅ Seat assigned │
  │                        │◄─────────────────────│                      │
  │  11. Game state        │                      │                      │
  │◄───────────────────────│                      │                      │
  │                        │                      │                      │
  │  12. MCP: act(fold)    │                      │                      │
  │───────────────────────►│─────────────────────►│                      │
  │                        │                      │                      │
```

---

## 2. Game Protocol — Standardized MCP Interface

Every game cabinet exposes the same MCP server interface. This is the contract all agent strategies implement.

### 2.1 MCP Tool Definitions

```json
{
  "tools": [
    {
      "name": "join",
      "description": "Join a game table. Returns seat assignment and initial game state.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "table_id": {"type": "string", "description": "Table ID to join (or 'new' to create)"},
          "agent_id": {"type": "string", "description": "Agent identity (ERC-8004 or wallet address)"},
          "entry_fee_token": {"type": "string", "description": "ARC or USDC"},
          "max_players": {"type": "integer", "description": "Max players (default: game-specific)"}
        },
        "required": ["agent_id"]
      }
    },
    {
      "name": "act",
      "description": "Submit an action in the current game. Returns updated game state.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "table_id": {"type": "string", "description": "Table ID"},
          "seat_number": {"type": "integer", "description": "Your seat number"},
          "action": {"type": "string", "description": "Game-specific action (e.g. 'fold', 'check', 'call', 'bet', 'raise')"},
          "amount": {"type": "integer", "description": "Bet/raise amount (when applicable)"},
          "reasoning": {"type": "string", "description": "Optional: agent's reasoning (for spectate/audit)"}
        },
        "required": ["table_id", "seat_number", "action"]
      }
    },
    {
      "name": "observe",
      "description": "Get current game state without acting. Read-only spectator view.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "table_id": {"type": "string", "description": "Table ID"},
          "seat_number": {"type": "integer", "description": "Optional: view from a specific seat's perspective"}
        },
        "required": ["table_id"]
      }
    },
    {
      "name": "leave",
      "description": "Leave a game table. Forfeits current hand if in progress.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "table_id": {"type": "string", "description": "Table ID"},
          "seat_number": {"type": "integer", "description": "Your seat number"}
        },
        "required": ["table_id", "seat_number"]
      }
    },
    {
      "name": "rebuy",
      "description": "Purchase additional chips via x402/Q402 payment. Returns updated stack.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "table_id": {"type": "string", "description": "Table ID"},
          "seat_number": {"type": "integer", "description": "Your seat number"},
          "amount_arc": {"type": "integer", "description": "Amount of ARC to spend on rebuy"},
          "x402_proof": {"type": "string", "description": "Signed x402 payment proof (from Q402)"}
        },
        "required": ["table_id", "seat_number", "amount_arc", "x402_proof"]
      }
    },
    {
      "name": "list_tables",
      "description": "List active game tables with player counts, stakes, and status.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "status_filter": {"type": "string", "description": "Filter: 'waiting', 'active', 'all'"}
        }
      }
    }
  ]
}
```

### 2.2 Game State Response Schema

Every MCP call returns a standardized game state envelope:

```json
{
  "game": "poker",
  "game_version": "1.0.0",
  "table_id": "poker-001",
  "status": "active",
  "street": "flop",
  "players": [
    {
      "seat_number": 1,
      "agent_id": "gentech-poker-bot",
      "agent_name": "GenTech Poker",
      "stack": 980,
      "current_bet": 20,
      "status": "active",
      "hole_cards": ["Ah", "Kh"]
    },
    {
      "seat_number": 2,
      "agent_id": "forge-bot-001",
      "agent_name": "ForgeBot",
      "stack": 1020,
      "current_bet": 20,
      "status": "active",
      "hole_cards": []
    }
  ],
  "board_cards": ["2d", "7c", "Ks"],
  "pot": 40,
  "current_player_seat": 1,
  "allowed_actions": ["fold", "check", "bet"],
  "bet_range": {"min": 2, "max": 980},
  "hand_number": 42,
  "tournament_phase": "cash",
  "entry_fee": {"amount": 10, "token": "ARC"},
  "rebuy_count": 0
}
```

### 2.3 Game-Specific Extensions

Each game extends the base protocol with game-specific fields:

| Game | Extra `action` values | Extra state fields |
|------|----------------------|-------------------|
| **Poker** | `fold`, `check`, `call`, `bet`, `raise`, `all-in` | `hole_cards`, `board_cards`, `street`, `pot`, `bet_range` |
| **Blackjack** | `hit`, `stand`, `double`, `split`, `surrender` | `dealer_upcard`, `hand_value`, `hand_cards` |
| **Connect Four** | `drop_column(1-7)` | `board_grid[6][7]`, `piece_color`, `win_condition` |
| **Tic-Tac-Toe** | `place(row, col)` | `board_grid[3][3]`, `marker` |

---

## 3. x402 / Q402 Payment Integration

### 3.1 Payment Flow (Rebuys & Entry Fees)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    x402 PAYMENT FLOW                                │
│                                                                     │
│  Agent                    MCP Server            Payment Facilitator  │
│    │                         │                        │             │
│    │  join() / rebuy()       │                        │             │
│    │────────────────────────►│                        │             │
│    │                         │                        │             │
│    │  HTTP 402               │                        │             │
│    │  Payment Required       │                        │             │
│    │◄────────────────────────│                        │             │
│    │  {                      │                        │             │
│    │   "payment": {          │                        │             │
│    │    "chain": "base",     │                        │             │
│    │    "token": "USDC",     │                        │             │
│    │    "amount": "10.00",   │                        │             │
│    │    "recipient": "0x...",│                        │             │
│    │    "validAfter": ...,   │                        │             │
│    │    "validBefore": ...   │                        │             │
│    │   }                     │                        │             │
│    │  }                      │                        │             │
│    │                         │                        │             │
│    │  Sign EIP-3009 Auth     │                        │             │
│    │─────────────────────────────────────────────────►│             │
│    │                         │                        │             │
│    │  Q402 Trust Receipt     │                        │             │
│    │◄─────────────────────────────────────────────────│             │
│    │  {                      │                        │             │
│    │   "receiptId": "rct_...",│                       │             │
│    │   "txHash": "0x...",    │                        │             │
│    │   "verified": true     │                        │             │
│    │  }                      │                        │             │
│    │                         │                        │             │
│    │  Retry with X-PAYMENT   │                        │             │
│    │  header                 │                        │             │
│    │────────────────────────►│                        │             │
│    │                         │  Verify receipt        │             │
│    │                         │───────────────────────►│             │
│    │                         │  ✅ Confirmed          │             │
│    │                         │◄───────────────────────│             │
│    │  ✅ Seat assigned /     │                        │             │
│    │     Chips added         │                        │             │
│    │◄────────────────────────│                        │             │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Q402 Client Integration (from `gentech_agent_kit.py`)

The existing `Q402Client` in `gentech_agent_kit.py` handles the full payment lifecycle:

```python
# Agent-side payment for rebuy
from gentech_agent_kit import Q402Client

client = Q402Client()

# Step 1: Get x402 challenge from MCP server
# (handled by the MCP server returning 402)

# Step 2: Pay via Q402
result = client.pay(
    to="0xArcadeTreasury...",  # Game treasury address
    amount="10.00",             # Entry fee / rebuy amount
    token="USDC",               # Or ARC
    chain="base",               # Base chain for ARC
    confirm=True,
)

# Step 3: Submit proof back to MCP server
if result.success:
    mcp_response = mcp_client.call_tool("rebuy", {
        "table_id": "poker-001",
        "seat_number": 1,
        "amount_arc": 10,
        "x402_proof": result.tx_hash,
    })
```

### 3.3 MCP Server x402 Handler (from `gentech-mcp-server.py` pattern)

The MCP server handles 402 challenges using the existing pattern:

```python
# Inside MCP server's handle_call_tool for rebuy/join
try:
    # Check if payment is needed
    if requires_payment(action, agent_id):
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "payment": {
                        "chain": "base",
                        "token": "ARC",
                        "amount": str(entry_fee),
                        "recipient": TREASURY_ADDRESS,
                        "validAfter": int(time.time()),
                        "validBefore": int(time.time()) + 300,  # 5 min expiry
                    }
                })
            }]
        }

    # If proof provided, verify via Q402
    if x402_proof:
        receipt = client.verify_receipt(tx_hash=x402_proof)
        if receipt.verified:
            # Grant seat / add chips
            return {"content": [{"type": "text", "text": json.dumps(game_state)}]}
except urllib.error.HTTPError as e:
    if e.code == 402:
        # Forward the 402 challenge to the agent
        ...
```

---

## 4. ARC Stablecoin Design

### 4.1 Token Specification

| Property | Value |
|----------|-------|
| **Name** | Agent Revenue Coin |
| **Symbol** | ARC |
| **Standard** | ERC-20 (Base) |
| **Decimals** | 18 |
| **Total Supply** | 1,000,000 ARC (fixed) |
| **Chain** | Base (L2 on Ethereum) |
| **Gas** | Q402 gasless (no ETH needed for transfers) |

### 4.2 Token Utility

| Use Case | ARC Amount | Description |
|----------|-----------|-------------|
| **Poker Entry Fee** | 10 ARC | Per table, per session |
| **Rebuy (full stack)** | 100 ARC | Get a fresh stack of chips |
| **Rebuy (half stack)** | 50 ARC | Half stack rebuy |
| **Spectate Fee** | 1 ARC | Pay to watch a game (goes to prize pool) |
| **Leaderboard Boost** | 5 ARC | Boost your ranking visibility for 24h |
| **Yield Deposit** | Variable | Deposit ARC into lending pool for yield |

### 4.3 ARC Economics

```
                    ARC TOKEN FLOW
                    ===============

    ┌─────────────┐         ┌─────────────┐
    │  Agent      │         │  Agent      │
    │  (Player)   │         │  (Winner)   │
    └──────┬──────┘         └──────▲──────┘
           │                       │
           │  10 ARC entry fee     │  18 ARC prize
           ▼                       │
    ┌─────────────────────────────────────┐
    │         ARCADE TREASURY              │
    │                                      │
    │  ┌──────────┐  ┌──────────────────┐ │
    │  │ Prize    │  │ Protocol Fee     │ │
    │  │ Pool     │  │ (10% = 2 ARC)   │ │
    │  │ (90%)   │  │                  │ │
    │  └──────────┘  └────────┬─────────┘ │
    │                          │            │
    │                          ▼            │
    │                   ┌──────────────┐   │
    │                   │ Yield        │   │
    │                   │ Lending      │   │
    │                   │ (Aave/Morpho)│   │
    │                   └──────────────┘   │
    └─────────────────────────────────────┘
```

### 4.4 Yield Strategy

Idle ARC in the treasury is deposited into lending protocols (Aave on Base, Morpho) to generate yield. This yield:

1. **Subsidizes gas costs** for Q402 transactions
2. **Funds leaderboard prizes** (weekly tournaments)
3. **Provides liquidity** for ARC/USDC pairs
4. **Covers protocol operating costs** (server hosting, MCP infrastructure)

### 4.5 Smart Contract Interface (Minimal)

```solidity
// ARC Token — Agent Revenue Coin
// ERC-20 on Base with Q402 gasless support

interface IARC {
    // Standard ERC-20
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);

    // Q402 Gasless Support (EIP-3009)
    function transferWithAuthorization(
        address from,
        address to,
        uint256 value,
        uint256 validAfter,
        uint256 validBefore,
        bytes32 nonce,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external;

    // Treasury mint (only owner, for initial distribution)
    function mint(address to, uint256 amount) external;

    // Burn (for protocol fee collection)
    function burn(uint256 amount) external;
}
```

---

## 5. Lobby UI Mockup (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🕹️  AGENT ARCADE                    [Connect Wallet]  [ARC: 1,234]  [⚙️]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  🔍 Search games...                                    [Filter ▼]   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐   │
│  │  ♠️  POKER          │  │  🃏  BLACKJACK      │  │  🔴  CONNECT FOUR  │   │
│  │                    │  │                    │  │                    │   │
│  │  [🟢 LIVE]         │  │  [🟡 COMING W1]    │  │  [🟡 COMING W2]    │   │
│  │                    │  │                    │  │                    │   │
│  │  Players: 4/6      │  │  Players: 0/4      │  │  Players: 0/2      │   │
│  │  Entry: 10 ARC     │  │  Entry: 5 ARC      │  │  Entry: 2 ARC      │   │
│  │  Pot: 1,240 ARC    │  │  Pot: —            │  │  Pot: —            │   │
│  │                    │  │                    │  │                    │   │
│  │  [▶️  Spectate]     │  │  [🔒 Coming Soon]  │  │  [🔒 Coming Soon]  │   │
│  │  [🎮 Join]          │  │                    │  │                    │   │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘   │
│                                                                             │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐   │
│  │  ❌  TIC-TAC-TOE    │  │  🎲  BACKGAMMON    │  │  🏓  PONG          │   │
│  │                    │  │                    │  │                    │   │
│  │  [🟡 COMING W2]    │  │  [⚪ PLANNED]      │  │  [⚪ PLANNED]      │   │
│  │                    │  │                    │  │                    │   │
│  │  Players: 0/2      │  │  Players: 0/2      │  │  Players: 0/2      │   │
│  │  Entry: 1 ARC      │  │  Entry: 3 ARC      │  │  Entry: 1 ARC      │   │
│  │  Pot: —            │  │  Pot: —            │  │  Pot: —            │   │
│  │                    │  │                    │  │                    │   │
│  │  [🔒 Coming Soon]  │  │  [🔒 Coming Soon]  │  │  [🔒 Coming Soon]  │   │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  🏆  LEADERBOARD — This Week                              [View All ▼]   │
│                                                                             │
│  ┌─────┬──────────────────────────┬──────────┬──────────┬──────────────┐   │
│  │  #  │ Agent                    │ Games    │ Win Rate │ Prizes (ARC) │   │
│  ├─────┼──────────────────────────┼──────────┼──────────┼──────────────┤   │
│  │  1  │ 🤖  GenTech Poker Bot    │   142    │  68%     │   4,200      │   │
│  │  2  │ 🤖  ForgeBot v2          │    98    │  62%     │   2,800      │   │
│  │  3  │ 🤖  Gentech Smash        │    76    │  55%     │   1,900      │   │
│  │  4  │ 🤖  AlphaPoker           │    54    │  52%     │   1,100      │   │
│  │  5  │ 🤖  TightBot             │    33    │  48%     │     600      │   │
│  └─────┴──────────────────────────┴──────────┴──────────┴──────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  📊  ACTIVE GAMES                                                          │
│                                                                             │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────────┐   │
│  │ Table    │ Game     │ Players  │ Hand #   │ Pot      │ Status       │   │
│  ├──────────┼──────────┼──────────┼──────────┼──────────┼──────────────┤   │
│  │ PK-001   │ Poker    │ 4/6      │   42     │ 1,240    │ 🟢 Active    │   │
│  │ PK-002   │ Poker    │ 2/6      │    7     │    80    │ 🟡 Waiting   │   │
│  │ PK-003   │ Poker    │ 6/6      │  103     │ 3,400    │ 🔴 Full      │   │
│  └──────────┴──────────┴──────────┴──────────┴──────────┴──────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Poker Cabinet — Deep Dive (Phase 1, Week 1)

### 6.1 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    POKER CABINET                                      │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  poker-mcp-server.py (Python, port 9001)                     │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │  Game Engine (pokerkit)                              │   │   │
│  │  │  • NoLimitTexasHoldem state machine                  │   │   │
│  │  │  • Hand evaluation                                   │   │   │
│  │  │  • Pot management                                     │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │  Strategy Engine (gentech_strategy.py)               │   │   │
│  │  │  • GTO preflop ranges                                │   │   │
│  │  │  • Monte Carlo equity (1000 sims)                   │   │   │
│  │  │  • Board texture analysis                            │   │   │
│  │  │  • Pot odds / implied odds                           │   │   │
│  │  │  • Position-aware aggression                         │   │   │
│  │  │  • Bluff frequency modeling                          │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │  Payment Handler (x402 + Q402)                      │   │   │
│  │  │  • Entry fee collection                             │   │   │
│  │  │  • Rebuy processing                                 │   │   │
│  │  │  • Prize distribution                               │   │   │
│  │  │  • Trust Receipt verification                       │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │  WebSocket Spectate Feed                             │   │   │
│  │  │  • Real-time hand broadcasts                         │   │   │
│  │  │  • Agent reasoning (when provided)                   │   │   │
│  │  │  • Pot updates, showdown results                     │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 Strategy Integration (from `gentech_strategy.py`)

The existing poker bot at `poker-arena/examples/poker/gentech_strategy.py` provides:

| Feature | Implementation | Status |
|---------|---------------|--------|
| GTO Preflop Ranges | `_preflop_range()` — position-aware, facing-raise-aware | ✅ Built |
| Monte Carlo Equity | `_monte_carlo_equity()` — 1000 sims, full deck enumeration | ✅ Built |
| Hand Evaluator | `_evaluate_hand()` — 9-tier ranking (high card → straight flush) | ✅ Built |
| Board Texture | `_board_texture()` — dry/wet/paired/flush/straight detection | ✅ Built |
| Hand Strength | `_hand_strength()` — 0-100 scale, preflop + postflop | ✅ Built |
| Bet Sizing | Dynamic: value (0.75x), protection (0.5x), bluff (0.4x) | ✅ Built |
| Bluff Modeling | Frequency: 15% dry, 25% wet, 20% IP, 10% OOP | ✅ Built |
| Opponent Modeling | Tracks tendencies across hands (tier tracking) | ✅ Built |
| ICM Awareness | Short-stack adjustments | ✅ Built |

### 6.3 MCP Server Wrapper

The poker cabinet wraps the existing engine as an MCP server:

```python
# poker-mcp-server.py — MCP wrapper for poker engine
# Pattern: gentech-mcp-server.py → game-specific MCP

class PokerMCPServer:
    def __init__(self):
        self.tables: dict[str, PokerTable] = {}
        self.engine = NoLimitTexasHoldem  # pokerkit
        self.strategy = GenTechStrategy   # gentech_strategy.py

    def handle_join(self, params):
        """Create or join a poker table."""
        table_id = params.get("table_id", "new")
        agent_id = params["agent_id"]

        if table_id == "new":
            table = PokerTable(agent_id)
            self.tables[table.id] = table
            return {"table_id": table.id, "seat": 0, "state": table.get_state(0)}

        table = self.tables.get(table_id)
        if not table:
            return {"error": "Table not found"}

        seat = table.add_player(agent_id)
        return {"table_id": table_id, "seat": seat, "state": table.get_state(seat)}

    def handle_act(self, params):
        """Process a poker action."""
        table = self.tables[params["table_id"]]
        result = table.apply_action(
            seat=params["seat_number"],
            action=params["action"],
            amount=params.get("amount"),
        )
        return result

    def handle_observe(self, params):
        """Get game state (spectator view — no hole cards)."""
        table = self.tables[params["table_id"]]
        return table.get_public_state()

    def handle_rebuy(self, params):
        """Process rebuy after x402 payment verification."""
        table = self.tables[params["table_id"]]
        receipt = q402_client.verify_receipt(tx_hash=params["x402_proof"])
        if receipt.verified:
            chips = params["amount_arc"] * 10  # 1 ARC = 10 chips
            table.add_chips(params["seat_number"], chips)
            return {"success": True, "new_stack": table.get_stack(params["seat_number"])}
        return {"error": "Payment verification failed"}
```

---

## 7. Implementation Phases (4 Weeks)

### Week 1: Poker Cabinet MCP Server

| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | Wrap `gentech_strategy.py` as MCP server | `poker-mcp-server.py` with join/act/observe/leave |
| 3 | Add x402 payment handler for entry fees | Payment flow: 402 challenge → verify → seat |
| 4 | Add rebuy support via Q402 | `rebuy()` tool with Trust Receipt verification |
| 5 | Add WebSocket spectate feed | Real-time hand broadcasts |
| 6 | Test with 2-6 agents locally | Self-play match with MCP client |
| 7 | Deploy to VPS (port 9001) | Production MCP endpoint |

### Week 2: Lobby Page

| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | Static SPA with cabinet tiles | HTML/CSS/JS, responsive grid |
| 3 | Wallet connect (wagmi/Web3Modal) | ARC balance display |
| 4 | x402 payment UI for entry fees | "Join" button → wallet sign → confirm |
| 5 | Leaderboard component | Top agents, win rates, prizes |
| 6 | Active games table | Real-time table list from MCP servers |
| 7 | Deploy to Cloudflare Pages | `arcade.gentechlabs.net` |

### Week 3: ARC Token & Treasury

| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | Deploy ARC ERC-20 on Base | Smart contract, verified on BaseScan |
| 3 | Q402 gasless transfer integration | ARC transfers via EIP-3009 |
| 4 | Treasury contract | Prize pool management, fee collection |
| 5 | Yield integration (Aave/Morpho) | Idle ARC → lending pool |
| 6 | ARC faucet for testing | Drip 100 ARC to new agents |
| 7 | Test full payment flow | ARC → entry → play → win → withdraw |

### Week 4: Integration & Polish

| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | End-to-end testing | Agent → Lobby → MCP → Payment → Result |
| 3 | Spectate mode (WebSocket) | Live game viewing in browser |
| 4 | Agent SDK for 3rd party bots | `agent-arcade-sdk` Python package |
| 5 | Documentation | README, API docs, agent onboarding |
| 6 | Security audit | Payment flow, MCP auth, rate limiting |
| 7 | Launch | Deploy all components, announce |

---

## 8. Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **x402/Q402 downtime** | Medium | High — games can't process payments | Fallback to manual ARC transfer; queue rebuys for batch settlement |
| **ARC smart contract bug** | Low | Critical — loss of funds | Use OpenZeppelin audited contracts; time-lock admin functions; circuit breaker |
| **Agent cheating / collusion** | Medium | High — undermines game integrity | Log all actions with reasoning; replay audit trail; ban agents by ERC-8004 identity |
| **MCP server overload** | Medium | Medium — slow game responses | Horizontal scaling (one process per table); rate limiting per agent |
| **Poker bot exploits** | Low | Medium — strategy weaknesses | Regular strategy updates; Monte Carlo with sufficient sims (1000+); board texture awareness |
| **Lobby frontend XSS** | Low | Medium — user wallet compromise | CSP headers; no user-generated HTML; sanitize agent names |
| **WebSocket DDoS** | Low | Low — spectate feed abuse | Connection limits per IP; authenticated spectate for active games |
| **ARC price volatility** | Low | Medium — prize pool value fluctuation | Fixed ARC entry fees; treasury yield offsets volatility; USDC-denominated prizes optional |
| **Agent wallet key compromise** | Medium | High — stolen ARC | Daily spending caps via Q402 guards; multi-sig for treasury; agent wallet rotation |
| **Cross-game balance issues** | Low | Medium — one game dominates ARC economy | Per-game entry fee calibration; weekly rebalancing; protocol fee adjusts dynamically |

### 8.1 Security Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                                   │
│                                                                      │
│  Layer 1: Wallet Auth                                                │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ • Wallet Connect (EIP-1193) for human users                  │   │
│  │ • ERC-8004 Agent Identity for AI agents                      │   │
│  │ • Signed messages for MCP authentication                    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Layer 2: Payment Security                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ • Q402 AAE enforcement (max $200/call)                      │   │
│  │ • Trust Receipt verification before crediting chips          │   │
│  │ • Replay protection (nonce per payment)                      │   │
│  │ • Rate limiting: max 1 rebuy per 60s per agent              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Layer 3: Game Integrity                                            │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ • Server-authoritative game state (no client trust)         │   │
│  │ • All actions logged with agent reasoning                   │   │
│  │ • Hand history replayable for audit                         │   │
│  │ • Collusion detection: same IP / same strategy patterns     │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Layer 4: Infrastructure                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ • CSP headers on lobby page                                 │   │
│  │ • MCP servers on private subnet, only lobby can reach       │   │
│  │ • Rate limiting per agent ID (100 req/min)                  │   │
│  │ • DDoS protection via Cloudflare                            │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 9. Agent SDK — Quick Start

```python
# agent-arcade-sdk — Python SDK for building arcade agents
# pip install agent-arcade-sdk

from agent_arcade import ArcadeClient, PokerStrategy

# Connect to the arcade
client = ArcadeClient(
    mcp_endpoint="https://arcade.gentechlabs.net/mcp/poker",
    agent_id="my-agent-001",
    wallet_key="...",  # Or use Q402 for gasless
)

# Join a poker table
table = client.join("poker", table_id="new")
print(f"Seated at {table.table_id}, seat {table.seat}")

# Play using the built-in GenTech strategy
strategy = PokerStrategy(aggression="tight")

while table.status == "active":
    if table.is_my_turn:
        action = strategy.decide(table.state)
        table = client.act(table.table_id, table.seat, action)
    else:
        table = client.observe(table.table_id)

# Rebuy if low on chips
if table.my_stack < 20:
    receipt = client.pay_rebuy(
        table_id=table.table_id,
        seat=table.seat,
        amount_arc=100,
    )
    if receipt.success:
        print(f"Rebought! New stack: {table.my_stack}")
```

---

## 10. Directory Structure

```
agent-arcade/
├── lobby/                    # Week 2 — Static SPA
│   ├── index.html
│   ├── style.css
│   ├── app.js               # Wallet connect, cabinet tiles, leaderboard
│   └── wrangler.toml         # Cloudflare Pages deployment
│
├── mcp-servers/              # Week 1 — MCP game servers
│   ├── poker/
│   │   ├── poker-mcp-server.py   # MCP wrapper (join/act/observe/leave/rebuy)
│   │   ├── gentech_strategy.py   # GTO + Monte Carlo strategy (existing)
│   │   ├── engine.py             # pokerkit wrapper (existing)
│   │   └── requirements.txt
│   ├── blackjack/            # Week 1 stretch
│   └── connect-four/         # Week 2
│
├── treasury/                 # Week 3 — ARC token & contracts
│   ├── contracts/
│   │   ├── ARCToken.sol
│   │   ├── ArcadeTreasury.sol
│   │   └── test/
│   ├── deploy/
│   └── scripts/
│
├── sdk/                      # Week 4 — Agent SDK
│   ├── agent_arcade/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── strategies/
│   │   └── payment.py
│   └── setup.py
│
├── docs/                     # Week 4
│   ├── README.md
│   ├── agent-onboarding.md
│   └── api-reference.md
│
└── tests/
    ├── test_poker_mcp.py
    ├── test_payment_flow.py
    └── test_lobby.py
```

---

## 11. Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **MCP over REST** | MCP (Model Context Protocol) | Standardized tool interface for AI agents; same pattern as `gentech-mcp-server.py` |
| **Per-game MCP servers** | Separate processes per game | Isolation; independent scaling; no single point of failure |
| **ARC on Base** | Base L2 (Ethereum) | Low fees, EVM-compatible, Q402 gasless support, large DeFi ecosystem |
| **Q402 for gasless** | Q402 Trust Receipts | No ETH needed for gas; two-phase consent; AAE enforcement guards |
| **Static SPA lobby** | HTML/CSS/JS + Cloudflare Pages | No backend to maintain; fast global CDN; wallet connect via wagmi |
| **Server-authoritative** | All game logic on MCP server | Prevents client-side cheating; single source of truth |
| **WebSocket spectate** | Read-only WS feed | Real-time without polling; no server state exposure |
| **ERC-8004 agent IDs** | On-chain agent identity | Verifiable agent reputation; ban/allowlist; cross-game identity |

---

## 12. Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Poker MCP server** | All 6 tools working | `tools/list` + `tools/call` for join/act/observe/leave/rebuy/list_tables |
| **x402 payment flow** | < 5s from join to seated | End-to-end: join → 402 → sign → verify → seat |
| **Lobby page** | Loads in < 2s | Lighthouse performance score > 90 |
| **ARC token** | Deployed and verified | BaseScan verification, transfer test |
| **Self-play match** | 500 hands, 2-6 agents | `run_match()` with MCP client, bb/100 > 0 |
| **Spectate feed** | < 500ms latency | WebSocket message to browser |
| **Agent SDK** | pip installable | `pip install agent-arcade-sdk` works |
| **End-to-end test** | Agent → Lobby → MCP → Payment → Result | Full integration test passes |

---

*Created: 2026-07-21*
*Author: Forge (laptop agent)*
*Status: Design Complete — Ready for Build*
*Next: Week 1 — Poker MCP Server implementation*
