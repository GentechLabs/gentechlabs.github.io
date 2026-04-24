# 🎫 Sign-Up Checklist — Arc Hackathon

**Date:** April 16, 2026
**Status:** Ready to execute

---

## 🔐 Accounts You Need

### 1. Circle Developer Platform (USDC)
**Why:** For USDC integration in escrow contracts
**Link:** https://circle.com/developers

**What to do:**
- Create account
- Get API keys (for testnet)
- Access USDC faucet for testing
- Documentation: https://developers.circle.com

---

### 2. Coinbase Developer Platform (x402)
**Why:** x402 protocol is maintained by Coinbase
**Link:** https://portal.cdp.coinbase.com

**What to do:**
- Create account
- Get API keys
- Access x402 documentation
- Join Discord: https://discord.gg/cdp

---

### 3. Solana Wallet (for x402)
**Why:** Dexter SDK supports Solana payments
**Options:**
- **Phantom:** https://phantom.app
- **Solflare:** https://solflare.com

**What to do:**
- Install browser extension
- Create wallet
- Save private key (for dev)
- Get devnet SOL: https://faucet.solana.com

---

### 4. EVM Wallet (for Avalanche/Base)
**Why:** Multi-chain support for x402
**Options:**
- **MetaMask:** https://metamask.io
- **Rabby:** https://rabby.io

**What to do:**
- Install browser extension
- Create wallet
- Export private key (for dev)
- Add Avalanche Fuji testnet
- Get testnet AVAX: https://faucet.avax.network

---

### 5. GitHub (Already done ✅)
**Status:** ProtoJay4789/arc-hackathon created

---

### 6. Hackathon Registration
**Check:** Are you registered for the Arc Hackathon?
**Link:** https://arc.dev/hackathon (verify current URL)

**What to do:**
- Register as participant
- Join hackathon Discord
- Review rules + timeline
- Submit project when ready

---

## 🧪 Testnet Tokens You Need

### Avalanche Fuji Testnet
- **Faucet:** https://faucet.avax.network
- **Amount:** 2-5 AVAX for testing
- **Use:** Gas fees for contract deployment

### Base Sepolia Testnet
- **Faucet:** https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet
- **Amount:** 0.1-0.5 ETH
- **Use:** Alternative testnet for x402

### Solana Devnet
- **Faucet:** https://faucet.solana.com
- **Amount:** 2-5 SOL
- **Use:** x402 Solana payments testing

### USDC Testnet
- **From Circle:** https://faucet.circle.com
- **Amount:** 100-500 USDC
- **Use:** Escrow contract testing

---

## 📋 Quick Sign-Up Order

**Do this in order (30-45 min total):**

1. **Circle Developer** (5 min)
   - https://circle.com/developers
   - Get USDC testnet tokens

2. **Coinbase Developer** (5 min)
   - https://portal.cdp.coinbase.com
   - Get x402 API access

3. **MetaMask** (5 min)
   - https://metamask.io
   - Create wallet, save private key

4. **Phantom** (5 min)
   - https://phantom.app
   - Create wallet, save private key

5. **Avalanche Faucet** (2 min)
   - https://faucet.avax.network
   - Get 2-5 testnet AVAX

6. **USDC Faucet** (2 min)
   - https://faucet.circle.com
   - Get 100 testnet USDC

7. **Hackathon Registration** (5 min)
   - Verify you're registered
   - Join Discord

8. **Save Everything** (5 min)
   - Create `.env` file:
   ```
   SOLANA_PRIVATE_KEY=your_solana_key
   EVM_PRIVATE_KEY=your_evm_key
   CIRCLE_API_KEY=your_circle_key
   COINBASE_API_KEY=your_coinbase_key
   ```

---

## ⚠️ Security Notes

**NEVER share:**
- Private keys
- Seed phrases
- API keys (keep in `.env` file)

**ALWAYS:**
- Use testnet for development
- Keep `.env` in `.gitignore`
- Use different wallets for dev vs production

---

## ✅ Done Checklist

After signing up, check these off:

- [ ] Circle Developer account created
- [ ] Coinbase Developer account created
- [ ] MetaMask wallet created
- [ ] Phantom wallet created
- [ ] Avalanche testnet AVAX received
- [ ] USDC testnet tokens received
- [ ] Hackathon registered
- [ ] `.env` file created with all keys
- [ ] Joined Arc Hackathon Discord

---

**Time needed:** 30-45 minutes
**After this:** Ready to start coding!

---

**Next task:** Extend AgentEscrow for USDC payments (once you have keys)
