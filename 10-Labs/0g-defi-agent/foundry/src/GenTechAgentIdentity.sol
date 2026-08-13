// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title GenTech Agent Identity (ERC-7857)
 * @notice On-chain identity for the AI DeFi agent. Stores the agent's
 *         metadata URI (pointing to 0G Storage) and a verifiable record
 *         of its decisions. This is the agent's on-chain passport.
 *
 *         ERC-7857 is the 0G standard for Intelligent NFTs (INFTs) —
 *         agents whose state lives on-chain and whose data lives on
 *         0G Storage.
 */
contract GenTechAgentIdentity {
    address public owner;
    string public name;
    string public metadataURI;   // points to 0G Storage (root hash)
    uint256 public decisionCount;

    struct Decision {
        string action;      // HOLD / ADD / TRIM
        string reason;      // LLM analysis summary
        uint256 timestamp;
        string storageRoot; // 0G Storage root hash of the trade log
    }

    mapping(uint256 => Decision) public decisions;

    event DecisionRecorded(uint256 indexed index, string action, string storageRoot);
    event MetadataUpdated(string metadataURI);

    constructor(string memory _name, string memory _metadataURI) {
        owner = msg.sender;
        name = _name;
        metadataURI = _metadataURI;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    /// @notice Record a decision the agent made, with its 0G Storage proof.
    function recordDecision(
        string calldata _action,
        string calldata _reason,
        string calldata _storageRoot
    ) external onlyOwner {
        decisions[decisionCount] = Decision({
            action: _action,
            reason: _reason,
            timestamp: block.timestamp,
            storageRoot: _storageRoot
        });
        emit DecisionRecorded(decisionCount, _action, _storageRoot);
        decisionCount++;
    }

    /// @notice Update the metadata URI (0G Storage root hash).
    function setMetadataURI(string calldata _metadataURI) external onlyOwner {
        metadataURI = _metadataURI;
        emit MetadataUpdated(_metadataURI);
    }

    /// @notice Transfer agent ownership (the agent can be sold/shared).
    function transferOwnership(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), "Zero address");
        owner = _newOwner;
    }
}
