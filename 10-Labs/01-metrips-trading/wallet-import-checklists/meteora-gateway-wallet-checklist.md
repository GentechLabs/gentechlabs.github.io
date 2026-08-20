# Meteora Race — Gateway Wallet Import + Fund + Verify Checklist

**Date:** 2026-08-20 · **Deadline:** 2026-08-31 (Agent Builders Cup)
**Status:** ✅ Step 3 (import) DONE via Option A. Remaining: fund + verify + race.

**Import done Aug 20 via Option A (hummingbot-api GatewayClient):**
- `add_wallet(solana, base58_priv, set_default=True)` → `{'address': 'DSvtQzkw...C26V'}`
- Persisted: `/conf/wallets/solana/DSvtQzkw...C26V.json` (encrypted, mode 600)
- Verified: `get_wallets` → solana wallet present; `get_default_wallet_address('solana')` → DSvtQzkw (no longer placeholder)
- Probe: ping=True (mTLS certs/auth healthy). Temp probe scripts cleaned up. Secret not persisted.

## 📌 Key facts (verified this session)

- **Signing path:** consigliere strategy → HummingbotAPIClient → Hummingbot API
  (8002) → Gateway (15888, container `gateway`) → signs on-chain.
- **Gateway does NOT read loose keypair files.** It signs with the wallet in its
  encrypted store (`/conf/wallets/{chain}/{address}.json`). That store is EMPTY now.
- **Gateway `/wallet/add` endpoint accepts a Solana private key as BASE58**
  (`bs58.decode` → `Keypair.fromSecretKey`). It encrypts it with the gateway's
  wallet-encryption key before writing `{address}.json`.
- **Our signing keypair** already generated + verified:
  - Address: `DSvtQzkwS5USiCNCQyctf3BQP4vu5upDYkb1TUk5C26V`
  - File: `/root/.solana-trade/trade-keypair.json` (chmod 600)
  - On-chain balance: 0 SOL (brand new — MUST be funded)

## 2. Derive the base58 private key (from keypair file, no storage)

```bash
cd /root && python3 -c "
import json
from solders.keypair import Keypair
kb = json.load(open('/root/.solana-trade/trade-keypair.json'))
kp = Keypair.from_bytes(bytes(kb))
alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def b58(b):
    n=int.from_bytes(b,'big'); s=''; pad=0
    while n>0: n,r=divmod(n,58); s=alphabet[r]+s
    for x in b:
        if x==0: pad+=1
        else: break
    return '1'*pad+s
print('ADDRESS:', str(kp.pubkey()))
print('BASE58_PRIV:', b58(bytes(kp)))
"
```

**Treat the printed BASE58_PRIV as a secret — do not paste into chat/logs.**

## 3. Import into the gateway (manual, interactive)

The gateway `/wallet/add` endpoint is auth-gated (needs the gateway API
username/password + a session from `GATEWAY_PASSPHRASE`). Run it via the
gateway's setup wizard or a direct authenticated call. This step requires
human input of the gateway passphrase and is NOT something to run unattended.

**Checklist:**
- [ ] Gateway API + gateway container (`gateway`) is UP (port 15888)
- [ ] Have gateway API username/password + GATEWAY_PASSPHRASE ready
- [ ] `POST /wallet/add` with `{"chain":"solana","privateKey":"<BASE58_PRIV>","setDefault":true}`
- [ ] Confirm response `{"address":"DSvtQkz...C26"}` matches
- [ ] Verify `/conf/wallets/solana/DSvtQkz...C26.json` now exists (encrypted)

## 4. Fund the gateway-derived address

Fund `DSvtQkz...C26` (the address the executor will sign with) on Solana mainnet:

- **Recommended:** ~$25-30 SOL. Breakdown (from `consigliere`/`lp_slot_operator`):
  - `min_wallet_sol_reserve`: 0.3 SOL
  - Meteora slot rent: ~0.057 SOL/slot × 3 slots ≈ 0.17 SOL
  - Swap + LP open fees + Jupiter slippage buffer: rest
- Smaller is fine if we start with 1-2 slots, but reserve buffer + rent is a must.

## 5. Verify on-chain (the real test — "funded ≠ usable")

```bash
curl -s https://api.mainnet-beta.solana.com -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"getBalance","params":["DSvtQkz...C26"]}'
# expect value > 0
```

- [ ] `getBalance` > 0 (funded)
- [ ] Gateway can sign a test tx (e.g. a small Jupiter quote/swap or `getPortfolioOverview`)
- [ ] `manage_executors(search, executor_types=["lp_executor"])` returns the RUNNING set — proves the gateway wallet is the one the strategy sees

## 6. Race (Botcamp Step 2 — human action on dashboard)

- [ ] Apply to Teams before Aug 31
- [ ] Funded race wallet is the one shown to the judge

## Pitfalls (from the strategy + skill)

- **NEVER pass a swap's reported fill straight to `base_amount`** — Jupiter
  takes its cut; open fails on-chain if you ask the pool for tokens you don't
  have. Haircut: `base_amount = executed_amount_base × 0.995`.
- **A keypair file existing ≠ it's wired in.** The gateway only signs with its
  encrypted store. If we ever import a key into the gateway, that becomes the
  funded signing wallet — not the loose file.
- **Verifying the wallet was truly created:** `GET /accounts/gateway/wallets`
  should no longer return `[]` after the import.
