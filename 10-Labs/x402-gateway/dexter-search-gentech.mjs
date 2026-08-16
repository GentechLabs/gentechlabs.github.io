import { capabilitySearch } from "@dexterai/x402/client";
for (const q of ["gentechlabs", "gentech", "api.gentechlabs.net", "defi lp analytics", "rugcheck", "token security"]) {
  try {
    const r = await capabilitySearch({ query: q });
    const strong = r?.strongResults || [];
    console.log(`\n=== "${q}" → ${strong.length} strong ===`);
    strong.slice(0,8).forEach(a => console.log(`  - ${a.name}: ${a.price} [${a.url||a.resource||''}]`));
  } catch(e) { console.log(`\n=== "${q}" ERR:`, e?.message || e); }
}
