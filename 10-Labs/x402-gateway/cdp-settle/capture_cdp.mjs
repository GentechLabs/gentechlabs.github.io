import { x402Client } from "@x402/core/client";
import { ExactEvmScheme } from "@x402/evm/exact/client";
import { wrapFetchWithPayment } from "@x402/fetch";
import { privateKeyToAccount } from "viem/accounts";

const pk = process.env.EVM_PRIVATE_KEY;
const signer = privateKeyToAccount(pk.startsWith("0x") ? pk : `0x${pk}`);

const origFetch = globalThis.fetch;
globalThis.fetch = async (url, opts) => {
  const hdrs = opts && opts.headers;
  if (hdrs) {
    // Headers may be Headers object or plain object
    let out = {};
    try {
      if (hdrs.forEach) hdrs.forEach((v, k) => { out[k] = v; });
      else Object.assign(out, hdrs);
    } catch(e) { out = {err: String(e)}; }
    console.log("=== REQUEST HEADERS ===");
    console.log(JSON.stringify(out, null, 1).slice(0, 1200));
    // Try to read specific keys
    for (const k of ["PAYMENT-SIGNATURE","X-Payment","Authorization","X-PAYMENT","x402-payment"]) {
      const v = hdrs.get ? hdrs.get(k) : hdrs[k];
      if (v) console.log(`HDR[${k}] =`, String(v).slice(0, 300));
    }
  }
  return origFetch(url, opts);
};

const client = new x402Client();
client.register("eip155:*", new ExactEvmScheme(signer));
const fetchWithPayment = wrapFetchWithPayment(fetch, client);

const response = await fetchWithPayment("https://api.gentechlabs.net/v1/market/price/ETH", { method: "GET" });
const body = await response.json().catch(() => ({}));
console.log("status:", response.status);
console.log("body:", JSON.stringify(body).slice(0, 300));
