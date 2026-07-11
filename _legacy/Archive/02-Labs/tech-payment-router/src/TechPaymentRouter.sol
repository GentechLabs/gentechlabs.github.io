// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "./DiscountCalculator.sol";
import "./BurnSplitter.sol";

/// @title TechPaymentRouter
/// @notice Main entry point for $TECH payments with dynamic discount
/// @dev Users pay with $TECH at a discount; tokens are burned or sent to treasury
contract TechPaymentRouter is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    IERC20 public immutable techToken;
    DiscountCalculator public discountCalculator;
    BurnSplitter public burnSplitter;

    // Per-user cumulative $TECH spent (for loyalty tiers)
    mapping(address => uint256) public cumulativeSpent;

    event PaymentProcessed(
        address indexed user,
        uint256 usdPriceWei,
        uint256 techAmountPaid,
        uint256 discountBps,
        uint256 fullTechPrice,
        string service
    );

    event DiscountCalculatorUpdated(address oldAddr, address newAddr);
    event BurnSplitterUpdated(address oldAddr, address newAddr);

    constructor(
        address _techToken,
        address _discountCalculator,
        address _burnSplitter
    ) Ownable(msg.sender) {
        techToken = IERC20(_techToken);
        discountCalculator = DiscountCalculator(_discountCalculator);
        burnSplitter = BurnSplitter(_burnSplitter);
    }

    /// @notice Pay for a service using $TECH with dynamic discount
    /// @param usdPriceWei Full USD price of the service (18 decimals, e.g., 10e18 for $10)
    /// @param service Description of the service being paid for
    /// @return techAmountPaid How many $TECH tokens were deducted
    /// @return discountBps The discount percentage applied (bps)
    function payWithTech(
        uint256 usdPriceWei,
        string calldata service
    ) external nonReentrant returns (uint256 techAmountPaid, uint256 discountBps) {
        // 1. Calculate discounted amount
        (techAmountPaid, discountBps) = discountCalculator.getDiscountedTechAmount(
            usdPriceWei,
            cumulativeSpent[msg.sender]
        );

        require(techAmountPaid > 0, "TechPaymentRouter: zero payment");

        // 2. Calculate full price for event logging
        uint256 fullTechPrice = (usdPriceWei * 1e18) / _getOraclePrice();

        // 3. Pull tokens and split (burn + treasury)
        // checks-effects-interactions: update state BEFORE external call
        cumulativeSpent[msg.sender] += techAmountPaid;

        burnSplitter.split(msg.sender, techAmountPaid);

        emit PaymentProcessed(
            msg.sender,
            usdPriceWei,
            techAmountPaid,
            discountBps,
            fullTechPrice,
            service
        );
    }

    /// @notice Preview what a payment would cost in $TECH
    function previewPayment(uint256 usdPriceWei) external view returns (
        uint256 techAmount,
        uint256 discountBps,
        uint256 savingsInTech
    ) {
        uint256 fullPrice = (usdPriceWei * 1e18) / _getOraclePrice();
        (techAmount, discountBps) = discountCalculator.getDiscountedTechAmount(
            usdPriceWei,
            cumulativeSpent[msg.sender]
        );
        savingsInTech = fullPrice - techAmount;
    }

    // --- Admin ---

    function setDiscountCalculator(address _addr) external onlyOwner {
        require(_addr != address(0), "TechPaymentRouter: zero address");
        address old = address(discountCalculator);
        discountCalculator = DiscountCalculator(_addr);
        emit DiscountCalculatorUpdated(old, _addr);
    }

    function setBurnSplitter(address _addr) external onlyOwner {
        require(_addr != address(0), "TechPaymentRouter: zero address");
        address old = address(burnSplitter);
        burnSplitter = BurnSplitter(_addr);
        emit BurnSplitterUpdated(old, _addr);
    }

    // --- Internal ---

    function _getOraclePrice() internal view returns (uint256) {
        (, int256 answer,,,) = discountCalculator.priceFeed().latestRoundData();
        uint8 decimals = discountCalculator.priceFeed().decimals();
        return uint256(answer) * (10 ** (18 - decimals));
    }
}
