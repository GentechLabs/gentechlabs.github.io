import { payAndFetch, createEvmKeypairWallet } from "@dexterai/x402/client";

const pk = process.env.EVM_PRIVATE_KEY;
const wallet = await createEvmKeypairWallet(pk);
console.log("wallet:", wallet.address);

try {
  const result = await payAndFetch("https://api.gentechlabs.net/v1/market/price/ETH", { method: "GET" }, { evm: wallet }, { maxAmountAtomic: "20000" });
  console.log("ok:", result.ok, "paid:", result.paid);
  console.log("reason:", result.reason);
  console.log("detail:", result.detail);
} catch(e) {
  console.log("=== FULL STACK ===");
  console.log(e && e.stack ? e.stack : String(e));
}
