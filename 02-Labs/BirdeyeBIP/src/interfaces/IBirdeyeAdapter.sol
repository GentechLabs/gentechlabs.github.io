// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title IBirdeyeAdapter
/// @notice Interface for Birdeye market data adapter
/// @dev Feeds token price, volume, liquidity into agent decision engine
interface IBirdeyeAdapter {
    /// @notice Emitted when token data is updated
    event TokenDataUpdated(
        address indexed token,
        uint256 price,
        uint256 volume24h,
        uint256 liquidity,
        uint256 timestamp
    );

    /// @notice Emitted when an LP position goes out of range
    event LPRangeBreached(
        address indexed agent,
        address indexed token,
        uint256 currentPrice,
        uint256 lowerBound,
        uint256 upperBound
    );

    /// @notice Token market snapshot
    struct TokenSnapshot {
        uint256 price;        // USD price, 8 decimals
        uint256 volume24h;    // 24h volume, 8 decimals
        uint256 liquidity;    // Total liquidity, 8 decimals
        uint256 priceChange24h; // Signed? We'll use uint + direction bool
        bool priceDown;       // true if price went down
        uint256 updatedAt;
    }

    /// @notice LP position tracking
    struct LPPosition {
        address agent;
        address tokenA;
        address tokenB;
        uint256 lowerPrice;   // Range lower bound, 8 decimals
        uint256 upperPrice;   // Range upper bound, 8 decimals
        bool active;
    }

    /// @notice Push token data from Birdeye oracle
    /// @param _token Token address
    /// @param _price Current price (8 decimals)
    /// @param _volume24h 24h trading volume (8 decimals)
    /// @param _liquidity Total liquidity (8 decimals)
    function pushTokenData(
        address _token,
        uint256 _price,
        uint256 _volume24h,
        uint256 _liquidity
    ) external;

    /// @notice Register an LP position to monitor
    /// @param _tokenA First token in pair
    /// @param _tokenB Second token in pair
    /// @param _lowerPrice Range lower bound
    /// @param _upperPrice Range upper bound
    /// @return positionId The registered position ID
    function registerLPPosition(
        address _tokenA,
        address _tokenB,
        uint256 _lowerPrice,
        uint256 _upperPrice
    ) external returns (uint256 positionId);

    /// @notice Get latest token snapshot
    /// @param _token Token address
    /// @return snapshot The current market data
    function getTokenSnapshot(address _token) external view returns (TokenSnapshot memory snapshot);

    /// @notice Check if an LP position is in range
    /// @param _positionId The position ID
    /// @return inRange Whether position is within bounds
    function isLPInRange(uint256 _positionId) external view returns (bool inRange);
}
