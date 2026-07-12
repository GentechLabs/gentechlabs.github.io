# $TECH Dynamic Burn/Recycle Mechanism Research

*Drafted: 2026-04-20*

---

## The Problem

Fixed burn percentages are inflexible. If $TECH price pumps 10x, a flat 30% discount becomes a massive subsidy. If it dumps, nobody uses $TECH because USDC is cheaper. You need **adaptive mechanics** that respond to market conditions.

---

## Dynamic Model: Adaptive Burn Rate

Instead of burn-vs-recycle as a binary, make it a **continuous dial** controlled by on-chain or off-chain signals.

### Core Parameters

| Signal | Action |
|--------|--------|
| $TECH price rising fast (>20% 7d) | Increase burn % (reduce supply) |
| $TECH price falling (>20% 7d) | Increase recycle % (fund competitions, grow ecosystem) |
| Discount price > USDC price | Shrink discount (don't let $TECH payment cost more) |
| TVL / usage growing | Can afford more burns |
| Treasury running low | Shift toward recycle |

### The Algorithm

```
burn_ratio = base_burn (0.5) 
           + price_momentum * momentum_weight
           + treasury_health * treasury_weight
           - discount_pressure * pressure_weight

// Clamp to [0.1, 0.9] — never fully burn or fully recycle
burn_ratio = clamp(burn_ratio, 0.1, 0.9)

burn_amount = payment * burn_ratio
recycle_amount = payment * (1 - burn_ratio)
```

---

## Implementation Paths

### Option A: EVM (Base) — Solidity + OpenZeppelin

**Best for:** Composability, DeFi integrations, existing Base ecosystem

**Architecture:**
```
User pays $TECH
    → PaymentRouter contract
    → Reads burn_ratio from PriceOracle
    → burn_ratio * amount → transfer to 0x000...dEaD
    → (1 - burn_ratio) * amount → transfer to TreasuryMultisig
```

**Key Contracts:**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract TECHPaymentRouter is Ownable {
    using SafeERC20 for IERC20;
    
    IERC20 public immutable techToken;
    address public treasury;
    address public constant BURN_ADDRESS = 0x000000000000000000000000000000000000dEaD;
    
    // Basis points (0-10000), default 5000 = 50%
    uint256 public burnRatioBps;
    
    // Discount off USDC price in basis points
    uint256 public discountBps = 2500; // 25% off
    
    // Bounds
    uint256 public constant MIN_BURN_BPS = 1000;  // 10%
    uint256 public constant MAX_BURN_BPS = 9000;  // 90%
    
    event PaymentProcessed(address indexed buyer, uint256 totalPaid, uint256 burned, uint256 recycled);
    event BurnRatioUpdated(uint256 oldRatio, uint256 newRatio);
    
    constructor(address _techToken, address _treasury, uint256 _initialBurnRatio) Ownable(msg.sender) {
        techToken = IERC20(_techToken);
        treasury = _treasury;
        burnRatioBps = _initialBurnRatio;
    }
    
    function processPayment(uint256 amount) external {
        techToken.safeTransferFrom(msg.sender, address(this), amount);
        
        uint256 burnAmount = (amount * burnRatioBps) / 10000;
        uint256 recycleAmount = amount - burnAmount;
        
        if (burnAmount > 0) {
            techToken.safeTransfer(BURN_ADDRESS, burnAmount);
        }
        if (recycleAmount > 0) {
            techToken.safeTransfer(treasury, recycleAmount);
        }
        
        emit PaymentProcessed(msg.sender, amount, burnAmount, recycleAmount);
    }
    
    // Called by keeper/oracle with new ratio
    function updateBurnRatio(uint256 newRatioBps) external onlyOwner {
        require(newRatioBps >= MIN_BURN_BPS && newRatioBps <= MAX_BURN_BPS, "Out of bounds");
        uint256 oldRatio = burnRatioBps;
        burnRatioBps = newRatioBps;
        emit BurnRatioUpdated(oldRatio, newRatioBps);
    }
    
    function updateDiscount(uint256 newDiscountBps) external onlyOwner {
        require(newDiscountBps <= 5000, "Max 50% discount");
        discountBps = newDiscountBps;
    }
}
```

**Price Oracle / Keeper (off-chain):**
```python
# keeper.py — runs on cron, updates burn ratio on-chain
from web3 import Web3
from dataclasses import dataclass

@dataclass
class MarketSignals:
    price_7d_change: float   # -1.0 to +N
    treasury_usd: float
    daily_volume_usd: float
    token_price_usd: float

def calculate_burn_ratio(signals: MarketSignals) -> int:
    """Returns burn ratio in basis points (1000-9000)"""
    base = 5000  # 50%
    
    # Momentum: rising price → more burn
    momentum_adj = min(signals.price_7d_change * 1000, 2000)  # ±20%
    
    # Treasury health: more treasury → can burn more
    treasury_adj = min(signals.treasury_usd / 100_000 * 500, 1500)  # up to +15%
    
    ratio = base + int(momentum_adj) + int(treasury_adj)
    return max(1000, min(9000, ratio))

def calculate_discount(signals: MarketSignals, usdc_equivalent: float) -> int:
    """Dynamic discount — ensures $TECH payment is always cheaper than USDC"""
    tech_cost = usdc_equivalent * (1 - 0.25)  # 25% base discount
    if signals.token_price_usd * tech_cost > usdc_equivalent:
        # Token pumped too hard, shrink discount
        return 1500  # 15%
    return 2500  # 25%
```

**SDKs & Tools (Base/EVM):**
- **OpenZeppelin Contracts** — ERC20, SafeERC20, AccessControl
- **Hardhat + ethers.js** — Development & deployment
- **Chainlink Automation** — Keepers for periodic burn ratio updates
- **Gelato Network** — Alternative keeper network
- **Uniswap V3 TWAP Oracle** — On-chain price feed (no Chainlink dependency)
- **Foundry** — Testing (forge test, fuzz testing)

---

### Option B: Solana — SPL Token + Anchor

**Best for:** Low fees, fast finality, native token burn

**Architecture:**
```
User pays $TECH (SPL Token)
    → Anchor program instruction
    → SPL Token burn() for burn portion
    → SPL Token transfer() for recycle portion
    → Burn ratio from Pyth/Chainlink price feed
```

**Key Program (Anchor):**

```rust
use anchor_lang::prelude::*;
use anchor_spl::token::{self, Burn, Transfer, Token, TokenAccount};

#[program]
pub mod tech_payment {
    use super::*;

    pub fn process_payment(
        ctx: Context<ProcessPayment>,
        amount: u64,
    ) -> Result<()> {
        let config = &ctx.accounts.config;
        
        let burn_amount = amount
            .checked_mul(config.burn_ratio_bps as u64)
            .unwrap()
            .checked_div(10_000)
            .unwrap();
        let recycle_amount = amount - burn_amount;

        // Burn portion
        token::burn(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                Burn {
                    mint: ctx.accounts.tech_mint.to_account_info(),
                    from: ctx.accounts.user_token_account.to_account_info(),
                    authority: ctx.accounts.user.to_account_info(),
                },
            ),
            burn_amount,
        )?;

        // Recycle to treasury
        token::transfer(
            CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                Transfer {
                    from: ctx.accounts.user_token_account.to_account_info(),
                    to: ctx.accounts.treasury_token_account.to_account_info(),
                    authority: ctx.accounts.user.to_account_info(),
                },
            ),
            recycle_amount,
        )?;

        emit!(PaymentProcessed {
            user: ctx.accounts.user.key(),
            total: amount,
            burned: burn_amount,
            recycled: recycle_amount,
        });

        Ok(())
    }

    pub fn update_burn_ratio(
        ctx: Context<UpdateConfig>,
        new_ratio: u16,
    ) -> Result<()> {
        require!(new_ratio >= 1000 && new_ratio <= 9000, ErrorCode::RatioOutOfBounds);
        ctx.accounts.config.burn_ratio_bps = new_ratio;
        Ok(())
    }
}

