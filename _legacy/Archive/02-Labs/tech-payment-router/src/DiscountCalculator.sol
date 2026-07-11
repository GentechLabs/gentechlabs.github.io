// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./interfaces/IAggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title DiscountCalculator
/// @notice Computes dynamic $TECH discount based on oracle price + loyalty tier
/// @dev Hybrid model: oracle-based base discount + on-chain loyalty boost
contract DiscountCalculator is Ownable {
    // --- Discount bounds (basis points, 10000 = 100%) ---
    uint256 public constant MIN_DISCOUNT_BPS = 1000;  // 10% floor
    uint256 public constant MAX_DISCOUNT_BPS = 3000;  // 30% ceiling (before loyalty)
    uint256 public constant MAX_LOYALTY_BONUS_BPS = 500; // +5% max loyalty
    uint256 public constant ABSOLUTE_CAP_BPS = 3500;   // 35% absolute max

    // --- SMA thresholds ---
    uint256 public constant SMA_DEVIATION_HIGH = 120; // 120% of SMA = discount tightens
    uint256 public constant SMA_DEVIATION_LOW = 80;   // 80% of SMA = discount widens

    // --- Loyalty tiers (cumulative $TECH spent, in 18 decimals) ---
    uint256 public constant TIER_BRONZE = 0;
    uint256 public constant TIER_SILVER = 10_000 ether;   // 10K $TECH spent
    uint256 public constant TIER_GOLD = 100_000 ether;    // 100K $TECH spent
    uint256 public constant TIER_DIAMOND = 1_000_000 ether; // 1M $TECH spent

    // --- Loyalty bonuses ---
    uint256 public constant BONUS_BRONZE = 0;    // 0 bps
    uint256 public constant BONUS_SILVER = 100;  // +1%
    uint256 public constant BONUS_GOLD = 300;    // +3%
    uint256 public constant BONUS_DIAMOND = 500; // +5%

    IAggregatorV3Interface public immutable priceFeed;
    uint256 public smaPrice; // 50-day SMA, updated externally or via keeper

    event SMAUpdated(uint256 oldSma, uint256 newSma);
    event DiscountCalculated(
        address indexed user,
        uint256 oraclePrice,
        uint256 smaPrice,
        uint256 baseDiscountBps,
        uint256 loyaltyBonusBps,
        uint256 totalDiscountBps
    );

    constructor(address _priceFeed, uint256 _initialSma) Ownable(msg.sender) {
        priceFeed = IAggregatorV3Interface(_priceFeed);
        smaPrice = _initialSma;
    }

    // --- Core discount calculation ---

    /// @notice Calculate total discount for a user based on oracle + loyalty
    /// @param cumulativeSpent Total $TECH spent by user (tracked by router)
    /// @return totalDiscountBps Discount in basis points
    function calculateDiscount(uint256 cumulativeSpent) public view returns (uint256 totalDiscountBps) {
        uint256 baseBps = _calculateBaseDiscount();
        uint256 loyaltyBps = _calculateLoyaltyBonus(cumulativeSpent);

        totalDiscountBps = baseBps + loyaltyBps;

        // Absolute cap
        if (totalDiscountBps > ABSOLUTE_CAP_BPS) {
            totalDiscountBps = ABSOLUTE_CAP_BPS;
        }
    }

    /// @notice Convert a USD price to $TECH amount with discount applied
    /// @param usdPriceWei Price in USD (18 decimals, e.g., 10e18 = $10)
    /// @param cumulativeSpent User's cumulative $TECH spend
    /// @return techAmount $TECH tokens required (with discount)
    /// @return discountBps The discount applied
    function getDiscountedTechAmount(
        uint256 usdPriceWei,
        uint256 cumulativeSpent
    ) external view returns (uint256 techAmount, uint256 discountBps) {
        uint256 oraclePrice = _getOraclePrice();
        discountBps = calculateDiscount(cumulativeSpent);

        // Full price in $TECH: usdPrice / techPrice
        uint256 fullTechAmount = (usdPriceWei * 1e18) / oraclePrice;

        // Apply discount: user pays (10000 - discount)% of full amount
        techAmount = fullTechAmount * (10000 - discountBps) / 10000;
    }

    // --- SMA management ---

    /// @notice Update the 50-day SMA (called by keeper or admin)
    function updateSMA(uint256 newSma) external onlyOwner {
        uint256 oldSma = smaPrice;
        smaPrice = newSma;
        emit SMAUpdated(oldSma, newSma);
    }

    // --- Internal ---

    function _calculateBaseDiscount() internal view returns (uint256) {
        uint256 oraclePrice = _getOraclePrice();

        if (smaPrice == 0) return MIN_DISCOUNT_BPS; // safety fallback

        // Calculate price as percentage of SMA
        uint256 priceRatio = (oraclePrice * 100) / smaPrice;

        if (priceRatio >= SMA_DEVIATION_HIGH) {
            // Price is 120%+ of SMA → tight discount (only 10%)
            return MIN_DISCOUNT_BPS;
        } else if (priceRatio <= SMA_DEVIATION_LOW) {
            // Price is 80% or less of SMA → max discount (30%)
            return MAX_DISCOUNT_BPS;
        } else {
            // Linear interpolation between 80-120% range
            // At 80%: 30%, at 120%: 10%
            // Formula: MAX - (priceRatio - 80) * (MAX - MIN) / (120 - 80)
            uint256 range = SMA_DEVIATION_HIGH - SMA_DEVIATION_LOW; // 40
            uint256 position = priceRatio - SMA_DEVIATION_LOW; // 0 to 40
            return MAX_DISCOUNT_BPS - (position * (MAX_DISCOUNT_BPS - MIN_DISCOUNT_BPS) / range);
        }
    }

    function _calculateLoyaltyBonus(uint256 cumulativeSpent) internal pure returns (uint256) {
        if (cumulativeSpent >= TIER_DIAMOND) return BONUS_DIAMOND;
        if (cumulativeSpent >= TIER_GOLD) return BONUS_GOLD;
        if (cumulativeSpent >= TIER_SILVER) return BONUS_SILVER;
        return BONUS_BRONZE;
    }

    function _getOraclePrice() internal view returns (uint256) {
        (
            uint80 roundId,
            int256 answer,
            ,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();

        require(answer > 0, "DiscountCalculator: invalid oracle price");
        require(answeredInRound >= roundId, "DiscountCalculator: stale round");
        require(block.timestamp - updatedAt < 1 hours, "DiscountCalculator: stale price");

        uint8 decimals = priceFeed.decimals();
        // Normalize to 18 decimals
        return uint256(answer) * (10 ** (18 - decimals));
    }
}
