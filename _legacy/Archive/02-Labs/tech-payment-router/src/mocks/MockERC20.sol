// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/// @notice Mock ERC20 for $TECH token testing
contract MockERC20 is ERC20 {
    constructor() ERC20("GenTech Token", "$TECH") {}

    function decimals() public view override returns (uint8) {
        return 18;
    }

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}