#[account]
pub struct PaymentConfig {
    pub burn_ratio_bps: u16,       // 1000-9000
    pub discount_bps: u16,         // Dynamic discount
    pub authority: Pubkey,
}

#[derive(Accounts)]
pub struct ProcessPayment<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    #[account(mut)]
    pub user_token_account: Account<'info, TokenAccount>,
    pub tech_mint: Account<'info, token::Mint>,
    #[account(mut)]
    pub treasury_token_account: Account<'info, TokenAccount>,
    pub config: Account<'info, PaymentConfig>,
    pub token_program: Program<'info, Token>,
}
```

**SDKs & Tools (Solana):**
- **Anchor Framework** — Rust program development (high-level, account validation)
- **SPL Token Program** — Native burn(), transfer() instructions
- **Pyth Network** — On-chain price oracle (used by Jupiter, etc.)
- **Solana Web3.js** / **@solana/spl-token** — JS/TS client SDK
- **Anchor + Mocha** — Testing framework
- **Metaplex** — If you want metadata attached to $TECH
- **Jupiter API** — Best swap routes if you need USDC↔TECH pricing

---

### Option C: Hybrid — Both Chains

Run $TECH on both Base + Solana (wrapped). Burn logic lives on each chain independently. Bridge via Wormhole or LayerZero.

**Pros:** Maximum reach, DeFi on Base + Solana speed
**Cons:** More complexity, bridge risk, split liquidity

---

## Dynamic Discount Mechanism

The discount must adapt so $TECH payment is **always cheaper** than USDC, regardless of token price.

```
effective_price_usdc = base_price_usdc
effective_price_tech = base_price_usdc * (1 - discount_bps/10000)

