import { payAndFetch, createEvmKeypairWallet } from "@dexterai/x402/client";

const pk = process.env.EVM_PRIVATE_KEY;
const wallet = await createEvmKeypairWallet(pk);

// Monkeypatch fetch to capture the retry's PAYMENT-SIGNATURE header + body
const origFetch = globalThis.fetch;
globalThis.fetch = async (url, opts) => {
  const hdrs = opts && opts.headers;
  const sig = hdrs && hdrs.get && hdrs.get("PAYMENT-SIGNATURE");
  if (sig) {
    console.log("=== PAYMENT-SIGNATURE header captured ===");
    const decoded = Buffer.from(sig, "base64").toString("utf8");
    console.log("decoded JSON:", decoded.slice(0, 800));
  }
  const pr = hdrs && hdrs.get && hdrs.get("payment-required");
  if (pr) console.log("(payment-required on retry)");
  return origFetch(url, opts);
};

const result = await payAndFetch(
  "https://api.gentechlabs.net/v1/market/price/ETH",
  { method: "GET" },
  { evm: wallet },
  { maxAmountAtomic: "20000" }
);
console.log("ok:", result.ok, "paid:", result.paid, "reason:", result.reason, "detail:", result.detail);
