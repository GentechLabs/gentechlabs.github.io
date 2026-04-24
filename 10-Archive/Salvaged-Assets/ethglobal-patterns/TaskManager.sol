// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ITaskManager} from "./interfaces/ITaskManager.sol";
import {IAgentRegistry} from "./interfaces/IAgentRegistry.sol";

/**
 * @title TaskManager
 * @notice On-chain task lifecycle with ETH escrow for agent task execution
 * @dev Tasks are posted with ETH, claimed by agent owners, completed with 0G result hashes
 */
contract TaskManager is ITaskManager {
    uint256 private _nextTaskId = 1;
    mapping(uint256 => Task) private _tasks;
    IAgentRegistry public immutable agentRegistry;

    constructor(address _agentRegistry) {
        agentRegistry = IAgentRegistry(_agentRegistry);
    }

    /// @inheritdoc ITaskManager
    function postTask(uint256 agentId, string calldata taskDataHash) external payable returns (uint256) {
        require(msg.value > 0, "Payment required");
        if (agentId > 0) {
            IAgentRegistry.Agent memory agent = agentRegistry.getAgent(agentId);
            require(agent.isActive, "Agent inactive");
        }
        uint256 taskId = _nextTaskId++;
        _tasks[taskId] = Task({
            poster: msg.sender,
            agentId: agentId,
            payment: msg.value,
            status: TaskStatus.Open,
            claimer: address(0),
            taskDataHash: taskDataHash,
            createdAt: block.timestamp,
            completedAt: 0,
            resultHash: bytes32(0)
        });
        emit TaskPosted(taskId, msg.sender, msg.value);
        return taskId;
    }

    /// @inheritdoc ITaskManager
    function claimTask(uint256 taskId) external {
        Task storage task = _tasks[taskId];
        require(task.status == TaskStatus.Open, "Not open");
        // TODO: Verify msg.sender is owner of the assigned agent
        task.claimer = msg.sender;
        task.status = TaskStatus.Claimed;
        emit TaskClaimed(taskId, msg.sender);
    }

    /// @inheritdoc ITaskManager
    function completeTask(uint256 taskId, bytes32 resultHash) external {
        Task storage task = _tasks[taskId];
        require(task.status == TaskStatus.Claimed, "Not claimed");
        require(task.claimer == msg.sender, "Not claimer");
        task.status = TaskStatus.Completed;
        task.completedAt = block.timestamp;
        task.resultHash = resultHash;
        emit TaskCompleted(taskId, resultHash);
    }

    /// @inheritdoc ITaskManager
    function disputeTask(uint256 taskId, bytes32 reason) external {
        Task storage task = _tasks[taskId];
        require(task.status == TaskStatus.Completed, "Not completed");
        require(task.poster == msg.sender, "Not poster");
        task.status = TaskStatus.Disputed;
        emit TaskDisputed(taskId, msg.sender);
    }

    /// @inheritdoc ITaskManager
    function cancelTask(uint256 taskId) external {
        Task storage task = _tasks[taskId];
        require(task.poster == msg.sender, "Not poster");
        require(task.status == TaskStatus.Open || task.status == TaskStatus.Claimed, "Cannot cancel");
        task.status = TaskStatus.Cancelled;
        (bool success, ) = payable(msg.sender).call{value: task.payment}("");
        require(success, "Refund failed");
        emit TaskCancelled(taskId);
    }

    /// @inheritdoc ITaskManager
    function releasePayment(uint256 taskId) external {
        Task storage task = _tasks[taskId];
        require(task.poster == msg.sender, "Not poster");
        require(task.status == TaskStatus.Completed, "Not completed");
        uint256 amount = task.payment;
        task.payment = 0;
        (bool success, ) = payable(task.claimer).call{value: amount}("");
        require(success, "Payment failed");
        emit PaymentReleased(taskId, task.claimer, amount);
    }

    /// @inheritdoc ITaskManager
    function getTask(uint256 taskId) external view returns (Task memory) {
        require(taskId > 0 && taskId < _nextTaskId, "Invalid task");
        return _tasks[taskId];
    }

    /// @inheritdoc ITaskManager
    function totalTasks() external view returns (uint256) {
        return _nextTaskId - 1;
    }
}