// At $TECH = $0.10:
//   base_price = $10, discount = 25%
//   $TECH cost = $7.50 → user pays 75 $TECH ← cheaper ✓

// At $TECH = $1.00:
//   base_price = $10, discount = 25%  
//   $TECH cost = $7.50 → user pays 7.5 $TECH ← cheaper ✓

// If $TECH moons and discount makes it > USDC:
//   → Keeper shrinks discount automatically
```

**Formula:**
```
max_sustainable_discount = 1 - (usdc_price / (token_price * tech_amount_at_base_discount))
discount = min(base_discount, max_sustainable_discount)
```

---

## Burn Verification Dashboard

Holders want proof. Build a simple dashboard:

1. **On-chain burn tracker** — Total burned = balance of 0xdead (Base) or mint supply decrease (Solana)
2. **Real-time API** — Expose `/api/burn-stats` from indexer
3. **Telegram bot command** — `!burn` → shows total burned, burn rate, % of supply

---

## Recommended Stack

| Component | Base | Solana |
|-----------|------|--------|
| Contract/Program | Solidity + OpenZeppelin | Anchor + SPL Token |
| Price Oracle | Chainlink / Uniswap TWAP | Pyth Network |
| Keeper (burn ratio) | Chainlink Automation / Gelato | Clockwork / custom cron |
| Testing | Foundry (forge) | Anchor test suite |
| Client SDK | ethers.js / viem | @solana/spl-token + web3.js |
| Indexer | The Graph / Alchemy | Helius / SolanaFM |

---

## Test Results — 2026-04-20

**Status: ✅ ALL 29 TESTS PASSING**

| Suite | Tests | Status |
|-------|-------|--------|
| Core payment processing (50/70/90/10 splits, events, reverts) | 7 | ✅ |
| Dynamic burn ratio updates (bounds, events, access control) | 5 | ✅ |
| Dynamic discount updates (bounds, events, access control) | 4 | ✅ |
| Price calculation (discount math, edge cases) | 5 | ✅ |
| Keeper simulation (bull/bear market scenarios) | 2 | ✅ |
| Edge cases (treasury update, zero amounts) | 2 | ✅ |
| Fuzz tests (256 runs each — payments, ratios, discounts, price math) | 4 | ✅ |

**Key invariants verified by fuzz:**
- Tokens always fully accounted for (burn + recycle + user balance = total)
- $TECH cost always ≤ discounted USDC price (discount guarantee holds)
- All valid ratio/discount values accepted, all invalid ones revert

**Location:** `/root/gentech/agent-escrow/`
- Contract: `contracts/TECHPaymentRouter.sol`
- Tests: `test/TECHPaymentRouter.t.sol`
- Framework: Foundry (forge 1.5.1-stable)

---

## Next Steps

1. **Pick chain(s)** — Base only, Solana only, or hybrid?
2. **Decide oracle** — On-chain (TWAP) vs off-chain (Chainlink/Pyth)?
3. **Keeper strategy** — Who updates burn ratio and how often?
4. **Deploy testnet** — Base Sepolia or Solana Devnet
5. **Build keeper bot** — Python script with price feeds + contract calls
6. **Dashboard** — Burn tracker + Telegram integration

---

## References

- OpenZeppelin ERC20 Burnable: `@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol`
- Solana SPL Token Burn: `spl-token burn <TOKEN_ADDRESS> <AMOUNT>`
- Anchor Book: https://www.anchor-lang.com/
- Pyth Price Feeds: https://docs.pyth.network/price-feeds
- Chainlink Automation: https://automation.chain.link/
- Gelato Network: https://docs.gelato.network/
- Uniswap V3 Oracle: https://docs.uniswap.org/contracts/v3/reference/core/libraries/Oracle
