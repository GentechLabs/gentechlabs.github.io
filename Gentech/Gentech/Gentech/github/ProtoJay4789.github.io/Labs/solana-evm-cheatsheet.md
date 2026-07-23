# EVM → Solana Cheat Sheet

*For Solidity devs learning Solana/Anchor. Keep this open while coding.*

---

## 🧠 Mental Model

| EVM | Solana |
|---|---|
| Contract-centric | Account-centric |
| Code + data together | Code (programs) ≠ Data (accounts) |
| State lives in contract storage | State lives in separate PDAs |
| Contracts are stateful | Programs are stateless |
| Sequential execution | Parallel execution (Sealevel) |

---

## 📦 Programs = Contracts (but different)

```
// EVM — deploy a contract, it has storage
contract MyVault {
    uint256 public balance; // lives IN the contract
}

// Solana — program has NO storage
// Data lives in accounts you create and pass in
#[program]
pub mod my_vault {
    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        // write to an account, not to "self"
        ctx.accounts.vault.balance = 0;
        Ok(())
    }
}
```

---

## 🗂️ Account Types

| Type | Description | EVM Equivalent |
|---|---|---|
| **System Account** | Owned by System Program, holds SOL | EOA |
| **Program Account** | Stores executable code | Contract bytecode |
| **Data Account (PDA)** | Stores state, owned by a program | Contract storage slots |
| **Token Account** | SPL token balance for one owner | ERC-20 balance mapping |

---

## 🔑 PDAs (Program Derived Addresses)

The big brain-melter. PDAs are accounts derived from:
```rust
let (pda, bump) = Pubkey::find_program_address(
    &[b"vault", user.key().as_ref()], // seeds
    program_id
);
```

- **Deterministic**: same seeds + program = same address every time
- **No private key**: can't sign, only the owning program can write
- **Use them for**: storing state, authority delegation, mapping

**EVM equivalent**: `mapping(address => uint256)` — but instead of a mapping, you derive a whole account address per user.

---

## 💰 Tokens

| Concept | EVM (ERC-20) | Solana (SPL) |
|---|---|---|
| Token standard | Deploy a new contract per token | One program manages ALL tokens |
| Create token | Deploy ERC-20 contract | `spl-token create-mint` → creates mint account |
| User balance | `balanceOf(user)` in contract | Associated Token Account (ATA) per user per token |
| Transfer | `transfer(to, amount)` | CPI to Token Program with accounts |
| Mint authority | Set in constructor | Configured on mint creation |

---

## 🔄 Cross-Program Invocation (CPI)

```rust
// Solana — call another program
anchor_spl::token::transfer(
    CpiContext::new(
        ctx.accounts.token_program.to_account_info(),
        anchor_spl::token::Transfer {
            from: ctx.accounts.vault_token.to_account_info(),
            to: ctx.accounts.user_token.to_account_info(),
            authority: ctx.accounts.vault.to_account_info(),
        },
    ),
    amount,
)?;
```

**EVM equivalent**: `IERC20(token).transfer(to, amount)`

CPI is more verbose — you pass full account structs. But it's also what makes Solana composability work without reentrancy.

---

## 🛡️ Security Differences

| EVM Concern | Solana Equivalent |
|---|---|
| Reentrancy | Not possible (no cross-tx state sharing) |
| `tx.origin` phishing | N/A |
| Integer overflow | Rust panics (or use checked math) |
| Access control | Check account ownership + signer checks |
| **NEW**: Account validation | Must verify every account's owner, signer, mutability |
| **NEW**: Account stuffing | Attacker can pass fake accounts — validate seeds |

**Anchor helps**: `#[account(init, payer = user, ...)]` auto-validates account creation.

---

## 🛠️ Tooling Map

| EVM Tool | Solana Equivalent |
|---|---|
| Solidity | Rust + Anchor |
| Foundry (forge/cast) | Anchor CLI + Solana CLI |
| Hardhat | Anchor (has testing built in) |
| Remix | Solana Playground (solana playground.com) |
| ethers.js | @solana/web3.js |
| OpenZeppelin | Anchor (built-in SPL token support) |
| Sepolia testnet | Devnet |
| Etherscan | Solscan / Explorer.solana.com |
| MetaMask | Phantom / Backpack |
| `forge test` | `anchor test` |
| `forge build` | `anchor build` |

---

## 📝 Anchor Program Structure

```
my-program/
├── Anchor.toml          # like hardhat.config.js
├── Cargo.toml           # Rust dependencies
├── programs/
│   └── my-program/
│       └── src/
│           └── lib.rs   # your program (contract)
├── tests/
│   └── my-program.ts    # TypeScript tests
├── app/                 # frontend (optional)
└── target/              # build artifacts
    └── deploy/          # .so file (your compiled program)
```

---

## ⚡ Quick Syntax Comparison

### Variable declaration
```solidity
// Solidity
uint256 public balance;
address public owner;
```
```rust
// Rust/Anchor
pub balance: u64,
pub owner: Pubkey,
```

### Structs
```solidity
// Solidity
struct Vault {
    uint256 balance;
    address owner;
}
```
```rust
// Rust/Anchor
#[account]
pub struct Vault {
    pub balance: u64,
    pub owner: Pubkey,
}
```

### Error handling
```solidity
// Solidity
require(balance >= amount, "Insufficient balance");
// or custom errors
error InsufficientBalance();
```
```rust
// Rust/Anchor
#[error_code]
pub enum VaultError {
    #[msg("Insufficient balance")]
    InsufficientBalance,
}
require!(balance >= amount, VaultError::InsufficientBalance);
```

### Modifiers → Guards
```solidity
// Solidity
modifier onlyOwner() { require(msg.sender == owner); _; }
```
```rust
// Rust/Anchor — no modifiers, use constraints
#[account(mut, has_one = owner)]
pub vault: Account<'data, Vault>,
```

---

## 🚀 Deploy Flow

```bash
# EVM (Foundry)
forge build
forge script script/Deploy.s.sol --rpc-url $RPC --private-key $KEY --broadcast

# Solana (Anchor)
anchor build
anchor deploy --provider.cluster devnet
# programs deploy as .so files to a program address
```

---

## 🧪 Testing Comparison

```solidity
// Foundry
function testDeposit() public {
    vault.deposit{value: 1 ether}();
    assertEq(vault.balance(), 1 ether);
}
```
```typescript
// Anchor (TypeScript)
it("deposits", async () => {
    await program.methods
        .deposit(new BN(1_000_000_000))
        .accounts({ vault: vaultPda, user: provider.wallet.publicKey })
        .rpc();
    const vault = await program.account.vault.fetch(vaultPda);
    assert.ok(vault.balance.eq(new BN(1_000_000_000)));
});
```

---

## 🎯 When to Use What

| Scenario | EVM | Solana |
|---|---|---|
| DeFi (lending, AMMs) | ✅ Mature | ✅ Growing |
| NFTs | ✅ | ✅ Cheaper minting |
| High throughput needed | ❌ Limited by gas | ✅ Parallel execution |
| Security audit ecosystem | ✅ Massive | 🟡 Growing |
| Composability / DeFi legos | ✅ Deep | ✅ Different but works |
| Enterprise / permissioned | ✅ | 🟡 |

---

*Last updated: 2026-04-18*
*Source: Dmob research, for Jordan's reference*
