#!/usr/bin/env python3
"""SEC / CFTC Rulemaking Watch — the post-CLARITY operative framework.

WHY THIS EXISTS (Jordan, Sep 16 2026):
  "We can go ahead and stop this cron job... We got the announcement yesterday.
   Now we should be tracking what the SEC and the CFTC are going to be doing
   as result."

CLARITY (H.R.3633) died on the Senate floor 2026-09-15 (cloture 49-50). With no
statute, the operative framework for the next 12-24 months is SEC/CFTC RULEMAKING:
fast, narrow, and reversible. That is what we now watch, and it is a different
object from sentiment: agencies publish rules, courts do not.

SOURCES (all authoritative, all free, no API key)
  1. Federal Register API — SEC + CFTC documents. This is the OFFICIAL rulemaking
     record: a rule only exists once it is published here. "Proposed Rule" opens a
     comment window; "Rule" is final; "Notice" is mostly exchange SRO filings.
  2. SEC press releases RSS — official announcements and enforcement.
  3. CFTC press releases RSS — official announcements and enforcement.

DESIGN
  - Watermark dedup: each source's item IDs are stored; only NEW ids print.
  - First run records a BASELINE and prints nothing (use --digest to inspect now).
  - Silence doctrine: empty stdout when nothing is new, so the cron delivers nothing.
  - Relevance flagging: items touching digital assets / yield / staking / stablecoins
    / custody are flagged, because those are the ones that change the compliance
    shape of a yield-bearing position. Non-crypto rulemaking still prints (it is the
    agency's posture) but unmarked.
  - SRO NOISE FILTER: the Federal Register SEC feed is dominated by self-regulatory
    organisation filings (exchange fee schedules). Notices are dropped unless they
    are crypto-relevant.

HONESTY RULE
  This script reports what agencies PUBLISHED. It does not interpret, predict, or
  score probability. A rule is not law until it is published; a proposal is not a
  rule. Never upgrade an item's status in the report.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

STATE_PATH = "/root/.hermes/scripts/.sec-cftc-watch-state.json"
UA = "GenTech-Steward/1.0 (treasury research; contact@gentechlabs.net)"

FR_BASE = "https://www.federalregister.gov/api/v1/documents.json"
AGENCIES = {
    "SEC": "securities-and-exchange-commission",
    "CFTC": "commodity-futures-trading-commission",
}
PR_RSS = {
    "SEC": "https://www.sec.gov/news/pressreleases.rss",
    "CFTC": "https://www.cftc.gov/RSS/RSSGP/rssgp.xml",
}

# What actually touches a yield-bearing digital-asset position.
# NOTE: word boundaries are REQUIRED on short stems — a bare "defi" also matches
# "definition"/"definite"/"defined", which dragged Cboe fee-schedule SRO notices
# into the crypto-relevant list on the first run. Verified false positive.
RELEVANT = [
    # tokeni[sz]e: the agencies use the US spelling in their own titles, but the UK
    # spelling appears in quoted material and in our own notes. `tokeniz` alone
    # classified "Tokenised NMS Stock" as NOT relevant — a filter that silently
    # drops the item it was written to catch. Verified both directions below.
    r"\bdigital assets?\b", r"\bcrypto(?:currenc(?:y|ies))?\b", r"\btokeni[sz]\w*",
    r"\bstablecoins?\b", r"\bstaking\b", r"\byield\b", r"\bdefi\b",
    r"\bdecentraliz\w*", r"\bcustod\w+", r"\bblockchain\b",
    r"\bvirtual currenc\w+", r"\bdigital commodit\w+",
    r"\bspot\b.{0,20}\b(?:etf|exchange-traded)\b", r"\binvestment contract\w*",
    r"\bmarket structure\b",
    # ── VENUE + PRODUCT vocabulary, added 2026-09-23 ─────────────────────────
    # WHY: the filter keyed on ASSET vocabulary (crypto, blockchain, tokeniz...) and so
    # could only see an item that NAMES the asset. A digital-asset venue filing usually
    # names the VENUE and the PRODUCT instead, and nothing else. Measured 2026-09-23:
    # three crypto-native exchanges filed SRO rule changes published that morning —
    # Coinbase Derivatives (SR-COIN-2026-002, perpetual single-stock futures),
    # Bitnomial (SR-BTNL-2026-001), KalshiEX (SR-KALSHIEX-2026-02) — and all three were
    # DROPPED SILENTLY, because "Coinbase Derivatives" carries no asset vocabulary.
    # Same bug shape as the 2026-09-21 `tokeniz` defect: a filter that cannot catch the
    # item it exists to catch, reported as a clean, short list.
    # NOT a guess about relevance: every pattern is a NAMED venue or a NAMED listed
    # product, so a match asserts WHO filed, not what it might mean.
    # NOISE MEASURED BOTH DIRECTIONS on the live corpus (2026-06-01..2026-09-23):
    #   SEC  500 docs: relevant 4 -> 12 (+8, +1.6% of corpus), all 8 genuine.
    #   CFTC  41 docs: relevant 1 ->  5 (+4, +9.8% of corpus), all 4 genuine and all 4
    #                  previously invisible (Coinbase / event contracts /
    #                  individual-equity futures / prediction markets).
    # Negative controls still DROPPED after the patch: Cboe + NYSE fee schedules,
    # FINRA housekeeping, MEMX circuit-breaker notices, a mutual-fund trust notice.
    r"\bcoinbase\b", r"\bkalshi\w*\b", r"\bbitnomial\b", r"\bnadex\b",
    r"\bnorth american derivatives\b", r"\bprometheum\b", r"\bbakkt\b",
    r"\bzero hash\b", r"\bpolymarket\b", r"\bforecastex\b",
    # product names under which regulators list digital-asset-adjacent venues
    r"\bsecurit(?:y|ies) futures?\b", r"\bsingle-stock futures?\b",
    r"\bevent contracts?\b", r"\bperpetual\s+[\w-]*\s*futures?\b",
    r"\bcash-settled futures\b", r"\bpredictions? markets?\b",
]
REL_RE = re.compile("|".join(RELEVANT), re.I)
# Federal Register types worth surfacing
POLICY_TYPES = {"Rule", "Proposed Rule", "Presidential Document"}


def fetch(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def load_state():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(st):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f, indent=2)
    os.replace(tmp, STATE_PATH)


def federal_register(agency_slug, per_page=40):
    """Official rulemaking record for one agency."""
    fields = "".join(
        f"&fields%5B%5D={f}" for f in
        ("title", "type", "publication_date", "html_url", "document_number",
         "abstract", "comments_close_on", "action")
    )
    url = (f"{FR_BASE}?conditions%5Bagencies%5D%5B%5D={agency_slug}"
           f"&per_page={per_page}&order=newest{fields}")
    d = json.loads(fetch(url).decode())
    out, seen_urls = [], set()
    for it in d.get("results", []):
        u = it.get("html_url") or ""
        if u in seen_urls:
            continue
        seen_urls.add(u)
        out.append({
            "id": "fr:" + str(it.get("document_number") or u),
            "type": it.get("type") or "?",
            "date": it.get("publication_date") or "",
            "title": (it.get("title") or "").strip(),
            "url": u,
            "abstract": (it.get("abstract") or "").strip(),
            "comments_close_on": it.get("comments_close_on") or "",
        })
    return out


class DeadlineList(list):
    """A list of open comment windows that CARRIES which agencies failed to fetch.

    WHY THIS IS A LIST SUBCLASS AND NOT A TUPLE. Every existing caller — the report
    loop, and the regression test — treats this as a plain list (len, truthiness,
    iteration, sorted). Returning a tuple would silently break them. A subclass keeps
    the contract and adds the one thing that was missing: the failures.
    """
    failures = ()


def comment_deadlines(days_ahead=60):
    """Open comment windows across SEC + CFTC — the ACTIONABLE part of a proposal.

    A proposed rule is only a comment window until it closes; the deadline is the
    one date in the whole pipeline a reader can act on, so surface it.

    Query by comment-date RANGE on the API rather than filtering the newest-N list:
    a window opened in August can still be open in October, and the recent-docs
    fetch would never reach it. Administrative "Agency Information Collection
    Activities" paperwork notices are dropped — they are routine renewals, not policy.

    FAILURE MUST BE LOUD. This function used to `continue` on a fetch error, so a
    dead SEC query deleted every SEC window from the report — including Regulation
    Crypto Assets, the one deadline this treasury owns — and printed a shorter,
    clean-looking list with NO failure line. A partial outage was rendered as
    "nothing there". Measured 2026-09-22 by killing only the SEC comment-date
    query: 6 SEC windows including 2026-10-20 vanished, output said nothing.
    Failures are now returned so the caller can say the list is INCOMPLETE.
    """
    from datetime import date, timedelta
    today = date.today()
    horizon = today + timedelta(days=days_ahead)
    found = []
    failures = []
    for tag, slug in AGENCIES.items():
        url = (f"{FR_BASE}?conditions%5Bagencies%5D%5B%5D={slug}"
               f"&conditions%5Bcomment_date%5D%5Bgte%5D={today.isoformat()}"
               f"&conditions%5Bcomment_date%5D%5Blte%5D={horizon.isoformat()}"
               "&per_page=60&order=newest"
               "&fields%5B%5D=title&fields%5B%5D=type&fields%5B%5D=publication_date"
               "&fields%5B%5D=html_url&fields%5B%5D=document_number"
               "&fields%5B%5D=abstract&fields%5B%5D=comments_close_on")
        try:
            d = json.loads(fetch(url).decode())
        except Exception as e:
            # NOT `continue`. A swallowed agency is a silently shorter deadline list.
            failures.append(f"{tag} open-comment-window query failed: {e}")
            continue
        for it in d.get("results", []):
            cd = it.get("comments_close_on") or ""
            title = (it.get("title") or "").strip()
            if "agency information collection" in title.lower():
                continue  # routine paperwork renewal, not policy
            if not cd:
                continue
            try:
                dd = date.fromisoformat(cd)
            except Exception:
                continue
            found.append({
                "agency": tag, "type": it.get("type") or "?",
                "title": title, "url": it.get("html_url") or "",
                "abstract": (it.get("abstract") or "").strip(),
                "comments_close_on": cd, "days_left": (dd - today).days,
            })
    out = DeadlineList(sorted(found, key=lambda x: x["comments_close_on"]))
    out.failures = tuple(failures)
    return out


def record_hot(st, hot):
    """Hand the Chair pass the list of relevance-flagged items THIS run reported.

    WHY (found 2026-09-24): the two passes never spoke. Pass 1 discovers a changing set of
    relevance-flagged items; pass 2 renders a FIXED board named in its own READS dict and
    prints it as though it were the complete read. On 2026-09-24 pass 1 flagged five items
    (SEC 2026-19512 Coinbase Derivatives security-futures customer margin; 2026-19407/8/9
    the three crypto-venue SRO filings; 2026-19215 Nadex's Section 6(g) registration) while
    pass 2 rendered its three standing items and said nothing about the five it had no read
    for. A short, confident, complete-looking list that has silently dropped the items the
    other pass exists to catch is this treasury's signature failure one level up. An absent
    read is an ABSENCE, not a verdict of "does not reach us" — so pass 1 records it and
    pass 2 prints it.
    """
    st["last_hot"] = [
        {k: i.get(k) for k in ("id", "agency", "type", "date", "title", "url")}
        for i in hot
    ]
    st["last_hot_run"] = datetime.now(timezone.utc).isoformat()
    save_state(st)


def press_rss(agency, url):
    """Namespace-agnostic RSS parse.

    The feeds declare several namespaces (dc:, content:, foaf:, rdfs:, schema:...)
    and a naive `xmlns` strip leaves prefixes unbound -> ET raises 'unbound prefix'.
    Parsing normally and matching on the LOCAL tag name sidesteps prefixes entirely.
    """
    raw = fetch(url).decode("utf-8", "replace")
    root = ET.fromstring(raw)

    def local(el):
        return el.tag.split("}")[-1].lower()

    def text_of(item, name):
        for ch in item:
            if local(ch) == name:
                return (ch.text or "").strip()
        return ""

    out = []
    for it in root.iter():
        if local(it) != "item":
            continue
        link = text_of(it, "link")
        title = re.sub(r"\s+", " ", text_of(it, "title"))
        desc = re.sub(r"\s+", " ", text_of(it, "description"))
        pub = text_of(it, "pubdate") or text_of(it, "date")
        out.append({
            "id": f"pr:{agency}:" + (link or title),
            "type": "Press Release",
            "date": pub,
            "title": title,
            "url": link,
            "abstract": desc[:400],
        })
    return out


def relevant(item):
    """Is this item about a yield-bearing digital-asset position?

    ROUTINE PAPERWORK IS EXCLUDED, and this is the script's OWN stated policy rather than a
    new one: comment_deadlines() has dropped "Agency Information Collection Activities"
    notices since it was written, with the comment "routine paperwork renewal, not policy".
    The facts pass did not, so the pair disagreed about the same document.

    WHY THIS SURFACED NOW (2026-09-23): extending RELEVANT to VENUE vocabulary made a CFTC
    paperwork notice relevant — "Notice of Intent To Extend Collection 3038-0059: Part 41,
    Relating to Security Futures Products" — because the extension notice NAMES the product
    in its title. Measured: 17 relevant docs across both agencies since 2026-06-01, and
    exactly 1 of them is this class. Not a flood, but a document whose only content is an
    intent to keep an existing form is not a compliance-shape change, and the other pass
    already says so. Making the two agree is cheaper than explaining the difference.
    """
    title = item.get("title") or ""
    if "agency information collection" in title.lower():
        return False
    blob = f"{title} {item.get('abstract','')}"
    return bool(REL_RE.search(blob))


def collect():
    items = []
    for tag, slug in AGENCIES.items():
        try:
            for it in federal_register(slug):
                it["agency"] = tag
                # drop SRO/administrative noise unless it is crypto-relevant
                if it["type"] not in POLICY_TYPES and not relevant(it):
                    continue
                items.append(it)
        except Exception as e:
            items.append({"id": f"ERR:FR:{tag}", "agency": tag, "type": "ERROR",
                          "title": f"Federal Register fetch failed for {tag}: {e}",
                          "url": "", "date": "", "abstract": "", "_error": True})
    for tag, url in PR_RSS.items():
        try:
            for it in press_rss(tag, url):
                it["agency"] = tag
                items.append(it)
        except Exception as e:
            items.append({"id": f"ERR:PR:{tag}", "agency": tag, "type": "ERROR",
                          "title": f"Press-release feed failed for {tag}: {e}",
                          "url": "", "date": "", "abstract": "", "_error": True})
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--digest", action="store_true",
                    help="show the current relevant items regardless of watermark")
    ap.add_argument("--max", type=int, default=12)
    a = ap.parse_args()

    items = collect()
    st = load_state()
    seen = set(st.get("seen", []))
    first_run = "seen" not in st

    fresh = [i for i in items if i["id"] not in seen]
    # bound the watermark
    st["seen"] = list(dict.fromkeys(list(seen) + [i["id"] for i in items]))[-600:]
    st["last_run"] = datetime.now(timezone.utc).isoformat()
    save_state(st)

    errors = [i for i in fresh if i.get("_error")]
    if errors:
        print("⚠️ SEC/CFTC WATCH — SOURCE FAILURE (reporting, not hiding):")
        for e in errors:
            print(f"   {e['agency']}: {e['title']}")
        print()

    if first_run and not a.digest:
        # baseline established; stay silent
        return 0

    show = [i for i in fresh if not i.get("_error")]
    if a.digest:
        show = [i for i in items if not i.get("_error") and relevant(i)]
    if not show and not errors:
        # SILENCE IS ONLY HONEST WHEN THE COMMENT CLOCKS ARE STILL VISIBLE.
        # The Chair's own carry-forward names one live deadline this treasury owns
        # (Regulation Crypto Assets, comments close 2026-10-20). On a day with no new
        # publications this early return deleted that deadline from the delivered
        # message entirely — the one actionable date we have, suppressed by a
        # nothing-new condition. The deadline pass below is a SEPARATE fetch, so it is
        # cheap to check here: if any window is open, the run is not silent; if none is
        # open AND the fetch was clean, then there is genuinely nothing to deliver.
        try:
            _probe = comment_deadlines()
            _pfail = list(getattr(_probe, "failures", ()))
        except Exception as e:
            _probe, _pfail = [], [f"open-comment-window pass failed entirely: {e}"]
        record_hot(st, [])
        if not _probe and not _pfail:
            return 0
        # fall through and report the windows (and any failures) only
        now_probe = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        print(f"🏛️ SEC / CFTC RULEMAKING WATCH — NO NEW PUBLICATIONS — {now_probe}")
        # The header must not promise a list that is not printed. First draft said "the
        # clocks below are carried forward" unconditionally — true when windows follow,
        # a false claim when the fetch returned zero. Gate the sentence on the content.
        if _probe:
            print("   (nothing new from SEC or CFTC; the open comment clocks below are")
            print("    carried forward because a deadline does not need a new document to")
            print("    still be a deadline.)")
        else:
            print("   (nothing new from SEC or CFTC, and the comment-window feed failed;")
            print("    there is no window list to carry forward — see the warning below.)")
        print()
        if _pfail:
            print("⚠️ COMMENT-WINDOW INCOMPLETE (reporting, not hiding):")
            for f_ in _pfail:
                print(f"   {f_}")
            print()
        if _probe:
            print("🗓️ OPEN COMMENT WINDOWS (the actionable part — a proposal is only a")
            print("   comment window until it closes):")
            for d in _probe:
                flag = "●" if relevant(d) else " "
                print(f"   {flag} closes {d['comments_close_on']} ({d['days_left']}d) "
                      f"[{d['agency']} · {d['type']}] {d['title'][:90]}")
                print(f"     {d['url']}")
            print(f"   ── {len(_probe)} window(s) carried forward"
                  + (" — INCOMPLETE, see warning above." if _pfail else ", all shown."))
            print()
        print("   Reminder: a proposal is not a rule, and a rule is not law until published.")
        record_hot(st, [])
        return 0

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    label = "DIGEST (current relevant)" if a.digest else "NEW"
    print(f"🏛️ SEC / CFTC RULEMAKING WATCH — {label} — {now}")
    print()

    hot = [i for i in show if relevant(i)]
    cold = [i for i in show if not relevant(i)]
    # Hand the Chair pass exactly what was flagged here — see record_hot() for why.
    record_hot(st, hot)

    # Open comment windows — the only dated, actionable part of the pipeline.
    # A bare `except Exception: deadlines = []` used to sit here, which is the SAME
    # false-value shape one level up: a total failure of the deadline pass rendered as
    # an empty-but-valid list. Now the failure is PRINTED, and an empty list is never
    # allowed to read as "no windows are open".
    deadline_failures = []
    try:
        deadlines = comment_deadlines()
        deadline_failures = list(getattr(deadlines, "failures", ()))
    except Exception as e:
        deadlines = []
        deadline_failures = [f"open-comment-window pass failed entirely: {e}"]

    if deadline_failures:
        print("⚠️ COMMENT-WINDOW INCOMPLETE (reporting, not hiding):")
        for f_ in deadline_failures:
            print(f"   {f_}")
        if not deadlines:
            print("   → Zero windows shown BECAUSE THE FETCH FAILED, not because")
            print("     nothing is open. Treat this feed as unread this run.")
        else:
            print(f"   → The {len(deadlines)} window(s) below are only the ones that")
            print("     DID fetch. At least one agency's windows are missing.")
        print()

    if deadlines:
        print("🗓️ OPEN COMMENT WINDOWS (the actionable part — a proposal is only a")
        print("   comment window until it closes):")
        # Print EVERY open window. The cap used to be [:8] with no disclosure, so a
        # 12-window day reported 8 and looked complete — the count is the assertion,
        # so state it. If we ever re-introduce a cap it must print what it dropped.
        for d in deadlines:
            flag = "●" if relevant(d) else " "
            print(f"   {flag} closes {d['comments_close_on']} ({d['days_left']}d) "
                  f"[{d['agency']} · {d['type']}] {d['title'][:90]}")
            print(f"     {d['url']}")
        # The completeness claim is an ASSERTION, so it may only be printed when true.
        # "all shown" over a partially-fetched list is the exact lie this patch exists
        # to stop.
        if deadline_failures:
            print(f"   ── {len(deadlines)} window(s) shown — INCOMPLETE, see warning above.")
        elif len(deadlines) >= 8:
            print(f"   ── {len(deadlines)} open window(s) total, all shown.")
        print()
    elif not deadline_failures:
        print("🗓️ OPEN COMMENT WINDOWS: none open in the next 60 days "
              "(fetched SEC + CFTC, both live).")
        print()

    if hot:
        print(f"● DIGITAL-ASSET RELEVANT ({len(hot)}) — these change compliance shape:")
        if len(hot) > a.max:
            print(f"   (showing {a.max} of {len(hot)})")
        for i in hot[:a.max]:
            print(f"   [{i['agency']} · {i['type']}] {i['date']}")
            print(f"     {i['title'][:150]}")
            if i["url"]:
                print(f"     {i['url']}")
        print()
    if cold:
        print(f"○ other agency activity ({len(cold)}) — posture, not ours:")
        _cshow = max(4, a.max // 2)
        if len(cold) > _cshow:
            print(f"   (showing {_cshow} of {len(cold)})")
        for i in cold[:_cshow]:
            print(f"   [{i['agency']} · {i['type']}] {i['date']} — {i['title'][:110]}")
        print()
    print("   Reminder: a proposal is not a rule, and a rule is not law until published.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
