"""GenTech x402 backend — Lineage Guard (port 8095).

Data lineage blast-radius guard for the DataHub Agent Hackathon.
Walks DataHub downstream lineage, classifies affected assets, issues
BLOCK/REVIEW/SAFE verdict. Served behind the api.gentechlabs.net x402 gateway
as a pay-per-call endpoint. Reads the local DataHub GMS on port 28080.
"""
import os
import json
import urllib.request

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GenTech Lineage Guard", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GMS = os.environ.get("DATAHUB_GMS_URL", "http://localhost:28080")
GRAPHQL = GMS.rstrip("/") + "/api/graphql"

SEVERITY = {
    "DATASET": "medium",
    "CHART": "high",
    "DASHBOARD": "critical",
    "DATAFLOW": "high",
    "ML_MODEL": "high",
    "DATAPROCESS": "medium",
    "NOTEBOOK": "medium",
    "TAG": "low",
    "GLOSSARY_TERM": "low",
}


def gql(query):
    req = urllib.request.Request(
        GRAPHQL,
        data=json.dumps({"query": query}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def entity_type(urn):
    if urn.startswith("urn:li:dataset:"):
        return "DATASET"
    for prefix in ("chart", "dashboard", "dataFlow", "dataJob", "mlModel", "dataProcess", "notebook"):
        if urn.startswith(f"urn:li:{prefix}:"):
            return prefix.upper()
    return "UNKNOWN"


def asset_name(urn):
    inner = urn.split("(", 1)[-1].rstrip(")")
    parts = [p for p in inner.split(",") if p and "PROD" not in p and "DEV" not in p]
    return parts[-1] if parts else urn


def friendly(urn):
    q = ('{ entity(urn: "%s") { urn ... on Dataset { properties { name } } '
         '... on Chart { properties { name } } ... on Dashboard { properties { name } } } }' % urn)
    try:
        data = gql(q)["data"]["entity"]
        nm = (data.get("properties") or {}).get("name")
        return nm or None
    except Exception:
        return None


def blast_radius(urn, direction="DOWNSTREAM", depth=0, max_depth=5, seen=None, results=None):
    if seen is None:
        seen, results = set(), {}
    if depth > max_depth or urn in seen:
        return results
    seen.add(urn)
    q = ('{ dataset(urn: "%s") { lineage(input: { direction: %s, start: 0, count: 100 }) { '
         "total relationships { type entity { urn } degree } } } }" % (urn, direction))
    try:
        data = gql(q)["data"]["dataset"]
    except Exception:
        return results
    if not data or not data.get("lineage"):
        return results
    for rel in data["lineage"]["relationships"]:
        ent_urn = rel["entity"]["urn"]
        results[ent_urn] = {
            "urn": ent_urn,
            "type": entity_type(ent_urn),
            "name": friendly(ent_urn) or asset_name(ent_urn),
            "degree": rel.get("degree", 1),
            "relation": rel.get("type", direction),
        }
        blast_radius(ent_urn, direction, depth + 1, max_depth, seen, results)
    return results


def search_datasets(term):
    res = gql('{ search(input: { type: DATASET, query: "%s", start: 0, count: 10 }) '
              "{ searchResults { entity { urn ... on Dataset { properties { name } } } } } }" % term)
    return res["data"]["search"]["searchResults"]


def build_report(source_urn, source_name, affected):
    counts, criticals = {}, []
    for urn, info in affected.items():
        t = info["type"]
        counts[t] = counts.get(t, 0) + 1
        if SEVERITY.get(t, "low") in ("high", "critical"):
            criticals.append(info)
    total = len(affected)
    return {
        "subject": {"urn": source_urn, "name": source_name},
        "blast_radius_total": total,
        "assets_at_risk_by_type": counts,
        "critical_assets": [c["name"] for c in criticals],
        "severity_summary": {
            "critical": sum(1 for c in criticals if SEVERITY[c["type"]] == "critical"),
            "high": sum(1 for c in criticals if SEVERITY[c["type"]] == "high"),
            "medium": sum(1 for _, i in affected.items() if SEVERITY.get(i["type"], "low") == "medium"),
            "low": sum(1 for _, i in affected.items() if SEVERITY.get(i["type"], "low") == "low"),
        },
        "recommendation": (
            "BLOCK" if any(SEVERITY.get(c["type"], "low") in ("high", "critical") for c in criticals)
            else "REVIEW" if total else "SAFE"
        ),
    }


@app.get("/v1/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "service": "lineage_guard"}


@app.get("/v1/lineage/guard")
async def guard(urn: str, direction: str = "DOWNSTREAM"):
    if not urn.startswith("urn:li:"):
        return {"error": "invalid urn"}, 400
    try:
        affected = blast_radius(urn, direction.upper())
    except Exception as e:
        return {"error": f"DataHub query failed: {e}"}, 502
    if not affected:
        return {"error": "urn not found or no lineage", "urn": urn}, 404
    report = build_report(urn, asset_name(urn), affected)
    return {"data": report}


@app.get("/v1/lineage/guard/search")
async def guard_search(q: str, direction: str = "DOWNSTREAM"):
    try:
        hits = search_datasets(q)
    except Exception as e:
        return {"error": f"DataHub search failed: {e}"}, 502
    if not hits:
        return {"error": f"no dataset matched '{q}'"}, 404
    urn = hits[0]["entity"]["urn"]
    affected = blast_radius(urn, direction.upper())
    report = build_report(urn, asset_name(urn), affected)
    return {"data": {"matched_urn": urn, **report}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8095")))
