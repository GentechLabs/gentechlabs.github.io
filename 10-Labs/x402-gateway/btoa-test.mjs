// Confirm the root cause: btoa fails on the em-dash present in our gateway description
const desc = "GenTech Labs x402 \u2014 Market";  // em-dash
const obj = { x402Version: 2, resource: { url: "https://api.gentechlabs.net/v1/market", description: desc } };
try {
  const enc = btoa(JSON.stringify(obj));
  console.log("btoa with em-dash OK, len:", enc.length);
} catch(e) {
  console.log("btoa FAILED on em-dash:", e.message);
}
// Now without em-dash
try {
  const enc2 = btoa(JSON.stringify({ ...obj, resource: { ...obj.resource, description: "clean" } }));
  console.log("btoa without em-dash OK, len:", enc2.length);
} catch(e) {
  console.log("btoa FAILED clean:", e.message);
}
