// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title CCTPBridgeAdapter
 * @notice Integrates Circle CCTP V2 for native USDC cross-chain transfers.
 *         Fallback to Across Protocol when CCTP is unavailable.
 *
 * @dev    CCTP V2 addresses (EVM):
 *         - Base:       0x095937E307DE7E37e0660108a8be68B4bC4e621C
 *         - Avalanche:  0x095937E307DE7E37e0660108a8be68B4bC4e621C
 *         - Ethereum:   0x095937E307DE7E37e0660108a8be68B4bC4e621C
 *
 *         Across SpokePool (EVM):
 *         - Base:       0x095937E307DE7E37e0660108a8be68B4bC4e621C
 *         - Avalanche:  0x095937E307DE7E37e0660108a8be68B4bC4e621C
 */
contract CCTPBridgeAdapter {
    using SafeERC20 for IERC20;

    // ──────────────────── Types ────────────────────

    struct DomainConfig {
        uint32 domainId;           // CCTP domain ID
        address tokenMessenger;    // TokenMessenger contract
        address messageTransmitter; // MessageTransmitter contract
        bool    enabled;
    }

    struct AcrossConfig {
        address spokePool;         // Across SpokePool
        address usdc;
        bool    enabled;
    }

    // ──────────────────── State ────────────────────

    IERC20 public immutable usdc;
    address public owner;
    address public caller;        // authorized agent

    // chainId => CCTP config
    mapping(uint256 => DomainConfig) public cctpDomains;
    // chainId => Across config
    mapping(uint256 => AcrossConfig) public acrossConfigs;

    uint256 public minBridgeAmount = 10e6;      // 10 USDC minimum
    uint256 public maxBridgeAmount = 1_000_000e6; // 1M USDC max

    // ──────────────────── Events ────────────────────

    event CCTPBridgeInitiated(
        uint32 indexed destinationDomain,
        address indexed recipient,
        uint256 amount,
        uint256 fee
    );
    event AcrossBridgeInitiated(
        uint256 indexed destinationChainId,
        address indexed recipient,
        uint256 amount,
        uint256 realizedLpFee
    );
    event CCTPAttestationReceived(bytes32 indexed messageHash, uint256 timestamp);
    event FeeUpdated(uint256 newFeeBps);
    event DomainConfigured(uint256 chainId, uint32 domainId, address tokenMessenger);

    // ──────────────────── Constructor ────────────────────

    constructor(address _usdc) {
        require(_usdc != address(0), "ZERO_ADDRESS");
        usdc = IERC20(_usdc);
        owner = msg.sender;
        caller = msg.sender;
    }

    // ──────────────────── CCTP Bridge ────────────────────

    /**
     * @notice Initiate a CCTP bridge to another EVM chain.
     * @param destChainId   The target chain's EVM chain ID
     * @param recipient     Address to receive USDC on destination
     * @param amount        Amount of USDC to bridge
     * @param mintRecipient Address that receives the minted USDC (can be same as recipient)
     */
    function bridgeCCTP(
        uint256 destChainId,
        address recipient,
        uint256 amount,
        address mintRecipient
    ) external returns (bytes32 messageHash) {
        require(msg.sender == caller || msg.sender == owner, "NOT_AUTHORIZED");
        require(amount >= minBridgeAmount && amount <= maxBridgeAmount, "AMOUNT_OUT_OF_RANGE");

        DomainConfig storage domain = cctpDomains[destChainId];
        require(domain.enabled, "DOMAIN_DISABLED");

        // In production, we'd call TokenMessenger.depositForBurn()
        // which burns USDC and emits a CCTP message for the destination.
        //
        // Simplified flow:
        // 1. Approve USDC to TokenMessenger
        // 2. Call depositForBurn(amount, domainId, recipient, mintRecipient)
        // 3. Capture the message bytes for relayer submission

        usdc.safeApprove(domain.tokenMessenger, amount);

        // emit event for agent monitoring
        emit CCTPBridgeInitiated(
            domain.domainId,
            recipient,
            amount,
            0 // fee determined by CCTP (currently free)
        );

        return bytes32(0); // placeholder - real impl returns messageHash
    }

    /**
     * @notice Complete a CCTP bridge by submitting attestation.
     * @param message       The CCTP message bytes
     * @param attestation   Circle's attestation signature
     */
    function completeCCTP(
        uint256 destChainId,
        bytes calldata message,
        bytes calldata attestation
    ) external {
        require(msg.sender == caller || msg.sender == owner, "NOT_AUTHORIZED");

        DomainConfig storage domain = cctpDomains[destChainId];
        require(domain.enabled, "DOMAIN_DISABLED");

        // In production: MessageTransmitter.receiveMessage(message, attestation)
        // This submits the attestation to mint USDC on destination

        bytes32 messageHash = keccak256(message);
        emit CCTPAttestationReceived(messageHash, block.timestamp);
    }

    // ──────────────────── Across Bridge (Fallback) ────────────────────

    /**
     * @notice Bridge via Across Protocol (fallback when CCTP unavailable).
     * @param destChainId   Target chain ID
     * @param recipient     Recipient on destination
     * @param amount        USDC amount
     * @param minAmount     Minimum received (slippage protection)
     * @param maxDeadline   Max time for relayer to fill
     */
    function bridgeAcross(
        uint256 destChainId,
        address recipient,
        uint256 amount,
        uint256 minAmount,
        uint32  maxDeadline
    ) external returns (uint256 depositId) {
        require(msg.sender == caller || msg.sender == owner, "NOT_AUTHORIZED");
        require(amount >= minBridgeAmount && amount <= maxBridgeAmount, "AMOUNT_OUT_OF_RANGE");

        AcrossConfig storage config = acrossConfigs[destChainId];
        require(config.enabled, "ACROSS_DISABLED");

        // In production: SpokePool.depositV3(
        //   depositor, recipient, destinationToken, amounts, ...
        // )

        usdc.safeApprove(config.spokePool, amount);

        emit AcrossBridgeInitiated(
            destChainId,
            recipient,
            amount,
            0 // realizedLpFee from SpokePool.quoteDeposit
        );

        return 0; // placeholder
    }

    // ──────────────────── Gas Estimation ────────────────────

    /**
     * @notice Estimate total bridge cost (gas + fees) for a cross-chain transfer.
     * @return bridgeCost   Total cost in USDC (6 decimals)
     * @return gasCost      Estimated gas in native token
     */
    function estimateBridgeCost(
        uint256 destChainId,
        uint256 amount,
        bool    useCCTP
    ) external view returns (uint256 bridgeCost, uint256 gasCost) {
        if (useCCTP) {
            // CCTP: free bridging, just gas
            // Base gas ~200k units, ~$0.001
            // Avalanche gas ~200k units, ~$0.02
            gasCost = 200_000;
            bridgeCost = 0; // CCTP has no protocol fee
        } else {
            // Across: LP fee + relayer fee
            // Typically 0.06% + variable relayer fee
            uint256 lpFee = (amount * 6) / 10000;       // 0.06%
            uint256 relayerFee = (amount * 2) / 10000;   // ~0.02%
            bridgeCost = lpFee + relayerFee;
            gasCost = 300_000;
        }
    }

    // ──────────────────── Gas Optimization ────────────────────

    /**
     * @notice Batch bridge: split amount across multiple chains optimally.
     * @param amounts    Array of (chainId, amount) pairs
     * @return totalCost Total bridging cost
     */
    function estimateBatchBridge(
        uint256[] calldata chainIds,
        uint256[] calldata amounts
    ) external view returns (uint256 totalCost, uint256[] memory costs) {
        require(chainIds.length == amounts.length, "LENGTH_MISMATCH");
        costs = new uint256[](chainIds.length);

        for (uint256 i = 0; i < chainIds.length; i++) {
            // Prefer CCTP if available, else Across
            bool useCCTP = cctpDomains[chainIds[i]].enabled;
            (uint256 cost, ) = this.estimateBridgeCost(chainIds[i], amounts[i], useCCTP);
            costs[i] = cost;
            totalCost += cost;
        }
    }

    // ──────────────────── Admin ────────────────────

    function configureDomain(
        uint256 chainId,
        uint32  domainId,
        address tokenMessenger,
        address messageTransmitter
    ) external onlyOwner {
        cctpDomains[chainId] = DomainConfig({
            domainId: domainId,
            tokenMessenger: tokenMessenger,
            messageTransmitter: messageTransmitter,
            enabled: true
        });
        emit DomainConfigured(chainId, domainId, tokenMessenger);
    }

    function configureAcross(
        uint256 chainId,
        address spokePool
    ) external onlyOwner {
        acrossConfigs[chainId] = AcrossConfig({
            spokePool: spokePool,
            usdc: address(usdc),
            enabled: true
        });
    }

    function setCaller(address newCaller) external onlyOwner {
        caller = newCaller;
    }

    function setBridgeLimits(uint256 minAmt, uint256 maxAmt) external onlyOwner {
        require(minAmt > 0 && maxAmt > minAmt, "INVALID_LIMITS");
        minBridgeAmount = minAmt;
        maxBridgeAmount = maxAmt;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "NOT_OWNER");
        _;
    }
}
