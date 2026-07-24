// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/// @title Solana x402 Router
/// @notice Routes verified x402 payments to Solana Agent Economy contracts
/// @dev Accepts x402 payment proofs, verifies them, and forwards to AgentRegistry/JobEscrow
/// @author GenTech Labs
contract X402Router is AccessControl, ReentrancyGuard {
    bytes32 public constant GATEWAY_ROLE = keccak256("GATEWAY_ROLE");
    bytes32 public constant VERIFIER_ROLE = keccak256("VERIFIER_ROLE");

    address public agentRegistry;
    address public jobEscrow;

    struct PaymentProof {
        address payer;
        uint256 amount;
        uint256 timestamp;
        bytes32 paymentId;
        bytes signature;
    }

    mapping(bytes32 => bool) public usedPayments;
    uint256 public minPayment = 0.01 ether; // 0.01 USDC minimum

    event PaymentRouted(
        bytes32 indexed paymentId,
        address indexed payer,
        uint256 amount,
        string action
    );

    constructor(address _registry, address _escrow) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(GATEWAY_ROLE, msg.sender);
        agentRegistry = _registry;
        jobEscrow = _escrow;
    }

    /// @notice Verify x402 payment proof and register an agent
    function payAndRegister(
        string calldata agentName,
        bytes32 skillHash,
        PaymentProof calldata proof
    ) external nonReentrant returns (uint256 agentId) {
        _verifyPayment(proof, "register");
        // Forward to AgentRegistry
        (bool success, bytes memory data) = agentRegistry.call(
            abi.encodeWithSignature("registerAgent(string,bytes32)", agentName, skillHash)
        );
        require(success, "Registration failed");
        agentId = abi.decode(data, (uint256));
        emit PaymentRouted(proof.paymentId, proof.payer, proof.amount, "register");
    }

    /// @notice Verify x402 payment proof and create a job
    function payAndCreateJob(
        address agent,
        uint256 deadline,
        string calldata description,
        PaymentProof calldata proof
    ) external payable nonReentrant returns (uint256 jobId) {
        _verifyPayment(proof, "createJob");
        // Forward to JobEscrow with payment
        (bool success, bytes memory data) = jobEscrow.call{value: msg.value}(
            abi.encodeWithSignature("createJob(address,uint256,string)", agent, deadline, description)
        );
        require(success, "Job creation failed");
        jobId = abi.decode(data, (uint256));
        emit PaymentRouted(proof.paymentId, proof.payer, proof.amount, "createJob");
    }

    function _verifyPayment(PaymentProof calldata proof, string memory action) internal {
        require(!usedPayments[proof.paymentId], "Payment already used");
        require(proof.amount >= minPayment, "Below minimum payment");
        // Verify the payment was processed by the gateway
        require(hasRole(VERIFIER_ROLE, msg.sender) || hasRole(GATEWAY_ROLE, msg.sender), "Unauthorized");
        usedPayments[proof.paymentId] = true;
    }

    function setMinPayment(uint256 _min) external onlyRole(ADMIN_ROLE) {
        minPayment = _min;
    }

    function addVerifier(address verifier) external onlyRole(ADMIN_ROLE) {
        _grantRole(VERIFIER_ROLE, verifier);
    }
}
