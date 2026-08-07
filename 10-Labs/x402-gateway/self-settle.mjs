#!/usr/bin/env node
/**
 * GENTECH SELF-SETTLEMENT — OpenDexter Auto-Catalog Trigger
 *
 * Settles ONE real x402 payment against OUR OWN endpoint through Dexter's
 * facilitator. Dexter auto-discovers any API that receives an x402 payment
 * through its facilitator, so this triggers our listing on the OpenDexter
 * marketplace (open.dexter.cash).
 *
 * Prereq: an EVM (Base) wallet that (a) we hold the private key for, and
 * (b) has >= ~0.02 USDC on Base. We settle on Base because our gateway's
 * 402 terms are `eip155:8453` (Base) USDC.
 *
 * Run:
 *   EVM_PRIVATE_KEY=<hex> node self-settle.mjs
 *
 * NOTE on the wallet gap (as of Aug 3, 2026):
 *   - 0x7ebff... (Jordan's owner wallet) HAS 2.97 USDC on Base, but NO key in env.
 *   - 0x3d117... (GTA arb wallet) HAS the key, but only 0.001 USDC.
 *   Either (a) drop ~$2 USDC into 0x3d117, or (b) provide the key for 0x7ebff,
 *   then this script is live.
 *
 * Dependencies (install once): npm i @dexterai/x402 viem
 */

import { payAndFetch, createEvmKeypairWallet } from "@dexterai/x402/client";

// Our own paid endpoint — cheapest service is market_intelligence (0.005 USDC)
// Use token_security (0.01) or market (0.005). Cap the call at 0.02 USDC.
const TARGET = process.env.SELF_SETTLE_URL || "https://api.gentechlabs.net/v1/market/price/ETH";
const MAX_ATOMIC = process.env.SELF_SETTLE_CAP || "20000"; // 0.02 USDC (6 decimals)

const pk = process.env.EVM_PRIVATE_KEY;
if (!pk) {
  console.error("❌ EVM_PRIVATE_KEY not set. Provide the hex private key of a Base wallet with USDC.");
  process.exit(1);
}

async function main() {
  console.log(`🔄 Settling x402 against our own endpoint: ${TARGET}`);
  console.log(`   (cap ${Number(MAX_ATOMIC)/1e6} USDC on Base)`);

  const wallet = await createEvmKeypairWallet(pk);
  console.log(`   payer wallet: ${wallet.address ?? "(check key)"}`);

  const result = await payAndFetch(TARGET, { method: "GET" }, { evm: wallet }, {
    maxAmountAtomic: MAX_ATOMIC,
  });

  if (result.ok && result.paid) {
    console.log(`\n✅ PAID ${result.amountPaid} atomic on ${result.network?.bare}`);
    if (result.txSignature) console.log(`   tx: ${result.txSignature}`);
    if (result.response) {
      const data = await result.response.json().catch(() => ({}));
      console.log("   endpoint response:", JSON.stringify(data));
    }
    console.log("\n🎯 OpenDexter auto-discovery should now catalog:");
    console.log(`   https://api.gentechlabs.net (our gateway)`);
    console.log("   Check: https://open.dexter.cash/mcp (x402_search) + claim the resource.");
  } else if (result.ok && !result.paid) {
    console.log("ℹ️ Endpoint returned non-402 (no payment sent).");
    if (result.response) console.log(await result.response.json().catch(() => ({})));
  } else {
    console.error(`❌ Payment failed: ${result.reason}`, result.detail ?? "");
    if (result.reason === "insufficient_funds") {
      console.error("   → The wallet needs more USDC on Base. Fund it, then rerun.");
    }
    process.exit(1);
  }
}

main().catch((e) => { console.error("unexpected error:", e); process.exit(1); });
