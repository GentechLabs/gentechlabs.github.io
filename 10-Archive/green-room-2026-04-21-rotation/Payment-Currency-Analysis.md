# Payment Currency Analysis — USDC vs $TECH for Agent Launches
## 🔧 Dmob's Technical + Economic Analysis
*April 19, 2026*

---

## The Question
Should users pay per agent launch in:
- **Option A:** USDC (stablecoin)
- **Option B:** $TECH (protocol token)
- **Option C:** Hybrid (pay USDC, protocol converts to $TECH)

---

## Analysis by Protocol Pattern

### What GMX Does
- **Users pay fees in:** The asset they're trading (ETH, USDC, BTC, etc.)
- **Fee distribution:** 70% to stakers in the SAME asset they paid + esGMX
- **Result:** Stakers earn stablecoins AND volatile assets — diversified real yield
- **Key insight:** GMX doesn't force users to buy GMX to use the platform

### What Aave Does
- **Borrowers pay interest in:** The asset they borrowed (USDC interest paid in USDC, ETH interest in ETH)
- **Protocol revenue:** Accumulates in the lent assets
- **Stakers earn:** From safety module, backed by protocol revenue in those assets
- **Key insight:** No token forced into payment flow — revenue naturally accumulates in useful assets

### What Velodrome Does
- **Users pay trading fees in:** The tokens being swapped
- **Fee distribution:** To veVELO voters in the traded tokens
- **Bribes:** Paid in whatever token the protocol wants to incentivize
- **Key insight:** Accepts any token, distributes to stakers in kind

---

## Option A: Pay in USDC Only
### Pros
- ✅ Lowest friction — everyone has stablecoins
- ✅ Predictable pricing for users ($5 per launch, always)
- ✅ No token volatility risk for users
- ✅ Easy to market: "Pay $5 to launch an agent"
- ✅ Stakers earn stablecoin yield (more valuable than volatile token)

### Cons
- ❌ No direct buy pressure on $TECH from usage
- ❌ Need separate mechanism to create $TECH demand
- ❌ Protocol holds USDC, not aligned with token ecosystem

### Contract Implementation
```solidity
function launchAgent(address agent, bytes calldata input) external payable {
    uint256 fee = agent.getLaunchFee(); // in USDC
    IERC20(usdc).transferFrom(msg.sender, feeRouter, fee);
    feeRouter.distributeFees(fee);
    agent.execute(input);
}
```

---

## Option B: Pay in $TECH Only
### Pros
- ✅ Direct buy pressure — users MUST buy $TECH to use platform
- ✅ Deflationary if fees are burned
- ✅ Strong token utility narrative
- ✅ Stakers earn $TECH (aligns with token holders)

### Cons
- ❌ High friction — users must acquire $TECH first (DEX swap)
- ❌ Price volatility makes pricing unpredictable
- ❌ "Gas token" problem: token pumps → platform becomes expensive
- ❌ Tax implications: every $TECH spend is a taxable event
- ❌ Death spiral risk: token drops → fewer users → less revenue → token drops more

### Contract Implementation
```solidity
function launchAgent(address agent, bytes calldata input) external {
    uint256 fee = agent.getLaunchFeeInTECH();
    IERC20(tech).transferFrom(msg.sender, feeRouter, fee);
    feeRouter.distributeFees(fee); // Burns % or distributes to stakers
    agent.execute(input);
}
```

---

## Option C: Hybrid — Pay USDC, Protocol Buys $TECH (RECOMMENDED)
### How It Works
1. User pays launch fee in USDC (low friction)
2. Protocol fee router splits fees:
   - 50% → distributed to $TECH stakers as USDC (stable real yield)
   - 30% → used to buy $TECH from DEX and burn (deflationary pressure)
   - 20% → protocol treasury (development, operations)

### Pros
- ✅ Low user friction (pay in stablecoins)
- ✅ Creates buy pressure on $TECH (protocol buys from open market)
- ✅ Deflationary mechanism (regular buy-and-burn)
- ✅ Stakers earn stablecoin yield (more valuable than volatile token)
- ✅ No death spiral risk (usage not dependent on token price)
- ✅ Predictable pricing for users
- ✅ Best of both worlds

### Cons
- ❌ Slightly more complex contract (needs DEX integration for buyback)
- ❌ Slippage on DEX buys (mitigate with TWAP or limit orders)
- ❌ Need to handle DEX routing (UniV3, LFJ, etc.)

