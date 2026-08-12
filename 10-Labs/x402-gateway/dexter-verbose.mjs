import { payAndFetch, createEvmKeypairWallet } from "@dexterai/x402/client";
import { readFileSync } from "fs";
const pk = readFileSync("/root/.blockrun/jordan-avax-secret", "utf8").trim();
const wallet = await createEvmKeypairWallet(pk);
for (const TARGET of ["https://api.gentechlabs.net/v1/token-security", "https://api.gentechlabs.net/v1/market"]) {
  console.log(`\n=== ${TARGET} ===`);
  try {
    const r = await payAndFetch(TARGET, { method: "GET" }, { evm: wallet }, { maxAmountAtomic: "20000", verbose: true });
    console.log("result ok:", r.ok, "| reason:", r.reason, "| detail:", r.detail, "| paid:", r.paid);
  } catch(e) { console.log("THROWN:", e?.message); }
}
