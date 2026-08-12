import { payAndFetch, createEvmKeypairWallet } from "@dexterai/x402/client";
import { readFileSync } from "fs";

const pk = readFileSync("/root/.blockrun/jordan-avax-secret", "utf8").trim();
const TARGET = "https://api.gentechlabs.net/v1/market/price/ETH";

try {
  const wallet = await createEvmKeypairWallet(pk);
  console.log("payer wallet:", wallet.address);

  console.log("calling payAndFetch...");
  const result = await payAndFetch(TARGET, { method: "GET" }, { evm: wallet }, {
    maxAmountAtomic: "20000",
  });
  console.log("result:", JSON.stringify(result, (k, v) =>
    typeof v === "bigint" ? v.toString() : v, 2));
} catch (e) {
  console.error("caught error:", e?.message || e);
  if (e?.stack) console.error(e.stack.split("\n").slice(0, 6).join("\n"));
}
