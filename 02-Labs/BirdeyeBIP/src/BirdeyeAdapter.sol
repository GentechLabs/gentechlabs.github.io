// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "./interfaces/IBirdeyeAdapter.sol";

/// @title IAdapter (embedded for BIP — no AAE dependency required)
/// @notice Base interface for all sidetrack adapters
interface IAdapter {
    event DataProcessed(address indexed source, bytes32 indexed dataHash, uint256 timestamp);
    event ActionTriggered(address indexed agent, bytes32 indexed actionHash, bool success);
    function adapterName() external view returns (string memory name);
    function processData(bytes calldata _data) external returns (bool success);
    function isHealthy() external view returns (bool healthy);
}

/// @title BirdeyeAdapter
/// @notice On-chain adapter for Birdeye Data Services — market data → agent decisions
/// @dev Feeds Solana token prices, volumes, and liquidity into the AAE agent economy
/// @dev Oracle pattern: off-chain script polls Birdeye x402 API, pushes data on-chain
/// @dev Part of the AAE Adapter architecture alongside ZerionAdapter and GoldRushAdapter
/// @author YoYo (GenTech Strategies)
contract BirdeyeAdapter is IBirdeyeAdapter, AccessControl {
    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");

    // --- Core Data ---
    mapping(address => TokenSnapshot) public snapshots;
    mapping(address => address) public birdeyeToEVM; // Birdeye token → EVM representation

    // --- LP Monitoring ---
    LPPosition[] public lpPositions;
    mapping(uint256 => bool) public positionBreached; // positionId => breached

    // --- Stats ---
    uint256 public totalDataPushes;
    uint256 public totalPositionsMonitored;
    uint256 public totalBreachesDetected;

    // --- Config ---
    uint256 public stalenessThreshold = 15 minutes;
    address public immutable agentRegistry;

    error NotOracle();
    error StaleData(uint256 age);
    error InvalidPosition();
    error InactivePosition();

    /// @param _agentRegistry Address of AgentRegistry contract (optional, address(0) to skip)
    constructor(address _agentRegistry) {
        agentRegistry = _agentRegistry;
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ORACLE_ROLE, msg.sender);
    }

    // ═══════════════════════════════════════════
    //              ADAPTER INTERFACE
    // ═══════════════════════════════════════════

    /// @dev IAdapter implementation
    function adapterName() external pure returns (string memory) {
        return "Birdeye";
    }

    /// @dev IAdapter implementation
    function isHealthy() external view returns (bool) {
        return hasRole(ORACLE_ROLE, msg.sender) || totalDataPushes > 0;
    }

    /// @dev IAdapter.processData — thin wrapper for batch pushes
    function processData(bytes calldata _data) external returns (bool) {
        if (!hasRole(ORACLE_ROLE, msg.sender)) revert NotOracle();

        // Decode batch: (address[] tokens, uint256[] prices, uint256[] volumes, uint256[] liquidities)
        (address[] memory tokens, uint256[] memory prices, uint256[] memory volumes, uint256[] memory liquidities) =
            abi.decode(_data, (address[], uint256[], uint256[], uint256[]));

        require(tokens.length == prices.length, "Birdeye: length mismatch");
        require(tokens.length == volumes.length, "Birdeye: length mismatch");
        require(tokens.length == liquidities.length, "Birdeye: length mismatch");

        for (uint256 i = 0; i < tokens.length; i++) {
            _updateTokenData(tokens[i], prices[i], volumes[i], liquidities[i]);
        }

        return true;
    }

    // ═══════════════════════════════════════════
    //              BIRDEYE DATA FEED
    // ═══════════════════════════════════════════

    /// @inheritdoc IBirdeyeAdapter
    function pushTokenData(
        address _token,
        uint256 _price,
        uint256 _volume24h,
        uint256 _liquidity
    ) external override {
        if (!hasRole(ORACLE_ROLE, msg.sender)) revert NotOracle();
        _updateTokenData(_token, _price, _volume24h, _liquidity);
    }

    function _updateTokenData(
        address _token,
        uint256 _price,
        uint256 _volume24h,
        uint256 _liquidity
    ) internal {
        TokenSnapshot storage snap = snapshots[_token];

        // Track price direction
        bool priceDown = _price < snap.price && snap.updatedAt > 0;

        snap.price = _price;
        snap.volume24h = _volume24h;
        snap.liquidity = _liquidity;
        snap.priceDown = priceDown;
        snap.updatedAt = block.timestamp;

        totalDataPushes++;

        emit TokenDataUpdated(_token, _price, _volume24h, _liquidity, block.timestamp);

        // Check all active LP positions for this token
        _checkLPPositionsForToken(_token, _price);
    }

    // ═══════════════════════════════════════════
    //              LP RANGE MONITORING
    // ═══════════════════════════════════════════

    /// @inheritdoc IBirdeyeAdapter
    function registerLPPosition(
        address _tokenA,
        address _tokenB,
        uint256 _lowerPrice,
        uint256 _upperPrice
    ) external override returns (uint256) {
        uint256 positionId = lpPositions.length;

        lpPositions.push(LPPosition({
            agent: msg.sender,
            tokenA: _tokenA,
            tokenB: _tokenB,
            lowerPrice: _lowerPrice,
            upperPrice: _upperPrice,
            active: true
        }));

        totalPositionsMonitored++;
        return positionId;
    }

    /// @inheritdoc IBirdeyeAdapter
    function getTokenSnapshot(address _token) external view override returns (TokenSnapshot memory) {
        return snapshots[_token];
    }

    /// @inheritdoc IBirdeyeAdapter
    function isLPInRange(uint256 _positionId) external view override returns (bool) {
        if (_positionId >= lpPositions.length) revert InvalidPosition();
        LPPosition memory pos = lpPositions[_positionId];
        if (!pos.active) return false;

        TokenSnapshot memory snap = snapshots[pos.tokenA];
        if (snap.updatedAt == 0) return true; // No data yet, assume OK
        if (block.timestamp - snap.updatedAt > stalenessThreshold) return true; // Stale data, don't alarm

        return snap.price >= pos.lowerPrice && snap.price <= pos.upperPrice;
    }

    /// @notice Get full LP position details
    function getLPPosition(uint256 _positionId) external view returns (LPPosition memory) {
        return lpPositions[_positionId];
    }

    /// @notice Deactivate an LP position (user can remove their own)
    function deactivatePosition(uint256 _positionId) external {
        if (_positionId >= lpPositions.length) revert InvalidPosition();
        if (lpPositions[_positionId].agent != msg.sender && !hasRole(DEFAULT_ADMIN_ROLE, msg.sender)) {
            revert InvalidPosition();
        }
        lpPositions[_positionId].active = false;
    }

    function _checkLPPositionsForToken(address _token, uint256 _currentPrice) internal {
        for (uint256 i = 0; i < lpPositions.length; i++) {
            LPPosition storage pos = lpPositions[i];
            if (!pos.active) continue;
            if (pos.tokenA != _token) continue;

            if (_currentPrice < pos.lowerPrice || _currentPrice > pos.upperPrice) {
                if (!positionBreached[i]) {
                    positionBreached[i] = true;
                    totalBreachesDetected++;
                    emit LPRangeBreached(
                        pos.agent,
                        _token,
                        _currentPrice,
                        pos.lowerPrice,
                        pos.upperPrice
                    );
                }
            } else {
                // Back in range — reset breach flag
                positionBreached[i] = false;
            }
        }
    }

    // ═══════════════════════════════════════════
    //              ADMIN
    // ═══════════════════════════════════════════

    /// @notice Update staleness threshold
    function setStalenessThreshold(uint256 _threshold) external onlyRole(DEFAULT_ADMIN_ROLE) {
        stalenessThreshold = _threshold;
    }

    // ═══════════════════════════════════════════
    //              INTERFACE STUBS
    // ═══════════════════════════════════════════

    /// @dev Required by IAdapter — we don't use it directly
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(AccessControl)
        returns (bool)
    {
        return
            interfaceId == type(IAdapter).interfaceId ||
            interfaceId == type(IBirdeyeAdapter).interfaceId ||
            super.supportsInterface(interfaceId);
    }
}
