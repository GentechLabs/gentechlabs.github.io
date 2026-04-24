// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IAgentKeeper} from "./interfaces/IAgentKeeper.sol";
import {IAgentRegistry} from "./interfaces/IAgentRegistry.sol";

/**
 * @title AgentKeeper
 * @notice Condition-based autonomous agent execution via KeeperHub integration
 * @dev Agents register conditions and actions; KeeperHub triggers execution
 */
contract AgentKeeper is IAgentKeeper {
    uint256 private _nextJobId = 1;
    mapping(uint256 => KeeperJob) private _jobs;
    IAgentRegistry public immutable agentRegistry;

    constructor(address _agentRegistry) {
        agentRegistry = IAgentRegistry(_agentRegistry);
    }

    /// @inheritdoc IAgentKeeper
    function registerJob(
        uint256 agentId,
        ConditionType conditionType,
        ExecutionType executionType,
        bytes calldata conditionData,
        bytes calldata executionData,
        uint256 maxExecutions
    ) external returns (uint256) {
        // Verify agent exists and caller owns it
        IAgentRegistry.Agent memory agent = agentRegistry.getAgent(agentId);
        require(agent.owner == msg.sender, "Not agent owner");
        require(agent.isActive, "Agent inactive");

        uint256 jobId = _nextJobId++;
        _jobs[jobId] = KeeperJob({
            agentId: agentId,
            owner: msg.sender,
            conditionType: conditionType,
            executionType: executionType,
            conditionData: conditionData,
            executionData: executionData,
            isActive: true,
            lastExecutedAt: 0,
            executionCount: 0,
            maxExecutions: maxExecutions
        });
        emit JobRegistered(jobId, agentId, conditionType);
        return jobId;
    }

    /// @inheritdoc IAgentKeeper
    function executeJob(uint256 jobId) external {
        KeeperJob storage job = _jobs[jobId];
        require(job.isActive, "Job inactive");
        require(
            job.maxExecutions == 0 || job.executionCount < job.maxExecutions,
            "Max executions reached"
        );

        // TODO: Implement condition checking logic
        // TODO: Implement execution logic based on executionType
        // This will be triggered by KeeperHub's check-and-execute pattern

        job.executionCount++;
        job.lastExecutedAt = block.timestamp;
        emit JobExecuted(jobId, job.executionCount);
    }

    /// @inheritdoc IAgentKeeper
    function deactivateJob(uint256 jobId) external {
        KeeperJob storage job = _jobs[jobId];
        require(job.owner == msg.sender, "Not owner");
        job.isActive = false;
        emit JobDeactivated(jobId);
    }

    /// @inheritdoc IAgentKeeper
    function updateJob(uint256 jobId, bytes calldata newConditionData, bytes calldata newExecutionData) external {
        KeeperJob storage job = _jobs[jobId];
        require(job.owner == msg.sender, "Not owner");
        job.conditionData = newConditionData;
        job.executionData = newExecutionData;
        emit JobUpdated(jobId, newConditionData, newExecutionData);
    }

    /// @inheritdoc IAgentKeeper
    function getJob(uint256 jobId) external view returns (KeeperJob memory) {
        require(jobId > 0 && jobId < _nextJobId, "Invalid job");
        return _jobs[jobId];
    }

    /// @inheritdoc IAgentKeeper
    function totalJobs() external view returns (uint256) {
        return _nextJobId - 1;
    }
}
