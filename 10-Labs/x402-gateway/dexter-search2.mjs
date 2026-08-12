import { capabilitySearch } from "@dexterai/x402/client";
for (const q of ["gentech", "gentechlabs", "deFi LP analytics", "rugcheck token risk", "GenTech Labs x402"]) {
  try {
    const r = await capabilitySearch({ query: q });
    const strong = r?.strongResults || [];
    const related = r?.relatedResults || [];
    console.log(`\n=== "${q}" → ${strong.length} strong / ${related.length} related ===`);
    [...strong,...related].slice(0,5).forEach(a => console.log(`  - ${a.name}: ${a.price} [${a.url||a.resource||''}]`));
  } catch(e) { console.log(`\n=== "${q}" ERR:`, e?.message || e); }
}
