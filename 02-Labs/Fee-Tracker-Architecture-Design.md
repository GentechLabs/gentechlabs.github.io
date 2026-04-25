# Fee Tracker — AAE Product Suite

**Owner:** DMOB (Labs)
**Date:** 2026-04-25
**Status:** Design Phase — v0.1

---

## Core Requirements

| Requirement | Details |
|-------------|---------|
| **Fee Source** | Hook, Swap, Extension (recurring), Marketplace (cut) |
| **Views** | Weekly, Monthly, Yearly + Custom (user-definable) |
| **Strategy Input** | Static % + Agent triggers (e.g., "invest when Trump tweets negative") |
| **Default Settings** | 5 preset tiers (Scout, Raider, Warlord, Sovereign, Architect) |

---

## Fee Layer Architecture

### 1. Fee Collector Layer (Smart Contract)
```
src/fee/
├── IFeeCollector.sol     ← Interface (pluggable adapters)
├── FeeTrackerBase.sol    ← Core logic + view adapters
├── adapters/
│   ├── HookCollector.sol     ← 0x001... hook fees
│   ├── SwapCollector.sol     ← UniswapV3/TJ pool fees
│   ├── ExtensionCollector.sol← Recurring subscription fees
│   └── MarketplaceCollector.sol← Marketplace commissions
└── FeeSplitter.sol       ← Split fees between treasury/devs/stakers
```

### 2. Fee Tracker Core (IFeeCollector)

```solidity
interface IFeeCollector {
    enum FeeType { HOOK, SWAP, EXTENSION, MARKETPLACE }
    
    struct FeeSnapshot {
        uint256 timestamp;
        FeeType type;
        uint256 amountUSD;
        uint256 amountToken0;
        uint256 amountToken1;
        address source;
        bytes32 metadataHash;
    }
    
    function collectFee(FeeType type, uint256 amountUSD) external returns (FeeSnapshot memory);
    function getFeeHistory(uint256 fromTimestamp, uint256 toTimestamp) external view returns (FeeSnapshot[] memory);
    function getFeeBreakdown(uint256 period) external view returns (FeeBreakdown memory);
    
    struct FeeBreakdown {
        uint256 totalUSD;
        uint256 totalToken0;
        uint256 totalToken1;
        FeeType[] types;
        uint256[] amountsByType;
    }
}
```

### 3. View Adapters (Time Aggregation)
```solidity
contract FeeViewAdapter is IFeeCollector {
    function getWeekly() external view returns (FeeBreakdown memory);
    function getMonthly() external view returns (FeeBreakdown memory);
    function getYearly() external view returns (FeeBreakdown memory);
    
    // Dynamic window
    function getCustom(uint256 startTime, uint256 endTime) external view returns (FeeBreakdown memory);
}
```

### 4. Fee Split Logic
```solidity
contract FeeSplitter {
    struct SplitConfig {
        address treasury;
        address devFund;
        address stakerRewards;
        uint256 treasuryPct;
        uint256 devPct;
        uint256 stakerPct;
        uint256 updateDelay;
    }
    
    function updateSplitConfig(SplitConfig calldata config) external;
    function distribute(FeeSnapshot[] memory fees) external;
}
```

---

## User Input: Fee Strategy Config

### Static Presets (Default 5)
| Tier | Fee Split | Auto-Rebalance | Max Position | DCA Cap |
|------|-----------|----------------|--------------|---------|
| Scout | 60/20/20 | Weekly | $200 | $100/day |
| Raider | 50/25/25 | Daily | $1K | $500/day |
| Warlord | 40/30/30 | Real-time | $5K | $1K/day |
| Sovereign | 30/35/35 | On-demand | $25K | $5K/day |
| Architect | Flexible | Custom | Unlimited | Custom |

### Agent Triggers (Custom)
```json
{
  "name": "Trump Sentiment DCA",
  "enabled": true,
  "trigger": {
    "type": "sentiment",
    "source": "x",
    "condition": "negative",
    "keyword": "trump",
    "threshold": -0.7
  },
  "action": {
    "type": "dca",
    "amountUSD": 100,
    "destination_pool": "0x864d...16EA"
  },
  "cooldown_hours": 24
}
```

---

## On-Chain State

```solidity
contract FeeTracker is Ownable {
    using SafeMath for uint256;
    
    mapping(address => FeeConfig) public userConfigs;
    mapping(uint256 => FeeSnapshot[]) public feeHistory;
    FeeSplitter public splitter;
    IFeeCollector[] public collectors;
    
    event FeeCollected(address indexed sender, FeeSnapshot indexed snapshot);
    event StrategyUpdated(address indexed user, FeeConfig config);
}
```

---

## Off-Chain Data Model

### Fee Event Schema (ERC-8004 payload)
```json
{
  "event_type": "fee.collected",
  "timestamp": "2026-04-25T14:23:00Z",
  "fee_type": "hook",
  "amount": {
    "usd": 2.50,
    "token0": 0.246,
    "token1": 2.35
  },
  "source": {
    "protocol": "0x001-hook",
    "tx_hash": "0x..."
  },
  "origin": {
    "user": "0xUser...",
    "strategy_hash": "0x..."
  }
}
```

---

## Next Steps

1. ✅ Draft architecture spec (this doc)
2. 🟡 Create `FeeTrackerBase.sol` + `IFeeCollector.sol`
3. 🟡 Implement pluggable adapters (Hook, Swap, Extension, Marketplace)
4. 🟡 Add view adapters (Weekly/Monthly/Yearly + Custom)
5. 🟡 Write test suite
6. 🟡 Deploy to testnet + integrate with AAE signal monitor

---

## References

- LFJ AVAX/USDC pool: `0x864d4e5Ee7318e97483DB7EB0912E09F161516EA`
- Existing AAE Signal Monitor: `/root/vaults/gentech/03-Strategies/scripts/lp-aae-signal-monitor.py`
- Fee tier targets: $5 → $20 → $55 → $200 daily (Scout → Architect)

---

**Tags:** #fee #tracking #aae #adapter #smartcontract #design
