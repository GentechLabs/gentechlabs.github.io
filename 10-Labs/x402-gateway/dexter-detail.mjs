import { payAndFetch, createEvmKeypairWallet, DEXTER_FACILITATOR_URL } from "@dexterai/x402/client";
import { readFileSync } from "fs";
const pk = readFileSync("/root/.blockrun/jordan-avax-secret", "utf8").trim();
const wallet = await createEvmKeypairWallet(pk);
console.log("wallet:", wallet.address);
console.log("facilitator:", DEXTER_FACILITATOR_URL);
// Probe the facilitator directly
try {
  const r = await fetch(DEXTER_FACILITATOR_URL);
  const txt = await r.text();
  console.log("facilitator status:", r.status, "body:", txt.slice(0,200));
} catch(e){ console.log("facilitator fetch err:", e.message); }
