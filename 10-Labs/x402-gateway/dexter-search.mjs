import { capabilitySearch } from "@dexterai/x402/client";
for (const q of ["token security", "wallet analysis", "get ETH price", "nft search"]) {
  try {
    const r = await capabilitySearch({ query: q });
    const strong = r?.strongResults || [];
    console.log(`\n=== "${q}" → ${strong.length} strong results ===`);
    strong.slice(0,5).forEach(a => console.log(`  - ${a.name}: ${a.price} [${a.url||a.resource||''}]`));
  } catch(e) { console.log(`\n=== "${q}" ERR:`, e?.message || e); }
}
