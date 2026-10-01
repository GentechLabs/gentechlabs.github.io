// Render test: the two shape boxes must never contradict each other again.
//
// Jordan, 2026-09-27, sent a screenshot of his own page showing:
//     green:  "✓ This shape is CORRECT — spot at the trough (a V) is where a bid-ask is BUILT to sit"
//     amber:  "⚠ ... but the live book is bid-ask — they DISAGREE"
// Two boxes, one book, opposite messages. The amber box was arithmetic, not a fault: the book holds
// 12 bins, fewer than any deployable geometry, because his ask leg sold off into the rally. Reading
// it as "your book disagrees with the market" is a false alarm, and a warning printed next to a tick
// teaches the reader to distrust both.
//
// So this asserts, on the SHIPPED page, driven by the REAL payload:
//   1. a PARTIAL book gets one calm informational box and NO alarm;
//   2. the two boxes do not contradict;
//   3. a genuinely mis-shaped book STILL gets the warning (the alarm must not be silenced).
//
// Run: node test_shape_verdict_render.js <page.html> <tenant>
const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const tenant = process.argv[3];
const dataPath = '/var/www/gentechlabs/DeFi/defi-data-' + tenant + '.json';

let ok = 0, fail = 0;
const check = (n, c, d) => {
  if (c) { ok++; console.log('  PASS  ' + n); }
  else { fail++; console.log('  FAIL  ' + n + (d ? '  -> ' + d : '')); }
};

// Extract the two blocks that write the verdicts, verbatim from the shipped page, and run them.
const grab = (from, to) => {
  const i = html.indexOf(from);
  const j = html.indexOf(to, i);
  if (i < 0 || j < 0) throw new Error('could not extract ' + from.slice(0, 40));
  return html.slice(i, j);
};
const verdictBlock = grab('const st = document.getElementById("shapetick");', '// ── WHY THIS SHAPE');
// End the why-block at its OWN closing brace, not at the next section comment: the first attempt
// grabbed unrelated code (a `sc` variable) and threw a ReferenceError. Extract exactly the block.
const whyStart = html.indexOf('const sw2 = document.getElementById("shapewhy");');
const whyEnd = html.indexOf('\n  }', html.indexOf('sw2.style.display = "none";', whyStart));
const whyBlock = html.slice(whyStart, whyEnd + 4);

function run(payload) {
  const nodes = {};
  ['shapetick', 'shapewhy'].forEach(id => { nodes[id] = { id, textContent: '', style: {}, className: '' }; });
  global.document = { getElementById: id => nodes[id] || null };
  const dset = (id, v) => { const e = global.document.getElementById(id); if (e) e.textContent = String(v); };
  const d = payload;
  eval(verdictBlock);
  eval(whyBlock);
  return nodes;
}

const real = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

console.log('\n  ── THE LIVE BOOK (the one in the screenshot) ──────────────────────');
const r = run(real);
console.log('    shapetick: ' + r.shapetick.textContent.slice(0, 150));
console.log('    className: ' + r.shapetick.className);
console.log('    shapewhy : ' + r.shapewhy.textContent.slice(0, 160));