### Contract Implementation
```solidity
contract FeeRouter {
    address public constant USDC = ...;
    address public constant TECH = ...;
    address public constant DEX_ROUTER = ...;
    
    uint256 public constant STAKER_PCT = 50;
    uint256 public constant BUYBACK_PCT = 30;
    uint256 public constant TREASURY_PCT = 20;
    
    function distributeFees(uint256 amount) external {
        // 50% to stakers as USDC (pull-over-push)
        uint256 stakerShare = (amount * STAKER_PCT) / 100;
        pendingStakerRewards += stakerShare;
        
        // 30% buy $TECH and burn
        uint256 buybackAmount = (amount * BUYBACK_PCT) / 100;
        _buyAndBurnTECH(buybackAmount);
        
        // 20% to treasury
        uint256 treasuryShare = (amount * TREASURY_PCT) / 100;
        IERC20(USDC).transfer(treasury, treasuryShare);
    }
    
    function _buyAndBurnTECH(uint256 usdcAmount) internal {
        // Swap USDC → $TECH on DEX
        IERC20(USDC).approve(DEX_ROUTER, usdcAmount);
        (uint256 tegenAmount,) = IDEXRouter(DEX_ROUTER).swapExactTokensForTokens(
            usdcAmount,
            0, // minOut (use slippage protection)
            [USDC, TECH],
            address(this),
            block.timestamp + 300
        );
        
        // Burn the $TECH
        IERC20(TECH).transfer(address(0), tegenAmount);
        emit TokensBurned(tegenAmount);
    }
    
    // Stakers claim their USDC rewards
    function claimStakerRewards() external {
        uint256 reward = pendingRewards[msg.sender];
        pendingRewards[msg.sender] = 0;
        IERC20(USDC).transfer(msg.sender, reward);
    }
}
```

---

## The GMX Parallel

GMX proved this works:
- Traders pay fees in ETH/USDC/BTC
- Stakers earn fees in those SAME assets (stable + volatile)
- esGMX emissions provide additional token-aligned rewards
- Result: $500M+ TVL, survived bear markets

For AAE:
- Users pay USDC for launches
- Stakers earn USDC (stable yield) + $TECH buybacks support token price
- This is MORE sustainable than forcing $TECH payments

---

## The Death Spiral Prevention

**Option B (pay $TECH only) creates death spiral risk:**
1. $TECH price drops 50%
2. Platform becomes 2x more expensive in USD terms (if fee adjusted)
3. Users leave for cheaper alternatives
4. Less revenue → stakers sell $TECH
5. Price drops more → repeat

**Option C (hybrid) prevents this:**
1. $TECH price drops 50%
2. Platform stays same price in USDC ($5 per launch)
3. Protocol buys MORE $TECH with same USDC (buyback acceleration)
4. Increased buy pressure supports token price
5. Usage continues uninterrupted

---

## Recommended Fee Flow

```
User pays 10 USDC for agent launch
│
├── 5 USDC → Staker Rewards Pool (claimable by $TECH stakers)
├── 3 USDC → DEX swap → $TECH → Burn (deflationary)
└── 2 USDC → Protocol Treasury (dev, operations, reserve fund)
```

### Why This Split?
- **50% to stakers:** Competitive with GMX (70%), sustainable
- **30% buyback/burn:** Creates consistent buy pressure, deflationary
- **20% treasury:** Funds development, burn reserve, operations

### Burn Reserve Funding
The 20% treasury allocation can fund the Agent NFT burn reserve:
- If Agent NFT costs 1000 $TECH, treasury buys $TECH from market over time
- Reserve grows organically from protocol revenue
- No need to lock up 50% of mint price (more capital efficient)

---

## Multi-Chain Considerations

If AAE expands to multiple chains:
- Each chain has its own USDC/TECH pair
- Fee router works identically on each chain
- Stakers earn from ALL chains (aggregated rewards)
- Buyback happens on each chain (supports local liquidity)

---

## Summary: Hybrid Wins

| Factor | USDC Only | $TECH Only | Hybrid (Recommended) |
|--------|-----------|-------------|---------------------|
| **User Friction** | ✅ Low | ❌ High | ✅ Low |
| **Buy Pressure** | ❌ None | ✅ Direct | ✅ Protocol-driven |
| **Price Stability** | ✅ Stable | ❌ Volatile | ✅ Stable for users |
| **Death Spiral Risk** | ✅ None | ❌ High | ✅ None (buyback accel) |
| **Staker Yield Quality** | ✅ Stable | ❌ Volatile | ✅ Stable (USDC) |
| **Deflationary** | ❌ No | ✅ Yes | ✅ Yes (buyback/burn) |
| **Contract Complexity** | ✅ Simple | ✅ Simple | ⚠️ Moderate (DEX) |

**Recommendation:** Hybrid model — users pay USDC, protocol buys/burns $TECH, stakers earn USDC.

*Next: YoYo to validate tokenomics math and model buyback impact on token price over time.*
