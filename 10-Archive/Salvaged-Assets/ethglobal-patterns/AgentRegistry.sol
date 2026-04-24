// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IAgentRegistry} from "./interfaces/IAgentRegistry.sol";

/**
 * @title AgentRegistry
 * @notice On-chain registry for AI agents with 0G Storage skill references
 * @dev Agents store skills off-chain on 0G Storage; root hash is stored on-chain
 */
contract AgentRegistry is IAgentRegistry {
    uint256 private _nextAgentId = 1;
    mapping(uint256 => Agent) private _agents;
    mapping(address => uint256[]) private _ownerAgents;

    /// @inheritdoc IAgentRegistry
    function registerAgent(bytes32 skillRootHash, string calldata metadataURI) external returns (uint256) {
        uint256 agentId = _nextAgentId++;
        _agents[agentId] = Agent({
            owner: msg.sender,
            skillRootHash: skillRootHash,
            metadataURI: metadataURI,
            registeredAt: block.timestamp,
            isActive: true
        });
        _ownerAgents[msg.sender].push(agentId);
        emit AgentRegistered(msg.sender, agentId, skillRootHash);
        return agentId;
    }

    /// @inheritdoc IAgentRegistry
    function updateSkills(uint256 agentId, bytes32 newSkillRootHash) external {
        Agent storage agent = _agents[agentId];
        require(agent.owner == msg.sender, "Not owner");
        require(agent.isActive, "Agent inactive");
        agent.skillRootHash = newSkillRootHash;
        emit SkillsUpdated(agentId, newSkillRootHash);
    }

    /// @inheritdoc IAgentRegistry
    function deactivateAgent(uint256 agentId) external {
        Agent storage agent = _agents[agentId];
        require(agent.owner == msg.sender, "Not owner");
        agent.isActive = false;
        emit AgentDeactivated(agentId);
    }

    /// @inheritdoc IAgentRegistry
    function getAgent(uint256 agentId) external view returns (Agent memory) {
        require(agentId > 0 && agentId < _nextAgentId, "Invalid agent");
        return _agents[agentId];
    }

    /// @inheritdoc IAgentRegistry
    function totalAgents() external view returns (uint256) {
        return _nextAgentId - 1;
    }
}
