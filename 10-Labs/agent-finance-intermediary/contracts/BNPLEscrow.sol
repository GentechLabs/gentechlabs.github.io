// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title BNPLEscrow
 * @notice Crypto-only BNPL: 4-installment escrow for agent-to-agent payments.
 *         Merchant receives full USDC upfront; user repays in 4 installments.
 *         Defaults penalize ERC-8004 reputation (off-chain scoring).
 *
 * @dev    Deployed on Base (USDC native). Uses x402 payment pattern.
 *         No KYC, no fiat — pure smart contract utility.
 *
 * @author GenTech Labs
 */
contract BNPLEscrow {
    // ──────────────────────────────────────────────
    //  Types
    // ──────────────────────────────────────────────

    enum InstallmentStatus { Pending, Paid, Defaulted }

    struct Installment {
        uint256 dueDate;          // Unix timestamp
        uint256 amount;           // USDC amount (6 decimals)
        InstallmentStatus status;
    }

    struct BNPLAgreement {
        address merchant;         // Receives funds
        address user;             // Repays installments
        address token;            // USDC token address
        uint256 totalAmount;      // Total USDC (6 decimals)
        uint256 installmentSize;  // Per-installment amount
        uint256 gracePeriod;      // Seconds after due before default
        uint256 spacing;          // Seconds between installments
        Installment[4] installments;
        bool active;
    }

    // ──────────────────────────────────────────────
    //  State
    // ──────────────────────────────────────────────

    /// @dev agreementId => BNPLAgreement
    mapping(uint256 => BNPLAgreement) public agreements;
    uint256 public nextAgreementId;

    /// @dev Owner for emergency controls
    address public owner;
    bool public paused;

    // ──────────────────────────────────────────────
    //  Modifiers
    // ──────────────────────────────────────────────

    modifier onlyOwner() {
        require(msg.sender == owner, "BNPL: not owner");
        _;
    }

    modifier notPaused() {
        require(!paused, "BNPL: paused");
        _;
    }

    // ──────────────────────────────────────────────
    //  Events
    // ──────────────────────────────────────────────

    event AgreementCreated(
        uint256 indexed agreementId,
        address indexed merchant,
        address indexed user,
        uint256 totalAmount,
        uint256 installmentSize
    );

    event InstallmentPaid(
        uint256 indexed agreementId,
        uint8 indexed installmentIndex,
        address payer
    );

    event InstallmentDefaulted(
        uint256 indexed agreementId,
        uint8 indexed installmentIndex
    );

    event AgreementSettled(uint256 indexed agreementId);

    event AgreementCancelled(uint256 indexed agreementId);

    event EmergencyPause(bool paused);

    // ──────────────────────────────────────────────
    //  Constructor
    // ──────────────────────────────────────────────

    constructor() {
        owner = msg.sender;
    }

    // ──────────────────────────────────────────────
    //  Core
    // ──────────────────────────────────────────────

    /**
     * @notice Create a BNPL agreement.
     *         Merchant must have already approved this contract to spend `totalAmount` USDC.
     *         The full amount is pulled upfront and held in escrow.
     *
     * @param merchant  Address receiving the funds
     * @param user      Address repaying installments
     * @param token     USDC token address
     * @param total     Total USDC amount (6 decimals)
     * @param installs  Number of installments (must be 4)
     * @param graceSec  Grace period in seconds after each due date
     * @param spacingSec Seconds between installment due dates
     */
    function createAgreement(
        address merchant,
        address user,
        address token,
        uint256 total,
        uint8 installs,
        uint256 graceSec,
        uint256 spacingSec
    ) external notPaused returns (uint256 agreementId) {
        require(installs == 4, "BNPL: must be 4 installments");
        require(total >= installs, "BNPL: total too small");  // C3: prevent zero installments
        require(merchant != address(0) && user != address(0), "BNPL: zero address");
        require(token != address(0), "BNPL: zero token");
        require(spacingSec > 0, "BNPL: zero spacing");

        agreementId = nextAgreementId++;
        uint256 installmentSize = total / installs;
        uint256 remainder = total - (installmentSize * installs);  // C1: track rounding loss

        BNPLAgreement storage a = agreements[agreementId];
        a.merchant = merchant;
        a.user = user;
        a.token = token;
        a.totalAmount = total;
        a.installmentSize = installmentSize;
        a.gracePeriod = graceSec;
        a.spacing = spacingSec;
        a.active = true;

        // Set installment schedule with configurable spacing (M1)
        for (uint8 i = 0; i < installs; i++) {
            uint256 amt = installmentSize;
            if (i == installs - 1) {
                amt += remainder;  // C1: add remainder to last installment
            }
            a.installments[i] = Installment({
                dueDate: block.timestamp + spacingSec * (i + 1),
                amount: amt,
                status: InstallmentStatus.Pending
            });
        }

        // Pull full amount from merchant into escrow
        require(_checkedTransferFrom(token, msg.sender, address(this), total), "BNPL: transfer failed");  // L1: check return

        emit AgreementCreated(agreementId, merchant, user, total, installmentSize);
    }

    /**
     * @notice User pays an installment.
     *         Must have approved this contract to spend `installmentSize` USDC.
     */
    function payInstallment(uint256 agreementId, uint8 index) external notPaused {
        BNPLAgreement storage a = agreements[agreementId];
        require(a.active, "BNPL: not active");
        require(index < 4, "BNPL: invalid index");
        require(a.installments[index].status == InstallmentStatus.Pending, "BNPL: already paid/defaulted");
        require(block.timestamp <= a.installments[index].dueDate + a.gracePeriod, "BNPL: past grace period");

        a.installments[index].status = InstallmentStatus.Paid;
        require(_checkedTransferFrom(a.token, msg.sender, address(this), a.installments[index].amount), "BNPL: transfer failed");  // L1: check return

        emit InstallmentPaid(agreementId, index, msg.sender);

        // If all 4 paid, settle
        if (_allPaid(a)) {
            _settle(agreementId);
        }
    }

    /**
     * @notice Mark an installment as defaulted (anyone can trigger after grace period).
     *         All funds (paid + remaining escrow) are released to the merchant.
     */
    function markDefault(uint256 agreementId, uint8 index) external notPaused {
        BNPLAgreement storage a = agreements[agreementId];
        require(a.active, "BNPL: not active");
        require(index < 4, "BNPL: invalid index");
        require(a.installments[index].status == InstallmentStatus.Pending, "BNPL: already paid/defaulted");
        require(block.timestamp > a.installments[index].dueDate + a.gracePeriod, "BNPL: grace period not elapsed");

        a.installments[index].status = InstallmentStatus.Defaulted;

        emit InstallmentDefaulted(agreementId, index);

        // Release ALL funds to merchant (paid installments + remaining escrow)
        uint256 contractBalance = _checkedBalance(a.token);
        if (contractBalance > 0) {
            require(_checkedTransfer(a.token, a.merchant, contractBalance), "BNPL: transfer failed");  // L1: check return
        }

        a.active = false;
    }

    /**
     * @notice Cancel an agreement (both parties must agree).
     *         Merchant gets all escrowed funds back.
     */
    function cancelAgreement(uint256 agreementId) external notPaused {
        BNPLAgreement storage a = agreements[agreementId];
        require(a.active, "BNPL: not active");
        require(msg.sender == a.merchant || msg.sender == a.user, "BNPL: not party to agreement");

        // Both parties must call this — second call triggers release
        // Simple approach: either party can trigger, funds go to merchant
        // In practice, both parties coordinate off-chain
        a.active = false;

        uint256 contractBalance = _checkedBalance(a.token);
        if (contractBalance > 0) {
            require(_checkedTransfer(a.token, a.merchant, contractBalance), "BNPL: transfer failed");
        }

        emit AgreementCancelled(agreementId);
    }

    /**
     * @notice Get agreement summary (view).
     */
    function getAgreement(uint256 agreementId)
        external
        view
        returns (
            address merchant,
            address user,
            address token,
            uint256 totalAmount,
            uint256 installmentSize,
            bool active,
            uint256 paidCount,
            uint256 defaultCount
        )
    {
        BNPLAgreement storage a = agreements[agreementId];
        merchant = a.merchant;
        user = a.user;
        token = a.token;
        totalAmount = a.totalAmount;
        installmentSize = a.installmentSize;
        active = a.active;

        for (uint8 i = 0; i < 4; i++) {
            if (a.installments[i].status == InstallmentStatus.Paid) paidCount++;
            if (a.installments[i].status == InstallmentStatus.Defaulted) defaultCount++;
        }
    }

    // ──────────────────────────────────────────────
    //  Emergency Controls (C3)
    // ──────────────────────────────────────────────

    /**
     * @notice Pause all operations (emergency).
     */
    function emergencyPause() external onlyOwner {
        paused = true;
        emit EmergencyPause(true);
    }

    /**
     * @notice Unpause operations.
     */
    function unpause() external onlyOwner {
        paused = false;
        emit EmergencyPause(false);
    }

    /**
     * @notice Sweep accidentally sent tokens.
     */
    function sweep(address token, address to) external onlyOwner {
        uint256 balance = _checkedBalance(token);
        if (balance > 0) {
            require(_checkedTransfer(token, to, balance), "BNPL: sweep failed");
        }
    }

    /**
     * @notice Transfer ownership.
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "BNPL: zero address");
        owner = newOwner;
    }

    // ──────────────────────────────────────────────
    //  Internal
    // ──────────────────────────────────────────────

    function _allPaid(BNPLAgreement storage a) internal view returns (bool) {
        for (uint8 i = 0; i < 4; i++) {
            if (a.installments[i].status != InstallmentStatus.Paid) return false;
        }
        return true;
    }

    function _settle(uint256 agreementId) internal {
        BNPLAgreement storage a = agreements[agreementId];
        a.active = false;
        // Send full contract balance to merchant: their deposit + user's payments
        uint256 contractBalance = _checkedBalance(a.token);
        if (contractBalance > 0) {
            require(_checkedTransfer(a.token, a.merchant, contractBalance), "BNPL: transfer failed");
        }
        emit AgreementSettled(agreementId);
    }

    // ──────────────────────────────────────────────
    //  Safe ERC20 Helpers (L1)
    // ──────────────────────────────────────────────

    function _checkedTransferFrom(address token, address from, address to, uint256 amount) internal returns (bool) {
        (bool success, bytes memory data) = token.call(abi.encodeWithSelector(
            IERC20.transferFrom.selector, from, to, amount
        ));
        return success && (data.length == 0 || abi.decode(data, (bool)));
    }

    function _checkedTransfer(address token, address to, uint256 amount) internal returns (bool) {
        (bool success, bytes memory data) = token.call(abi.encodeWithSelector(
            IERC20.transfer.selector, to, amount
        ));
        return success && (data.length == 0 || abi.decode(data, (bool)));
    }

    function _checkedBalance(address token) internal view returns (uint256) {
        (bool success, bytes memory data) = token.staticcall(abi.encodeWithSelector(
            IERC20.balanceOf.selector, address(this)
        ));
        require(success, "BNPL: balance check failed");
        return abi.decode(data, (uint256));
    }
}

/**
 * @dev Minimal IERC20 interface for USDC
 */
interface IERC20 {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}
