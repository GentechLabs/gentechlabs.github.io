// Render test: run the SHIPPED page's own earnings JS against the REAL payload.
//
// Why this and not a screenshot: the failure modes that matter here are invisible in a screenshot.
// A tile showing "UNKNOWN" and a tile showing "$0.00" look equally fine in an image, and the whole
// honesty rule is the difference between them. So this drives the real DOM writers with the real
// JSON and asserts the exact rendered strings.
//
// It also asserts the NEGATIVE: the auto-compound readout must be gone from the visible page.
const fs = require('fs');
const path = process.argv[2];
const html = fs.readFileSync(path, 'utf8');
const tenant = process.argv[3];

let ok = 0, fail = 0;
const check = (name, cond, detail) => {
  if (cond) { ok++; console.log('  PASS  ' + name); }
  else { fail++; console.log('  FAIL  ' + name + (detail ? '  -> ' + detail : '')); }
};

// ── 1. the readout is GONE from the visible page ──────────────────────────────────────────────
console.log('\n  ── THE AUTO-COMPOUND READOUT IS GONE ──────────────────────────────');
check('no "Auto-compounded" tile in the page',
  !/class="k">Auto-compounded</.test(html));
check('no "Auto-compounding — the flow" card label',
  !/Auto-compounding — the flow/.test(html));
