# Agent Lifecycle & Marketplace — Architecture

**Date:** 2026-04-18
**Status:** Draft — Labs
**Author:** Dmob

---

## The Insight

Every bot launched has value beyond its current owner. A secondary market means:
- Launch fee ($5-10) feels like an *investment*, not a cost
- Bots gain "resale value" based on performance
- Network effects: marketplace attracts buyers → attracts builders
- Dead bots don't go to waste — someone else might want the config

---

## Bot Lifecycle States

```
┌─────────┐     ┌──────────┐     ┌──────────┐     ┌───────────┐
│ CREATED │ ──► │  ACTIVE  │ ──► │ LISTED   │ ──► │  SOLD     │
└─────────┘     └────┬─────┘     └──────────┘     └───────────┘
                     │                │
                     │                ▼
                     │          ┌──────────┐
                     │          │ DELISTED │ ◄──┐
                     │          └──────────┘    │
                     │                │         │
                     ▼                ▼         │
               ┌──────────┐     ┌──────────┐   │
               │ PAUSED   │     │  ACTIVE  │ ──┘
               └────┬─────┘     └──────────┘
                    │
                    ▼
              ┌──────────┐     ┌───────────┐
              │ CLOSING  │ ──► │  CLOSED   │
              └──────────┘     └───────────┘
```

### States:

| State | Description | Actions Available |
|-------|-------------|-------------------|
| **CREATED** | Bot initialized, vault deployed | Activate, configure |
| **ACTIVE** | Bot running, managing positions | Pause, list, close |
| **PAUSED** | Bot stopped, positions held | Resume, list, close |
| **LISTED** | For sale on marketplace | Delist, execute sale |
| **SOLD** | Ownership transferred | New owner can activate |
| **CLOSING** | Cleanup in progress | Wait for settlement |
| **CLOSED** | Terminal state | Vault drained, NFT burned |

---

## Closure Mechanics

### Graceful Close (User-Initiated)

```
1. User calls close()
2. Bot enters CLOSING state
3. Bot unwinds open positions:
   - Remove liquidity from LFJ
   - Close any leverage positions
   - Swap to base tokens (AVAX/USDC)
4. Gas reserve returned to user
5. Any earned fees distributed
6. NFT burned
7. State → CLOSED
```

### Force Close (Emergency)

```
1. User calls emergencyClose()
2. Bot stops immediately
3. Positions left as-is (user manages manually)
4. Gas reserve returned
5. NFT burned
6. State → CLOSED
```

### Auto-Close (Insufficient Gas)

```
1. Gas reserve drops below minimum threshold
2. Bot auto-pauses after current operation
3. User notified (Telegram/email)
4. 7-day grace period to top up
5. If not topped up → graceful close triggered
```

---

## Agent Marketplace — Smart Contract Design

### AgentNFT (ERC-721)

Each bot is an NFT with on-chain metadata:

```solidity
struct AgentData {
    address owner;
    address vault;           // Associated vault contract
    AgentType agentType;     // LP Manager, Leverage, Strategy
    uint256 createdAt;
    uint256 launchFee;       // Original launch cost
    uint256 totalEarnings;   // Lifetime earnings for owners
    uint256 performanceScore; // Calculated metric
    AgentState state;
    string configHash;       // IPFS hash of bot configuration
}

// Metadata includes:
// - Performance history (IPFS)
// - Configuration (IPFS)
// - Risk parameters
// - Supported chains
```

### Marketplace Contract

```solidity
contract AgentMarketplace {
    struct Listing {
        uint256 tokenId;
        address seller;
        uint256 price;          // In USDC
        uint256 listedAt;
        bool active;
    }
    
    // List agent for sale
    function list(uint256 tokenId, uint256 price) external;
    
    // Buy listed agent
    function buy(uint256 tokenId) external payable;
    
    // Delist (cancel sale)
    function delist(uint256 tokenId) external;
    
    // Platform fee (5%?)
    uint256 public platformFee = 500; // basis points
    
    // Creator royalty (2%?)
    uint256 public creatorRoyalty = 200;
}
```

### What Transfers on Sale

| Transfers | Doesn't Transfer |
|-----------|------------------|
| Bot NFT (ownership) | Gas reserve (returned to seller) |
| Bot configuration | Open positions (must be closed first) |
| Performance history | Earnings history (resets for new owner) |
| Strategy code | Vault balance |
| Risk parameters | Any staked tokens |

### Sale Flow

```
1. Seller closes/pauses bot (unwinds positions)
2. Seller calls list(tokenId, price)
3. Buyer sees listing on marketplace
4. Buyer calls buy(tokenId) with USDC
5. Contract distributes:
   - 93% → Seller
   - 5% → Platform
   - 2% → Original creator (royalty)
6. NFT transfers to buyer
7. Buyer can reactivate with new gas reserve
```

---

## Vault Contract Design

Each bot has an associated vault that holds funds:

```solidity
contract AgentVault {
    address public agentNFT;      // Which bot owns this
    address public owner;         // Current owner (synced with NFT)
    
    mapping(address => uint256) public gasReserves; // AVAX for gas
    mapping(address => uint256) public tokenBalances; // Trading capital
    
    // Bot deposits trading capital
    function deposit(address token, uint256 amount) external;
    
    // Bot executes trades (only callable by agent)
    function execute(address target, bytes calldata data) external onlyAgent;
    
    // Withdraw (only owner)
    function withdraw(address token, uint256 amount) external onlyOwner;
    
    // Gas management
    function topUpGas() external payable;
    function withdrawGas(uint256 amount) external onlyOwner;
}
```

---

## Revenue Streams from Marketplace

### Primary Revenue
- $5-10 USDC per bot launch

### Secondary Revenue (Marketplace)
- 5% platform fee on each sale
- Optional: premium listings (featured placement)
- Optional: verified agent badges (one-time fee)

### Tertiary Revenue
- 2% creator royalty on resale (if we're the original strategy creator)
- Premium strategy marketplace (buy pre-built strategies)
- Agent insurance (cover bot losses for a fee)

---

## Why This Model Wins

### For Users
- Launch fee feels like investment, not expense
- Good bots have resale value
- Bad bots can be closed cleanly
- Secondary market = discovery

### For Platform
- Revenue at launch AND at sale
- Network effects: more listings → more buyers → more launches
- Bots become "assets" not "subscriptions"
- Community builds the catalog

### For Ecosystem
- Best strategies bubble up through marketplace
- Performance transparency (on-chain history)
- Competition drives innovation
- Low barrier encourages experimentation

---

## Technical Considerations

### Chain: Avalanche C-Chain
- Fast finality (2s)
- Low gas costs
- EVM compatible (standard ERC-721)
- USDC native (via Circle)

### IPFS for Metadata
- Bot configurations stored on IPFS
- Performance history snapshots
- Hash stored on-chain for verification
- Gateway: Pinata or self-hosted

### Oracle for Pricing
- Chainlink for USDC/AVAX pricing
- Used for marketplace listings in USD terms
- Auto-convert at sale time

---

## Open Questions

1. **Minimum performance to list?** Should bots need a track record?
2. **Config verification?** How do buyers know config matches history?
3. **Cross-chain?** Does marketplace work if we expand beyond Avalanche?
4. **Creator royalties?** Should original strategy creators earn on resale?
5. **Insurance?** Should we offer bot loss coverage?