// BRANCH ON THE ACTUAL PAYLOAD. The first version of this test asserted the live book was
// PARTIAL for every tenant, and dadrian's book simply is not (it is a healthy full-width curve that
// happens to have a crossed leg) — so the test reported two FAILs that were the TEST's fault. A test
// that hard-codes one tenant's state is not testing the page, it is testing its own assumption.
const livePartial = !!(real.shape_why && real.shape_why.partial_book);
console.log('    live book is partial: ' + livePartial);
const liveDisagrees = !!(real.shape_why && real.shape_why.agrees === false);
if (livePartial && !liveDisagrees) {
  check('a PARTIAL book with no disagreement is not warned about',
    r.shapetick.className.indexOf('warn') < 0, r.shapetick.className);
  check('  ...and it says PARTIAL, not CORRECT-or-upside-down',
    /partial/i.test(r.shapetick.textContent), r.shapetick.textContent.slice(0, 60));
  check('  ...and the why-box does NOT say DISAGREE',
    !/DISAGREE/.test(r.shapewhy.textContent), r.shapewhy.textContent.slice(0, 90));
  check('  ...and it explains the partial book instead',
    /NOT a disagreement/i.test(r.shapewhy.textContent), r.shapewhy.textContent.slice(0, 100));
} else if (liveDisagrees) {
  check('a real SHAPE disagreement is warned, even on a partial book',
    /warn/.test(r.shapetick.className), r.shapetick.className);
  check('  ...and it does not claim the legs are CORRECT',
    !/✓ This shape is CORRECT/.test(r.shapetick.textContent), r.shapetick.textContent.slice(0, 80));
  check('  ...and the why-box reports the disagreement',
    /shape question is real|DISAGREE/.test(r.shapewhy.textContent), r.shapewhy.textContent.slice(0, 90));
} else {
  check('a full-width book is not warned about (no "warn" class)',
    r.shapetick.className.indexOf('warn') < 0, r.shapetick.className);
  check('  ...and the why-box does not claim a false DISAGREE',
    !/DISAGREE/.test(r.shapewhy.textContent), r.shapewhy.textContent.slice(0, 90));
}
// THE ACTUAL INVARIANT, stated properly. The screenshot's sin was not "a warning exists" — it was
// that one box said CORRECT while the other warned. So: the two boxes must AGREE about whether
// there is a problem. Calm+calm and warn+warn are both fine; calm+warn is the bug.
const stWarn = /warn/.test(r.shapetick.className);
const swWarn = /warn/.test(r.shapewhy.className);
const stCalmTick = /✓/.test(r.shapetick.textContent) && !stWarn;
check('the two boxes agree about whether there is a problem (never a tick beside a warning)',
  !(stCalmTick && swWarn), 'shapetick=' + r.shapetick.className + ' shapewhy=' + r.shapewhy.className);

console.log('\n  ── A GENUINELY MIS-SHAPED BOOK MUST STILL BE WARNED ────────────────');
const bad = JSON.parse(JSON.stringify(real));
bad.shape_why = { label: 'RANGE_BOUND', market: 'curve', shape_for: 'curve', agrees: false,
                  note: 'the market reads curve and the RANGE_BOUND regime resolves to curve, '
                      + 'but the live book is bid-ask — they DISAGREE' };
bad.leg_orientation = { shape: 'bid-ask', verdict: 'INVERTED', judgeable: true };
const b = run(bad);
console.log('    shapetick: ' + b.shapetick.textContent.slice(0, 130));
console.log('    className: ' + b.shapetick.className);
check('a real fault still raises the warning', /warn/.test(b.shapetick.className), b.shapetick.className);
check('  ...and a real disagreement still says DISAGREE',
  /DISAGREE/.test(b.shapewhy.textContent), b.shapewhy.textContent.slice(0, 80));

console.log('\n  ── AND A HEALTHY FULL BOOK READS AS CORRECT ────────────────────────');
const good = JSON.parse(JSON.stringify(real));
good.shape_why = { label: 'RANGE_BOUND', market: 'curve', shape_for: 'curve', agrees: true,
                   note: 'the market reads curve and the RANGE_BOUND regime resolves to curve — the '
                       + 'layer that picks the shape agrees with the book we hold' };
good.leg_orientation = { shape: 'curve', verdict: 'OK', judgeable: true };
good.shape_kind = 'curve';
const g = run(good);
console.log('    shapetick: ' + g.shapetick.textContent.slice(0, 120));
check('a healthy book still reads CORRECT', /CORRECT/.test(g.shapetick.textContent));
check('  ...and its why-box says the layer agrees', /agrees with the book/.test(g.shapewhy.textContent));

console.log('\n  RESULT: ' + (fail === 0 ? 'PASS' : 'FAIL') + ' — ' + ok + '/' + (ok + fail) + ' checks passed\n');
process.exit(fail === 0 ? 0 : 1);
