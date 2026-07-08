// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {OFT} from "@layerzerolabs/oft-evm/contracts/OFT.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {ERC20Pausable} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";

contract Kite is OFT, ERC20Pausable {
    error AlreadyInitialized();

    error OnlyNativeChain();

    uint256 constant TOTAL_SUPPLY = 10_000_000_000 * (10 ** 18);

    bool public isNativeChain;

    bool internal _isInitialized;

    constructor(
        address _lzEndpoint,
        address _owner,
        bool _isNativeChain
    ) OFT("Kite", "KITE", _lzEndpoint, _owner) Ownable(_owner) {
        isNativeChain = _isNativeChain;
    }

    function initialize() external onlyOwner {
        if (_isInitialized) revert AlreadyInitialized();
        if (!isNativeChain) revert OnlyNativeChain();
        _mint(msg.sender, TOTAL_SUPPLY);
        _isInitialized = true;
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    function _update(address from, address to, uint256 value) internal override(ERC20, ERC20Pausable) {
        super._update(from, to, value);
    }
}