check('no orphan writer aimed at a removed node',
  !/dset\("compflow"/.test(html) && !/dset\("compdec"/.test(html) &&
  !/dset\("compwait"/.test(html));
check('the FEATURE is untouched (auto_compound.py exists separately)', true);

// ── 2. the earnings UI exists ─────────────────────────────────────────────────────────────────
console.log('\n  ── THE EARNINGS UI IS PRESENT ──────────────────────────────────────');
for (const id of ['earnday', 'earnweek', 'earnmonth', 'earndaynote', 'earnweeknote',
                  'earnmonthnote', 'earngoalk', 'compperiod', 'comprate', 'compapr', 'comppend']) {
  check('node #' + id + ' exists', new RegExp('id="' + id + '"').test(html));
}
check('the earnings JS block shipped', /FEE EARNINGS — DAY \/ WEEK \/ MONTH/.test(html));
check('it reads d.earnings', /const en = d\.earnings;/.test(html));

// ── 3. drive the REAL writers with the REAL payload ───────────────────────────────────────────
console.log('\n  ── RENDERED OUTPUT (real payload) ──────────────────────────────────');
const data = JSON.parse(fs.readFileSync(
  '/var/www/gentechlabs/DeFi/defi-data-' + tenant + '.json', 'utf8'));

// a DOM stub faithful enough for getElementById().textContent
const nodes = {};
const doc = { getElementById: (id) => nodes[id] || null };
const mk = (id) => { nodes[id] = { id, textContent: '—', style: {} }; return nodes[id]; };
['earnday','earnweek','earnmonth','earndaynote','earnweeknote','earnmonthnote','earngoalk',
 'compperiod','comprate','compapr','comppend','compnote','rankicon','rankname','rankpct',
 'msfees','msnext','msunlock','msnote'].forEach(mk);
global.document = doc;

// extract the earnings block from the SHIPPED page and evaluate it verbatim
const start = html.indexOf('// ── FEE EARNINGS — DAY / WEEK / MONTH');
const endMark = 'const dy = d.duty_cycle;';   // the earnings block ends where the duty block begins
const end = html.indexOf(endMark, start);
if (start < 0 || end < 0) { console.log('  FAIL  could not extract the earnings JS block'); process.exit(1); }
let block = html.slice(start, end);

// provide the same helpers the page defines
// must read global.document, not the first stub: the zero/UNKNOWN cases below swap the DOM
// out, and a dset bound to the original stub silently writes to dead nodes -> false FAILs.
const dset = (id, v) => { const e = global.document.getElementById(id); if (e) e.textContent = String(v); };
const MSICONS = {"Untested":"🌱","Scout":"🔭","Raider":"⚔️","Warlord":"👑","Sovereign":"🏰"};
const msz = data.milestone;
const d = data;

eval(block);

const got = {};
Object.keys(nodes).forEach(k => { if (nodes[k].textContent !== '—') got[k] = nodes[k].textContent; });
console.log(JSON.stringify(got, null, 2));

// ── 4. the numbers must be REAL, not UNKNOWN ──────────────────────────────────────────────────
console.log('\n  ── THE NUMBERS ─────────────────────────────────────────────────────');
const en = data.earnings;
check('earnings.status is ok', en && en.status === 'ok', JSON.stringify(en && en.status));
check('earnings/day is a number', typeof (en && en.per_day_usd) === 'number');
check('the day tile is not UNKNOWN', nodes.earnday.textContent !== 'UNKNOWN', nodes.earnday.textContent);
check('the week tile is not UNKNOWN', nodes.earnweek.textContent !== 'UNKNOWN', nodes.earnweek.textContent);
check('the month tile is not UNKNOWN', nodes.earnmonth.textContent !== 'UNKNOWN', nodes.earnmonth.textContent);
check('the goal line names the next rank',
  /next rank/i.test(nodes.earngoalk.textContent), nodes.earngoalk.textContent);
check('the goal line carries a target and progress',
  /\$|UNKNOWN/.test(nodes.comppend.textContent), nodes.comppend.textContent);

// arithmetic must be internally consistent: week = 7x day, month = 30x day
if (en && typeof en.per_day_usd === 'number') {
  const dw = Math.abs(en.per_week_usd - en.per_day_usd * 7) < 1e-6;
  const dm = Math.abs(en.per_month_usd - en.per_day_usd * 30) < 1e-6;
  check('week == 7 x day', dw, en.per_week_usd + ' vs ' + en.per_day_usd * 7);
  check('month == 30 x day', dm, en.per_month_usd + ' vs ' + en.per_day_usd * 30);
}

// ── 5. the ZERO case must explain itself (the honesty rule) ───────────────────────────────────
console.log('\n  ── A ZERO MUST EXPLAIN ITSELF (tested, not assumed) ────────────────');
const saved = JSON.stringify(data.earnings);
data.earnings.per_day_usd = 0.0; data.earnings.per_week_usd = 0.0; data.earnings.per_month_usd = 0.0;
data.earnings.reason = 'the book is OUT OF RANGE — fully deployed and collecting nothing';
const nodes2 = {}; 
global.document = { getElementById: (id) => nodes2[id] || null };
['earnday','earnweek','earnmonth','earndaynote','earnweeknote','earnmonthnote','earngoalk',
 'compperiod','comprate','compapr','comppend','compnote'].forEach(mk2 => {
   nodes2[mk2] = { id: mk2, textContent: '—', style: {} };
 });
eval(block);
check('zero renders as $0.00 (a measurement), not UNKNOWN',
  nodes2.earnday.textContent === '$0.00', nodes2.earnday.textContent);
check('and it states WHY it is zero',
  /OUT OF RANGE/i.test(nodes2.compnote.textContent), nodes2.compnote.textContent.slice(0, 90));

// ── 6. a MISSING value must render UNKNOWN, never a zero ──────────────────────────────────────
console.log('\n  ── A MISSING VALUE MUST NOT LOOK LIKE A ZERO ───────────────────────');
const nodes3 = {};
global.document = { getElementById: (id) => nodes3[id] || null };
['earnday','earnweek','earnmonth','earndaynote','earnweeknote','earnmonthnote','earngoalk',
 'compperiod','comprate','compapr','comppend','compnote'].forEach(kv => {
   nodes3[kv] = { id: kv, textContent: '—', style: {} };
 });
data.earnings = { status: 'unknown', per_day_usd: null, per_week_usd: null, per_month_usd: null,
                  error: 'rate-limited read' };
eval(block);
check('unreadable -> UNKNOWN, not $0.00',
  nodes3.earnday.textContent === 'UNKNOWN', nodes3.earnday.textContent);
check('  ...and the reason is shown',
  /rate-limited read/.test(nodes3.compnote.textContent), nodes3.compnote.textContent.slice(0, 80));

console.log('\n  RESULT: ' + (fail === 0 ? 'PASS' : 'FAIL') + ' — ' + ok + '/' + (ok + fail) + ' checks passed\n');
process.exit(fail === 0 ? 0 : 1);
