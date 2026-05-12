# Kite AI Bug Bounty — Audit Scope
## Source: https://docs.gokite.ai/kite-chain/3-developing/smart-contracts-list

### 1. Validator Staking Contracts (PRIORITY 1)
| Contract | Address |
|----------|---------|
| KiteStakingManager (Proxy) | 0x7d627b0F5Ec62155db013B8E7d1Ca9bA53218E82 |
| KiteStakingManager (Impl) | 0x065cA4309a5abc9F1cC2d8fA00634BC948C25C6b |
| RewardVault | 0xd26850d11e8412fC6035750BE6A871dff9091FAe |
| FixedAPRRewardCalculator | 0x171eefa30E88f9bca456CEf49c5Df093A516C7c2 |
| ValidatorMessages | 0x9C00629cE712B0255b17A4a657171Acd15720B8C |
| ProxyAdmin | 0x3FA7667FD726F73ef42c66f8715E0C6d37D44905 |

### 2. Staking Vault (LST) Contracts (PRIORITY 2)
| Contract | Address |
|----------|---------|
| StakingVault (Proxy) | 0x23f7b52E2830C66f88EFc1f35b8a6a4AAe218dCA |
| StakingVault (Impl) | 0x69379f875551A505d77876a9363BcDe3dfd00bbe |
| StakingVaultOperations (Impl) | 0xE31b845a6898D165e3dFc2AD4C3D61fE74394817 |

### 3. Tokens on Kite Mainnet
| Token | Address |
|-------|---------|
| WKITE | 0xcc788DC0486CD2BaacFf287eea1902cc09FbA570 |
| USDC.e | 0x7aB6f3ed87C42eF0aDb67Ed95090f8bF5240149e |
| USDT | 0x3Fdd283C4c43A60398bf93CA01a8a8BD773a755b |
| WETH | 0x3D66d6c3201190952e8EA973F59c4428b32D5F9b |

### 4. Algebra DEX Contracts (PRIORITY 3)
| Contract | Address |
|----------|---------|
| AlgebraFactory | 0x10253594A832f967994b44f33411940533302ACb |
| AlgebraPoolDeployer | 0xd7cB0E0692f2D55A17bA81c1fE5501D66774fC4A |
| SwapRouter | 0x03f8B4b140249Dc7B2503C928E7258CCe1d91F1A |
| NonfungiblePositionManager | 0xD637cbc214Bc3dD354aBb309f4fE717ffdD0B28C |
| Multicall3 | 0xE3104A157cc4C0d3c7C3a8c655092668D068c149 |

### 5. KITE Token (Cross-Chain)
| Network | Address |
|---------|---------|
| Ethereum Mainnet | 0x904567252D8F48555b7447c67dCA23F0372E16be |
| BSC Mainnet | 0x904567252D8F48555b7447c67dCA23F0372E16be |
| Avalanche C-Chain | 0x904567252D8F48555b7447c67dCA23F0372E16be |

### 6. LayerZero Bridge Contracts (PRIORITY 4)
| Contract | Address |
|----------|---------|
| EndpointV2 | 0x6F475642a6e85809B1c36Fa62763669b1b48DD5B |
| SendUln302 | 0xC39161c743D0307EB9BCc9FEF03eeb9Dc4802de7 |
| ReceiveUln302 | 0xe1844c5D63a9543023008D332Bd3d2e6f1FE1043 |
| LZ Executor | 0x4208D6E27538189bB48E603D6123A94b8Abe0A0b |
| LZ Dead DVN | 0x6788f52439ACA6BFF597d3eeC2DC9a44B8FEE842 |
| Blocked Message Library | 0xc1ce56b2099ca68720592583c7984cab4b6d7e7a |

### 7. Lucid Bridge Contracts
| Contract | Address |
|----------|---------|
| USDC Controller (Kite) | 0x92E2391d0836e10b9e5EAB5d56BfC286Fadec25b |
| WETH Controller (Kite) | 0x638d1c70c7b047b192eB88657B411F84fAc74681 |
| USDT Controller (Kite) | 0x80bA7204f060Fd321BFE8d4F3aB2E2bF4e6fCe49 |

### Previous Audits (OUT OF SCOPE)
- GoKite Contracts Audit (2025)
- Kite Core Contracts Audit (2025)
- Kite Staking & Rewards Audit (2026)
