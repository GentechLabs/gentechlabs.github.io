// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title AgentCatcher - On-chain token risk scoring via Somnia AI agents
/// @notice Uses dual-agent pattern: fetches security data via JSON API, classifies via LLM
contract AgentCatcher {
    // -- Somnia Platform --
    address public constant PLATFORM = 0x037Bb9C718F3f7fe5eCBDB0b600D607b52706776;
    
    // -- Agent IDs (testnet) --
    uint256 public constant JSON_API_AGENT_ID = 13174292974160097713;
    uint256 public constant LLM_AGENT_ID = 12847293847561029384;
    
    // -- Risk levels --
    string[] private RISK_LEVELS = ["safe", "low_risk", "moderate_risk", "high_risk", "scam"];
    
    // -- Structs --
    struct AnalysisRequest {
        address requester;
        string tokenAddress;
        uint256 chainId;
        uint256 timestamp;
        bool completed;
        string riskLevel;
        int256 riskScore;
    }
    
    // -- State --
    mapping(uint256 => AnalysisRequest) public requests;
    uint256 public requestCount;
    
    // Maps Somnia platform request ID -> our analysis request ID (for callback chaining)
    mapping(uint256 => uint256) public agentRequestToAnalysis;
    
    // -- Events --
    event AnalysisRequested(
        uint256 requestId,
        address requester,
        string tokenAddress,
        uint256 chainId
    );
    
    event RiskScored(
        uint256 requestId,
        string tokenAddress,
        string riskLevel,
        int256 riskScore
    );
    
    event RequestFailed(uint256 requestId, string reason);
    
    // -- Helpers --
    function getRequiredDeposit() external view returns (uint256) {
        return IAgentRequester(PLATFORM).getRequestDeposit();
    }
    
    function getRiskLevels() external view returns (string[] memory) {
        return RISK_LEVELS;
    }
    
    /// @notice Request risk analysis for a token
    /// @param _tokenAddress Token contract address
    /// @param _chainId GoPlus chain ID (1=ETH, 56=BSC, 137=Polygon, etc.)
    function requestAnalysis(string calldata _tokenAddress, uint256 _chainId) external payable {
        uint256 deposit = IAgentRequester(PLATFORM).getRequestDeposit();
        require(msg.value >= deposit, "Insufficient deposit");
        
        requestCount++;
        uint256 reqId = requestCount;
        
        requests[reqId] = AnalysisRequest({
            requester: msg.sender,
            tokenAddress: _tokenAddress,
            chainId: _chainId,
            timestamp: block.timestamp,
            completed: false,
            riskLevel: "",
            riskScore: -1
        });
        
        emit AnalysisRequested(reqId, msg.sender, _tokenAddress, _chainId);
        
        // Phase 1: Fetch GoPlus security data via JSON API
        string memory url = string.concat(
            "https://api.gopluslabs.io/api/v1/token_security/",
            _toString(_chainId),
            "?contract_addresses=",
            _tokenAddress
        );
        
        bytes memory payload = abi.encodeWithSelector(
            IJsonApiAgent.fetchString.selector,
            url,
            "$"
        );
        
        uint256 agentReqId = IAgentRequester(PLATFORM).createRequest{value: deposit}(
            JSON_API_AGENT_ID,
            address(this),
            this.handleDataFetched.selector,
            payload
        );
        
        // Map the Somnia agent request ID to our analysis request ID
        agentRequestToAnalysis[agentReqId] = reqId;
    }
    
    /// @notice Phase 1 callback - received raw API data, forward to LLM
    function handleDataFetched(
        uint256 agentReqId,
        Response[] memory responses,
        ResponseStatus status,
        Request memory
    ) external {
        require(msg.sender == PLATFORM, "Only platform");
        
        uint256 reqId = agentRequestToAnalysis[agentReqId];
        require(reqId > 0 && reqId <= requestCount, "Invalid request");
        
        if (status != ResponseStatus.Success || responses.length == 0) {
            requests[reqId].riskLevel = "unknown";
            requests[reqId].completed = true;
            emit RequestFailed(reqId, "API fetch failed");
            return;
        }
        
        string memory rawData = abi.decode(responses[0].result, (string));
        _requestLLMScore(reqId, rawData);
    }
    
    /// @notice Phase 2: Send security data to LLM for risk classification
    function _requestLLMScore(uint256 reqId, string memory rawData) internal {
        uint256 deposit = IAgentRequester(PLATFORM).getRequestDeposit();
        
        string memory prompt = string.concat(
            "Analyze this token security data and return ONLY the risk level. ",
            "Data: ",
            rawData
        );
        
        string[] memory allowedValues = new string[](5);
        allowedValues[0] = "safe";
        allowedValues[1] = "low_risk";
        allowedValues[2] = "moderate_risk";
        allowedValues[3] = "high_risk";
        allowedValues[4] = "scam";
        
        bytes memory payload = abi.encodeWithSelector(
            ILLMAgent.inferString.selector,
            prompt,
            "You are a DeFi security analyst. Analyze the token security data and classify its risk level.",
            false,
            allowedValues
        );
        
        uint256 agentReqId = IAgentRequester(PLATFORM).createRequest{value: deposit}(
            LLM_AGENT_ID,
            address(this),
            this.handleClassification.selector,
            payload
        );
        
        // Map LLM agent request ID to our analysis request ID
        agentRequestToAnalysis[agentReqId] = reqId;
    }
    
    /// @notice Phase 2 callback - LLM returned classification
    function handleClassification(
        uint256 agentReqId,
        Response[] memory responses,
        ResponseStatus status,
        Request memory
    ) external {
        require(msg.sender == PLATFORM, "Only platform");
        
        uint256 reqId = agentRequestToAnalysis[agentReqId];
        require(reqId > 0 && reqId <= requestCount, "Invalid request");
        
        if (status != ResponseStatus.Success || responses.length == 0) {
            requests[reqId].riskLevel = "unknown";
            requests[reqId].completed = true;
            emit RequestFailed(reqId, "LLM classification failed");
            return;
        }
        
        string memory riskLevel = abi.decode(responses[0].result, (string));
        int256 riskScore = _riskLevelToScore(riskLevel);
        
        requests[reqId].riskLevel = riskLevel;
        requests[reqId].riskScore = riskScore;
        requests[reqId].completed = true;
        
        emit RiskScored(reqId, requests[reqId].tokenAddress, riskLevel, riskScore);
    }
    
    function _riskLevelToScore(string memory level) internal pure returns (int256) {
        if (keccak256(bytes(level)) == keccak256(bytes("safe"))) return 100;
        if (keccak256(bytes(level)) == keccak256(bytes("low_risk"))) return 75;
        if (keccak256(bytes(level)) == keccak256(bytes("moderate_risk"))) return 50;
        if (keccak256(bytes(level)) == keccak256(bytes("high_risk"))) return 25;
        if (keccak256(bytes(level)) == keccak256(bytes("scam"))) return 0;
        return -1;
    }
    
    function _toString(uint256 value) internal pure returns (string memory) {
        if (value == 0) return "0";
        uint256 temp = value;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
        bytes memory buffer = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        return string(buffer);
    }
}

// -- Interfaces --
interface IAgentRequester {
    function createRequest(
        uint256 agentId,
        address callbackAddress,
        bytes4 callbackSelector,
        bytes calldata payload
    ) external payable returns (uint256 requestId);
    function getRequestDeposit() external view returns (uint256);
}

interface IJsonApiAgent {
    function fetchString(string calldata url, string calldata selector) external returns (string memory);
}

interface ILLMAgent {
    function inferString(
        string calldata prompt,
        string calldata system,
        bool chainOfThought,
        string[] calldata allowedValues
    ) external returns (string memory);
}

struct Response {
    bytes result;
    bytes proof;
}

enum ResponseStatus { Success, Timeout, Error, InsufficientBudget, UnsupportedMethod, ConsensusFailure }

struct Request {
    uint256 id;
    uint256 agentId;
    address requester;
    bytes payload;
    address callbackAddress;
    bytes4 callbackSelector;
    uint256 deposit;
    uint256 timestamp;
    ResponseStatus status;
}
