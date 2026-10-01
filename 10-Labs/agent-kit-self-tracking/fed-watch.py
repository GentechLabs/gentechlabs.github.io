#!/usr/bin/env python3
"""fed-watch.py — what was SAID, not just when.

Jordan (Sep 16 2026): "let's look for where we can go to track these meetings and what's
being said after. So not only do we know the days that is happening, but we also can get
the details."

WHY THIS EXISTS — the gap it closes
  We already had three of the four layers:
    DATES      agentic-calendar.json            (DST-correct FOMC schedule)
    DOCUMENTS  federalregister.gov              (sec-cftc-watch.py — proposals, comment clocks)
    ODDS       Kalshi / Polymarket              (steward_prediction.py)
  Missing entirely: SPEECH. A Federal Register document appears weeks after the remark that
  announced it, and never carries the press conference, the minutes, or the speeches around
  a decision. That is the layer where intent becomes visible first.

SOURCES — every one probed live before being trusted (discover-news-sources.py):
  9 of 11 candidates answered. SEC litigation (403) and the US Treasury press feed (404) do not.

  Federal Reserve  press_all · press_monetary · speeches · testimony
  SEC              press releases · speeches & statements
  CFTC             press releases · speeches & testimony

SILENCE DOCTRINE: prints nothing when nothing relevant is new. New items only, tracked by a
state file of seen ids, so a feed re-serving its last 10 items does not re-alert.
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
      "Accept": "application/rss+xml, application/xml, text/html;q=0.9"}

STATE = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/.fed-watch-state.json"

FEEDS = [
    ("FED",  "press",      "https://www.federalreserve.gov/feeds/press_all.xml"),
    ("FED",  "money",      "https://www.federalreserve.gov/feeds/press_monetary.xml"),
    ("FED",  "speech",     "https://www.federalreserve.gov/feeds/speeches.xml"),
    ("FED",  "testimony",  "https://www.federalreserve.gov/feeds/testimony.xml"),
    ("SEC",  "press",      "https://www.sec.gov/news/pressreleases.rss"),
    ("SEC",  "statement",  "https://www.sec.gov/news/speeches-statements.rss"),
    ("CFTC", "press",      "https://www.cftc.gov/RSS/RSSGP/rssgp.xml"),
    ("CFTC", "speech",     "https://www.cftc.gov/RSS/RSSST/rssst.xml"),
    # ── ADDED 2026-09-19 (Jordan: "anything related to crypto that's relevant to us and could
    # affect us"). Both verified reachable and returning real items before being added; ten other
    # candidate agency feeds were tested and REJECTED as 404/403 (FinCEN, OCC, FDIC, IRS, Treasury,
    # NYDFS, White House, SEC litigation) — so they are recorded here as tested-and-unavailable
    # rather than silently omitted.
    ("CFTC", "enforcement", "https://www.cftc.gov/RSS/RSSENF/rssenf.xml"),   # 10 items — ACTIONS
    ("NIST", "news",        "https://www.nist.gov/news-events/news/rss.xml"), # 40 items — AI std.
]

# ── FEDERAL REGISTER — one API, EVERY agency ────────────────────────────────
# Jordan (2026-09-19): "The SEC and the CFTC is going to have to step in... anything related to
# crypto that's relevant to us and could affect us."
#
# Ten agency-specific RSS feeds 404'd. This replaces all of them: the Federal Register is the single
# official record of every agency's rulemaking, and its API supports term search. Verified live:
# "crypto" 514 documents, "digital asset" 3,221, "artificial intelligence" 1,572 — and filtering to
# RULE + PRORULE gives 105 crypto documents WITH comment-close dates attached, which is the part that
# actually requires action. It surfaces agencies we had no feed for at all: Treasury, IRS, Justice,
# Commerce/NIST, PCAOB.
# ⚠️ QUOTED PHRASES ARE LOAD-BEARING — DO NOT "SIMPLIFY" THEM AWAY (fixed 2026-09-24).
# The FR API treats an UNQUOTED multi-word term as AND-OF-WORDS, not as a phrase. Measured
# 2026-09-24: term "digital asset" returned 1,704 documents — including a 649,454-character
# NRC reactor rule (FR 2026-19568) and an FAA oxygen rule (2026-19584). Neither contains the
# literal phrase even once (raw-text scan: "digital asset" 0 hits); a 650 KB regulation
# contains nearly every common English word, so an AND-of-words match is satisfied by
# "digital controls" + "the licensee's assets". The same shape hit "money transmission"
# (3,440 documents, matched on "save them money" + "disease transmission"). Quoting forces
# true phrase matching: "digital asset" 1,704 -> 89, "money transmission" 3,440 -> 48.
# Two junk items reached Jordan's desk on 2026-09-24 because of this.
# Verified BOTH directions before shipping: the two junk docs drop; every known-relevant
# control document survives (Regulation Crypto Assets, Transfer Agent Rules, GENIUS
# stablecoin, Huione Group, Compute Derivatives RFC, Prediction Markets, Resolution
# Submissions). Body-scanned a 30-document sample of what quoting would drop: 30/30
# genuinely irrelevant (cryptographic authentication, FFRDC "autonomous organization").
# "artificial intelligence agent" -> "artificial intelligence": the 3-word form returned
# the SAME 351 documents as the 2-word form, i.e. the extra word filtered nothing and only
# narrowed the phrase match; the quoted 2-word form is the honest term.
FR_TERMS = [
    '"crypto"', '"cryptocurrency"', '"crypto asset"', '"crypto assets"',
    '"digital asset"', '"digital assets"', '"stablecoin"', '"stablecoins"',
    '"tokenized"', '"tokenization"', '"money transmission"', '"money transmitter"',
    '"decentralized finance"', '"DeFi"',
    '"artificial intelligence"', '"AI agent"', '"AI agents"',
    '"autonomous agent"', '"autonomous agents"', '"agentic"',
]
FR_TYPES = ["RULE", "PRORULE"]     # final rules and proposed rules — NOT the notice firehose
FR_FIELDS = ["title", "publication_date", "agencies", "type", "html_url",
             "comments_close_on", "document_number", "action"]
FR_MAX = 25


def fetch_federal_register() -> list[dict]:
    """Return the newest crypto/AI rules and proposed rules from every agency.

    Shaped as feed items so they flow through the same watermark, filter and renderer as the RSS
    feeds — one code path, one watermark, no special case to drift.
    """
    out: list[dict] = []
    for term in FR_TERMS:
        params = [("per_page", str(FR_MAX)), ("order", "newest"),
                  ("conditions[term]", term)]
        for t in FR_TYPES:
            params.append(("conditions[type][]", t))
        for f in FR_FIELDS:
            params.append(("fields[]", f))
        url = "https://www.federalregister.gov/api/v1/documents.json?" + urllib.parse.urlencode(params)
        body = fetch(url, timeout=40)
        if not body:
            continue
        try:
            d = json.loads(body)
        except Exception:                                            # noqa: BLE001
            continue
        for r in d.get("results", []):
            title = r.get("title") or ""
            if not title:
                continue
            ag = ", ".join(a.get("name", "") for a in (r.get("agencies") or [])[:2]) or "Federal Register"
            dtype = r.get("type") or ""
            close = r.get("comments_close_on") or ""
            desc = r.get("action") or ""
            if close:
                desc = f"COMMENT WINDOW CLOSES {close}. " + desc
            out.append({
                "title": title,
                "link": r.get("html_url") or "",
                "date": r.get("publication_date") or "",
                "desc": desc[:300],
                "_agency": ag[:28],
                "_kind": "rule" if dtype == "Rule" else "proposed rule",
                "_doc": r.get("document_number") or "",
            })
    # de-dup: the same document surfaces under several terms
    seen_docs, uniq = set(), []
    for it in out:
        k = it["_doc"] or it["title"]
        if k in seen_docs:
            continue
        seen_docs.add(k)
        uniq.append(it)
    return uniq

# Relevance filter. Kept tight on purpose: a watch that fires on everything is noise, and a
# noisy watch gets ignored — which is worse than no watch. Word boundaries matter: the bare
# string "defi" matches "definition", the exact bug caught in sec-cftc-watch.py.
KEYWORDS = [
    r"\bcrypto", r"\bdigital asset", r"\bstablecoin", r"\bDeFi\b", r"decentralized finance",
    r"\btokeniz", r"\bblockchain", r"\bmarket structure", r"\bpayment (rails?|systems?|processors?|networks?|services?|charters?)\b", r"\bcustody\b",
    r"\brate (decision|cut|hike|path)", r"\bmonetary policy", r"\bfederal funds",
    r"\binflation", r"\bFOMC\b", r"\bCLARITY\b", r"\bGENIUS\b", r"\bexchange traded",
    r"\bdigital dollar", r"\bRWA\b", r"\breal-world asset",
    # ── REGULATORY-ACTION vocabulary, added 2026-09-17 ──────────────────────────────
    # WHY: the filter required the vocabulary of OUR interest, so a regulator could take
    # an action aimed squarely at us and still be dropped. Measured case: "CFTC Staff
    # Issues No-Action Position to Providers of Passive Software" (Release 9300-26,
    # 2026-09-17) — a staff no-action position for providers of automated trading
    # software, i.e. exactly what this treasury is — was DROPPED, because the headline
    # contains no crypto/DeFi/stablecoin term. Five other CFTC items dropped the same way.
    # The state file proved it: 34 Federal Reserve entries, ZERO CFTC entries, ever.
    # Agencies describe actions in their own language. Match the ACTION, not just the asset.
    r"\bno-action\b", r"\bintroducing broker", r"\bbroker", r"\bdealer\b", r"\bdealer\b",
    r"\bclearing\b", r"\bcleared\b", r"\bswap", r"\bderivativ", r"\bmargin\b",
    r"\bregistration\b", r"\bregister\b", r"\bfutures commission merchant\b", r"\bFCM\b",
    r"\bDCM\b", r"\bSEF\b", r"\bevent contract", r"\bprediction market",
    r"\bfinal rule\b", r"\brulemaking\b", r"\bproposed rule\b", r"\bexempt",
    r"\bpassive software\b", r"\binnovation\b", r"\benforcement\b", r"\bsettlement\b",
    # ── AI / AI-AGENT vocabulary, added 2026-09-17 ──────────────────────────────────
    # WHY: Jordan — "see if they also say anything about AI or AI agents as well."
    # We are an AI agent that manages capital, so an agency speaking about AI agents or
    # automated trading is speaking about us directly. Measured before adding: of 135 live
    # feed items, exactly 2 contain this language ("Barr, Will Artificial Intelligence
    # Broadly Raise Living Standards..." and "Bowman, Opening Remarks on Sound Practices
    # for Artificial Intelligence") — ~1.5% noise, and both are genuinely on-topic
    # regulator speech about AI governance. Cheap, so it goes in.
    r"\bartificial intelligence\b", r"\bA\.I\.\b", r"\bAI\b", r"\bmachine learning\b",
    r"\balgorithmic\b", r"\bautomated\b", r"\bautonomous\b", r"\bagentic\b",
    r"\bAI agents?\b", r"\bmodel risk\b",
    # ── OUR EXPOSURES, added 2026-09-19 (Jordan: "relevant to us and could affect us") ──────
    # Three surfaces this treasury actually touches, none of which the filter covered:
    #   1. PAYMENTS — we SELL x402 services. Money-transmission rules govern our seller side.
    #   2. TOKENIZED SECURITIES — we now track tokenized equities (Dinari/Ondo + SEC 2026-90).
    #   3. YIELD MECHANICS — staking/LP treatment decides whether our fee income is compliant.
    r"\bmoney transmission\b", r"\bmoney services business\b", r"\bMSB\b", r"\bremittance",
    r"\bprepaid\b", r"\bfintech charter\b", r"\bpayment stablecoin",
    r"\btokenized (stock|equit|securit)", r"\bdigital asset securit", r"\bNMS stock\b",
    r"\bstaking\b", r"\bliquidity pool", r"\byield\b", r"\blending protocol",
    r"\bself-regulatory organization\b", r"\bSRO\b", r"\bcomment (period|window|deadline)",
]
RE = re.compile("|".join(KEYWORDS), re.I)

# ── NOISE SUPPRESSOR (added 2026-09-19) ─────────────────────────────────────
# "A noisy watch gets ignored — which is worse than no watch." Measured on the first live run of the
# widened filter: 214 items, of which 16 lines were the Federal Reserve's personnel enforcement
# actions against former bank employees ("former employee of Northstar Bank", "former employee of
# American Express Travel Related Services"). Those match on \benforcement\b — a keyword added
# deliberately for the CFTC no-action case — and have nothing to do with this treasury.
# Suppressed BEFORE the relevance test, and COUNTED so the suppression stays auditable rather than
# becoming a second silent filter.
NOISE = re.compile(
    r"former employee|"
    r"announces termination of enforcement action|"
    r"issues enforcement action(s)? with (former|SouthPoint|United|Regions|Quontic|Deutsche)|"
    r"termination of enforcement action(s)? with",
    re.I,
)

# A statement from the Chair or a policy decision is always worth surfacing.
ALWAYS = re.compile(r"\bFOMC\b|\bmonetary policy\b|\bChair\b|\bminutes\b", re.I)


def fetch(url: str, timeout: int = 25) -> bytes | None:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(500_000)
    except Exception:                                                # noqa: BLE001
        return None


def strip_ns(tag: str) -> str:
    return tag.split("}")[-1]


def parse_feed(url: str) -> list[dict]:
    body = fetch(url)
    if not body:
        return []
    try:
        root = ET.fromstring(body)
    except Exception:                                                # noqa: BLE001
        return []
    items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
    out = []
    for it in items:
        d: dict[str, str] = {}
        for ch in it:
            t = strip_ns(ch.tag)
            if t == "title":
                d["title"] = (ch.text or "").strip()
            elif t in ("link", "id"):
                d["link"] = d.get("link") or (ch.text or ch.attrib.get("href") or "").strip()
            elif t in ("pubDate", "updated", "published", "date"):
                d["date"] = d.get("date") or (ch.text or "").strip()
            elif t in ("description", "summary", "content"):
                raw = ch.text or ""
                raw = re.sub(r"<[^>]+>", " ", raw)
                raw = html.unescape(html.unescape(raw))   # feeds double-encode: &amp;#39;
                d["desc"] = d.get("desc") or raw.strip()[:300]
        d["_feed"] = url
        if d.get("title"):
            out.append(d)
    return out


def load_state() -> dict:
    try:
        with open(STATE) as f:
            return json.load(f)
    except Exception:                                                # noqa: BLE001
        return {"seen": []}


def save_state(s: dict) -> None:
    s["seen"] = s.get("seen", [])[-600:]
    s["updated_at"] = datetime.now(timezone.utc).isoformat()
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as f:
        json.dump(s, f, indent=1, separators=(",", ":"))


# ── FR BODY VERIFIER (added 2026-09-24) ─────────────────────────────────────
# The FR pass deliberately skips RE ("pre-filtered by term at the API"). That reasoning was
# sound when the API did what we assumed — but an unquoted multi-word term is matched as
# AND-of-words, so a 650 KB regulation satisfied "digital asset" with "digital controls" +
# "the licensee's assets". Skipping RE meant there was no second gate at all: whatever the
# API returned became an alert, i.e. a check that could not fail.
#
# The FR terms are now quoted (real phrases), so the API-side match is honest. This is the
# SECOND gate: fetch the document's own text and confirm the phrase is actually in it.
# Applied ONLY to items that are NEW this run (bounded: normally 0-2 documents), never to
# the whole pool — fetching 400+ raw texts every run would be slow and pointless.
#
# FAIL-OPEN, deliberately: if the text cannot be fetched, the item is KEPT and flagged
# UNVERIFIED. A verification step that silently DROPS items on a network blip is the same
# false-value family it exists to catch — and a regulator action aimed at us must never be
# hidden by our own tooling. Dropping is reserved for a POSITIVE, decisive result: the full
# document text was read and contains none of our vocabulary.
FR_VERIFY_MAX_BYTES = 1_500_000

VERIFY_TERMS = [
    r"\bcrypto\w*", r"\bcrypto[\s\-]assets?\b", r"\bdigital[\s\-]assets?\b",
    r"\bstablecoins?\b", r"\btokeni[sz]", r"\btokenization\b",
    r"\bmoney[\s\-]transmis\w*", r"\bdecentralized finance\b", r"\bDeFi\b",
    r"\bartificial intelligence\b", r"\bAI agents?\b",
    r"\bautonomous agents?\b", r"\bagentic\b",
]
VERIFY_RE = re.compile("|".join(VERIFY_TERMS), re.I)


def _fr_body_confirm(doc: str) -> bool | None:
    """True = phrase confirmed in the document's own text. False = full text read and it is
    NOT there (drop). None = could not read the text (KEEP, flag unverified)."""
    if not doc:
        return None
    try:
        api = (f"https://www.federalregister.gov/api/v1/documents/{doc}.json"
               "?fields[]=raw_text_url")
        raw = fetch(api, timeout=30)
        if not raw:
            return None
        url = (json.loads(raw) or {}).get("raw_text_url") or ""
        if not url:
            return None
        body = fetch(url, timeout=60)
        if not body:
            return None
        text = body[:FR_VERIFY_MAX_BYTES].decode("utf-8", "ignore")
        # Sanity: an HTML error page is not the document. Refuse to draw a verdict from it.
        if len(text) < 2000:
            return None
        return VERIFY_RE.search(text) is not None
    except Exception:                                                # noqa: BLE001
        return None


def main() -> int:
    fresh = "--fresh" in sys.argv or "--digest" in sys.argv
    state = load_state()
    seen = set(state.get("seen", []))

    hits, total, failed, dropped, noise = [], 0, [], [], []
    sources = [(a, k, u) for a, k, u in FEEDS]
    for agency, kind, url in sources:
        items = parse_feed(url)
        if not items:
            failed.append(f"{agency} {kind}")
            continue
        total += len(items)
        for it in items:
            key = (it.get("title", "") + "|" + it.get("date", ""))[:200]
            it["_key"] = key
            if NOISE.search(it.get("title", "")):
                # suppressed as known-irrelevant, and COUNTED — an uncounted filter is a blind spot
                noise.append({"agency": agency, "kind": kind, "title": it.get("title", "")})
                continue
            if not (RE.search(it["title"]) or ALWAYS.search(it["title"])):
                # NOT silent any more. A filter that drops without record is a blind spot
                # you cannot audit — the 2026-09-17 miss proved it. We still do not ALERT
                # on these (noise gets a watch ignored), but we now COUNT them, keep the
                # last run's set, and can list them with --show-filtered.
                dropped.append({"agency": agency, "kind": kind, "title": it.get("title", ""),
                                "link": it.get("link", ""), "date": it.get("date", "")})
                continue
            if key in seen and not fresh:
                continue
            it["_agency"], it["_kind"] = agency, kind
            hits.append(it)

    # ── FEDERAL REGISTER PASS — every agency, one source ────────────────────
    # Fed through the SAME watermark and renderer as the RSS feeds. These arrive pre-filtered by
    # term at the API, so they are recorded as their own source rather than re-tested against RE —
    # a rule that matches "crypto" at the Register is relevant by construction, and re-filtering it
    # through a keyword list is how a real action gets dropped (the 2026-09-17 CFTC miss).
    fr_items = fetch_federal_register()
    fr_new = 0
    fr_unverified = []
    for it in fr_items:
        key = f"FR|{it['_doc']}|{it['date']}"[:200]
        it["_key"] = key
        if key in seen and not fresh:
            continue
        # SECOND GATE — the API's term match is not evidence the document is about us.
        verdict = _fr_body_confirm(it.get("_doc", ""))
        if verdict is False:
            # Full text read, none of our vocabulary in it. Record and do NOT alert.
            dropped.append({"agency": it["_agency"], "kind": it["_kind"],
                            "title": it["title"], "link": it.get("link", ""),
                            "date": it.get("date", "")})
            continue
        if verdict is None:
            fr_unverified.append(it.get("_doc", ""))
        fr_new += 1
        hits.append(it)

    show_filtered = "--show-filtered" in sys.argv
    if show_filtered:
        print(f"🏛️ FILTER AUDIT — {len(dropped)} dropped by relevance, {len(noise)} suppressed as known noise")
        print("   (these did NOT alert; shown so the blind spot is auditable)\n")
        for d in dropped:
            print(f"  [{d['agency']} · {d['kind']}]  {d['title'][:120]}")
        print()
        return 0

    if not hits:
        print(f"NO_NEW (probed {total} items across {len(FEEDS)-len(failed)} feeds + "
              f"{len(fr_items)} Federal Register docs; {len(dropped)} filtered out)")
        if failed:
            print(f"  feeds not answering: {', '.join(failed)}")
        save_state({"seen": list(seen) + [h["_key"] for h in hits]})
        return 0

    print(f"🏛️ FED / REGULATOR WATCH — {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC")
    print(f"   {len(hits)} relevant item(s) — {len(FEEDS)-len(failed)} live feeds + {len(fr_items)} Federal Register docs\n")
    for h in hits:
        print(f"  [{h['_agency']} · {h['_kind']}]  {h.get('date','')[:31]}")
        print(f"    {h['title'][:140]}")
        if h.get("desc"):
            print(f"    {h['desc'][:200].strip()}")
        if h.get("_doc") and h["_doc"] in fr_unverified:
            print("    ⚠ body NOT VERIFIED this run — kept rather than dropped")
        if h.get("link"):
            print(f"    {h['link']}")
        print()
    if failed:
        print(f"  ⚠ feeds not answering this run: {', '.join(failed)}")
    seen.update(h["_key"] for h in hits)
    save_state({"seen": list(seen)})
    return 0


if __name__ == "__main__":
    sys.exit(main())
