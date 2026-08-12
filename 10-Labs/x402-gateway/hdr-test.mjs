const raw = await (await fetch("https://api.gentechlabs.net/v1/market/price/ETH")).headers.get("payment-required");
console.log("header length:", raw?.length);
// Try atob
try {
  const dec = atob(raw);
  const parsed = JSON.parse(dec);
  console.log("atob OK, x402Version:", parsed.x402Version, "| accepts:", parsed.accepts?.length);
} catch(e) {
  console.log("atob/JSON FAILED:", e.message);
  // Find the offending char
  const b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
  for (let i=0;i<raw.length;i++){
    if(!b64.includes(raw[i])){ console.log(`invalid char at ${i}: ${JSON.stringify(raw[i])} (code ${raw.charCodeAt(i)})`); break; }
  }
}
