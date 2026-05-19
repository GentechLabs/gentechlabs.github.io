// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title GenLayerOracleResolver
 * @notice IResolver implementation that delegates disputes to a GenLayer Intelligent Contract
 * @dev Bridge pattern: Solidity stores lifecycle, keeper relays GenLayer verdict back.
 *      GenLayer contract reads evidence URL → runs LLM → consensus via Optimistic Democracy.
 *      This contract waits for the oracle callback before finalizing.
 *
 *      Flow:
 *        1. Escrow calls fileDispute() → stores context, emits event
 *        2. Keeper picks up event → calls GenLayer Intelligent Contract
 *        3. GenLayer LLM reads evidence URL, decides verdict
 *        4. Keeper relays verdict → submitVerdict() callback
 *        5. Escrow calls executeVerdict() → returns payouts
 *
 *      For hackathon: keeper is a trusted off-chain service (our bot).
 *      Production: replace with LayerZero cross-chain message or GenLayer native bridge.
 */
contract GenLayerOracleResolver is ReentrancyGuard, Ownable {

    // ============ Events ============
    event DisputeFiled(uint256 indexed disputeId, uint256 indexed escrowId, string evidenceUrl);
    event VerdictSubmitted(uint256 indexed disputeId, uint8 verdict, string reasoning);
    event VerdictExecuted(uint256 indexed disputeId);
    event KeeperAuthorized(address indexed keeper);
    event KeeperRevoked(address indexed keeper);
    event GenLayerContractUpdated(address oldContract, address newContract);

    // ============ Errors ============
    error DisputeNotFound();
    error DisputeAlreadyFiled();
    error DisputeNotReady();
    error DisputeAlreadyExecuted();
    error InvalidVerdict();
    error NotKeeper();
    error InvalidAddress();
    error MissingEvidenceUrl();
    error ChallengePeriodNotExpired();

    // ============ Types ============
    // Matches IResolver.Verdict
    enum Verdict {
        Pending,
        BuyerWins,
        SellerWins,
        Split,
        Escalated
    }

    enum DisputeStatus {
        Filed,          // Waiting for keeper to relay to GenLayer
        Adjudicating,   // GenLayer processing (LLM + consensus)
        Decided,        // Verdict relayed back, ready to execute
        Executed,       // Funds distributed
        Cancelled
    }

    struct Dispute {
        uint256 escrowId;
        address buyer;
        address seller;
        address token;
        uint256 amount;
        string serviceDescription;
        string evidenceUrl;         // URL for GenLayer LLM to read
        Verdict verdict;
        DisputeStatus status;
        string reasoning;           // GenLayer LLM's explanation
        uint256 filedAt;
        uint256 decidedAt;
        uint256 executedAt;
    }

    // ============ State ============
    address public genLayerContract;    // GenLayer Intelligent Contract address (for reference)
    uint256 public challengePeriod;     // Seconds to wait after verdict before execution (Optimistic Democracy safety)
    uint256 private _nextDisputeId = 1;

    mapping(uint256 => Dispute) public disputes;
    mapping(address => bool) public keepers;    // Authorized relay addresses

    // ============ Constructor ============
    constructor(
        address _genLayerContract,
        address _initialKeeper,
        uint256 _challengePeriod
    ) Ownable(msg.sender) {
        if (_genLayerContract == address(0)) revert InvalidAddress();
        if (_initialKeeper == address(0)) revert InvalidAddress();

        genLayerContract = _genLayerContract;
        challengePeriod = _challengePeriod;
        keepers[_initialKeeper] = true;

        emit KeeperAuthorized(_initialKeeper);
    }

    // ============ IResolver Implementation ============

    /**
     * @notice File a dispute — records context and signals keeper to relay to GenLayer
     * @dev Metadata field from IResolver.DisputeContext is ABI-encoded as:
     *      (string evidenceUrl) — the URL GenLayer's LLM will read to adjudicate
     * @return disputeId Unique ID within this resolver
     */
    function fileDispute(
        uint256 escrowId,
        address buyer,
        address seller,
        address token,
        uint256 amount,
        string calldata serviceDescription,
        bytes calldata metadata
    ) external nonReentrant returns (uint256 disputeId) {
        // Decode evidence URL from metadata
        string memory evidenceUrl = abi.decode(metadata, (string));
        if (bytes(evidenceUrl).length == 0) revert MissingEvidenceUrl();

        disputeId = _nextDisputeId++;

        disputes[disputeId] = Dispute({
            escrowId: escrowId,
            buyer: buyer,
            seller: seller,
            token: token,
            amount: amount,
            serviceDescription: serviceDescription,
            evidenceUrl: evidenceUrl,
            verdict: Verdict.Pending,
            status: DisputeStatus.Filed,
            reasoning: "",
            filedAt: block.timestamp,
            decidedAt: 0,
            executedAt: 0
        });

        emit DisputeFiled(disputeId, escrowId, evidenceUrl);
    }

    /**
     * @notice Submit evidence (additional URL or data for GenLayer to read)
     * @dev For GenLayer resolver, this updates the evidence URL
     */
    function submitEvidence(uint256 disputeId, bytes calldata evidence) external {
        Dispute storage d = disputes[disputeId];
        if (d.escrowId == 0) revert DisputeNotFound();
        if (d.status != DisputeStatus.Filed && d.status != DisputeStatus.Adjudicating) {
            revert DisputeNotReady();
        }

        // Update evidence URL — GenLayer will re-read on next adjudication
        string memory newUrl = abi.decode(evidence, (string));
        d.evidenceUrl = newUrl;
    }

    /**
     * @notice Get current verdict state
     */
    function getVerdict(uint256 disputeId)
        external view
        returns (
            Verdict verdict,
            string memory reasoning,
            uint256 buyerPayout,
            uint256 sellerPayout
        )
    {
        Dispute storage d = disputes[disputeId];
        if (d.escrowId == 0) revert DisputeNotFound();

        verdict = d.verdict;
        reasoning = d.reasoning;

        if (d.verdict == Verdict.BuyerWins) {
            buyerPayout = d.amount;
            sellerPayout = 0;
        } else if (d.verdict == Verdict.SellerWins) {
            buyerPayout = 0;
            sellerPayout = d.amount;
        } else if (d.verdict == Verdict.Split) {
            buyerPayout = d.amount / 2;
            sellerPayout = d.amount - buyerPayout;
        } else {
            buyerPayout = 0;
            sellerPayout = 0;
        }
    }

    /**
     * @notice Finalize and execute — returns payout amounts for escrow to distribute
     * @dev Only callable after challenge period expires (Optimistic Democracy safety)
     */
    function executeVerdict(uint256 disputeId)
        external nonReentrant
        returns (uint256 buyerPayout, uint256 sellerPayout)
    {
        Dispute storage d = disputes[disputeId];
        if (d.escrowId == 0) revert DisputeNotFound();
        if (d.status != DisputeStatus.Decided) revert DisputeNotReady();
        if (d.executedAt != 0) revert DisputeAlreadyExecuted();

        // Challenge period check — Optimistic Democracy can still appeal
        if (block.timestamp < d.decidedAt + challengePeriod) {
            revert ChallengePeriodNotExpired();
        }

        d.status = DisputeStatus.Executed;
        d.executedAt = block.timestamp;

        if (d.verdict == Verdict.BuyerWins) {
            buyerPayout = d.amount;
            sellerPayout = 0;
        } else if (d.verdict == Verdict.SellerWins) {
            buyerPayout = 0;
            sellerPayout = d.amount;
        } else {
            // Split
            buyerPayout = d.amount / 2;
            sellerPayout = d.amount - buyerPayout;
        }

        emit VerdictExecuted(disputeId);
    }

    /**
     * @notice Check if verdict is ready for execution
     */
    function isReady(uint256 disputeId) external view returns (bool ready) {
        Dispute storage d = disputes[disputeId];
        if (d.escrowId == 0) return false;
        if (d.status != DisputeStatus.Decided) return false;
        return block.timestamp >= d.decidedAt + challengePeriod;
    }

    /**
     * @notice Cancel a dispute (owner only, before verdict)
     */
    function cancelDispute(uint256 disputeId) external {
        Dispute storage d = disputes[disputeId];
        if (d.escrowId == 0) revert DisputeNotFound();
        if (d.status == DisputeStatus.Executed) revert DisputeAlreadyExecuted();
        if (msg.sender != owner() && msg.sender != d.buyer && msg.sender != d.seller) {
            revert NotKeeper();
        }

        d.status = DisputeStatus.Cancelled;
    }

    // ============ Oracle / Keeper Interface ============

    /**
     * @notice Called by keeper after GenLayer consensus completes
     * @param disputeId The dispute
     * @param verdict GenLayer's decision (1=BuyerWins, 2=SellerWins, 3=Split)
     * @param reasoning LLM-generated explanation
     */
    function submitVerdict(
        uint256 disputeId,
        Verdict verdict,
        string calldata reasoning
    ) external {
        if (!keepers[msg.sender]) revert NotKeeper();

        Dispute storage d = disputes[disputeId];
        if (d.escrowId == 0) revert DisputeNotFound();
        if (d.status != DisputeStatus.Filed && d.status != DisputeStatus.Adjudicating) {
            revert DisputeNotReady();
        }
        if (verdict == Verdict.Pending || verdict == Verdict.Escalated) {
            revert InvalidVerdict();
        }

        d.verdict = verdict;
        d.status = DisputeStatus.Decided;
        d.reasoning = reasoning;
        d.decidedAt = block.timestamp;

        emit VerdictSubmitted(disputeId, uint8(verdict), reasoning);
    }

    /**
     * @notice Keeper signals that GenLayer has received the dispute (optional status update)
     */
    function markAdjudicating(uint256 disputeId) external {
        if (!keepers[msg.sender]) revert NotKeeper();

        Dispute storage d = disputes[disputeId];
        if (d.escrowId == 0) revert DisputeNotFound();
        if (d.status == DisputeStatus.Filed) {
            d.status = DisputeStatus.Adjudicating;
        }
    }

    // ============ View ============

    function getDispute(uint256 disputeId) external view returns (Dispute memory) {
        if (disputes[disputeId].escrowId == 0) revert DisputeNotFound();
        return disputes[disputeId];
    }

    function getEvidenceUrl(uint256 disputeId) external view returns (string memory) {
        if (disputes[disputeId].escrowId == 0) revert DisputeNotFound();
        return disputes[disputeId].evidenceUrl;
    }

    // ============ Admin ============

    function addKeeper(address _keeper) external onlyOwner {
        if (_keeper == address(0)) revert InvalidAddress();
        keepers[_keeper] = true;
        emit KeeperAuthorized(_keeper);
    }

    function removeKeeper(address _keeper) external onlyOwner {
        keepers[_keeper] = false;
        emit KeeperRevoked(_keeper);
    }

    function setGenLayerContract(address _contract) external onlyOwner {
        if (_contract == address(0)) revert InvalidAddress();
        address old = genLayerContract;
        genLayerContract = _contract;
        emit GenLayerContractUpdated(old, _contract);
    }

    function setChallengePeriod(uint256 _period) external onlyOwner {
        challengePeriod = _period;
    }
}
