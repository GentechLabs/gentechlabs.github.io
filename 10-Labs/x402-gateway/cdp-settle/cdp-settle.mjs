#!/usr/bin/env node
/**
 * GENTECH CDP SELF-SETTLEMENT — CDP Bazaar Auto-Index Trigger
 *
 * Pays our OWN x402 endpoint through the CDP facilitator using our own EVM
 * key (GTA arb wallet, funded with USDC on Base). When the CDP facilitator
 * SETTLES a payment for our endpoint (with paymentPayload.resource set),
 * the CDP Bazaar indexes our service automatically.
 *
 * Why our own key instead of CdpX402Client: CdpX402Client needs
 * CDP_WALLET_SECRET to provision a managed wallet. We don't have that, but
 * we DO have our own EVM key with USDC on Base. The vanilla x402 client
 * signs with our key and the CDP facilitator still settles it — which is
 * what triggers Bazaar indexing.
 *
 * Prereq: EVM_PRIVATE_KEY (hex) of a Base wallet with USDC.
 *   Our GTA arb wallet: /root/.hermes/profiles/gentech/secure/gentech-arb-wallet.json
 *
 * Run:
 *   EVM_PRIVATE_KEY=<hex> node cdp-settle.mjs
 */

import { x402Client } from "@x402/core/client";
import { ExactEvmScheme } from "@x402/evm/exact/client";
import { wrapFetchWithPayment } from "@x402/fetch";
import { privateKeyToAccount } from "viem/accounts";

const TARGET = process.env.SELF_SETTLE_URL || "https://api.gentechlabs.net/v1/market/price/ETH";

async function main() {
  const pk = process.env.EVM_PRIVATE_KEY;
  if (!pk) {
    console.error("❌ EVM_PRIVATE_KEY not set. Provide the hex key of a Base wallet with USDC.");
    process.exit(1);
  }

  const signer = privateKeyToAccount(pk.startsWith("0x") ? pk : `0x${pk}`);
  console.log(`🔄 CDP self-settle against: ${TARGET}`);
  console.log(`   payer wallet: ${signer.address}`);

  const client = new x402Client();
  client.register("eip155:*", new ExactEvmScheme(signer));

  const fetchWithPayment = wrapFetchWithPayment(fetch, client);

  console.log("   Paying...");
  const response = await fetchWithPayment(TARGET, { method: "GET" });
  const body = await response.json().catch(() => ({}));
  console.log("   status:", response.status);
  console.log("   body:", JSON.stringify(body).slice(0, 300));

  const paymentResponse = response.headers.get("payment-response");
  if (paymentResponse) {
    console.log("\n✅ PAYMENT SETTLED:");
    console.log(paymentResponse);
    console.log("\n🎯 CDP Bazaar should now index:");
    console.log("   https://api.gentechlabs.net");
    console.log("   Verify: GET /v2/x402/discovery/search?query=gentech (allow up to 6h for ranking)");
  } else {
    console.log("\n⚠️ No payment-response header. Check the gateway verify mode.");
  }
}

main().catch((e) => {
  console.error("❌ Error:", e.message);
  process.exit(1);
});
