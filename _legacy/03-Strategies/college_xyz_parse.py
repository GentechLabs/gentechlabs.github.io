#!/usr/bin/env python3
"""Parse College.xyz careers page - handles RSC escaped JSON format."""
import json, re, sys, os, urllib.request

url = "https://www.college.xyz/careers"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req).read().decode("utf-8")

# Combine all RSC push blocks
push_blocks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.DOTALL)
full_text = ""
for block in push_blocks:
    try:
        unescaped = block.encode().decode('unicode_escape')
        full_text += unescaped
    except:
        full_text += block

# Find the initialCareers array
idx = full_text.find('"initialCareers":[')
if idx < 0:
    print("ERROR: initialCareers not found")
    sys.exit(1)

start = idx + len('"initialCareers":')
depth = 0
end = start
for i in range(start, min(start + 500000, len(full_text))):
    c = full_text[i]
    if c == '[':
        depth += 1
    elif c == ']':
        depth -= 1
        if depth == 0:
            end = i + 1
            break

jobs_json = full_text[start:end]
jobs = json.loads(jobs_json)
print(f"Total jobs on page: {len(jobs)}")

# Filter criteria
crypto_tech_tags = {
    "Engineering", "Software", "Crypto", "Blockchain", "Web3", "DeFi",
    "Fintech", "Tech", "Technology", "Data", "Analytics", "Python",
    "DevOps", "Backend", "Frontend", "Full Stack", "Smart Contract",
    "Protocol", "Infrastructure", "Security", "ML", "AI", "Research",
    "Quant", "Trading", "GTM", "Growth"
}

all_remote = []
matching = []

for j in jobs:
    loc = (j.get("location") or "").lower()
    name = j.get("name", "")
    company = j.get("company", {}).get("name", "") if isinstance(j.get("company"), dict) else ""
    stipend = j.get("stipend") or ""
    tags = j.get("tags") or []
    role_type = j.get("role_type", "")
    comp_type = j.get("compensation_type", "")
    apply_link = j.get("apply_link", "")
    apply_email = j.get("apply_email", "")
    status = j.get("status", "")
    desc = j.get("description", "")
    created = j.get("created_at", "")
    job_id = j.get("id")
    metadata = j.get("metadata") or {}
    description_long = metadata.get("descriptionLong", "")

    if "remote" in loc:
        all_remote.append({
            "id": job_id,
            "company": company,
            "title": name,
            "location": j.get("location"),
            "stipend": stipend,
            "tags": tags,
            "role_type": role_type,
        })

    if "remote" not in loc:
        continue
    if role_type != "internship":
        continue

    tag_set = set(tags) if tags else set()
    has_crypto_tech = bool(tag_set & crypto_tech_tags)
    if not has_crypto_tech:
        combined = f"{name} {desc}".lower()
        crypto_keywords = ["crypto", "blockchain", "web3", "defi", "fintech", "engineering", "software", "protocol"]
        if not any(kw in combined for kw in crypto_keywords):
            continue

    # Pay check - check stipend AND descriptionLong
    pay_ok = False
    pay_note = ""
    combined_pay_text = f"{stipend} {description_long}".strip()

    if comp_type == "paid":
        # Check for dollar amounts in combined pay text
        dollar_amounts = re.findall(r'\$+([0-9,]+(?:\.\d+)?)', combined_pay_text)
        
        if dollar_amounts:
            amounts = [float(a.replace(',', '')) for a in dollar_amounts]
            max_amt = max(amounts)
            
            # Check if any amount looks like hourly ($25+)
            if any(a >= 25 for a in amounts):
                pay_ok = True
                pay_note = combined_pay_text.strip() or "Paid"
            # Check if any amount looks like monthly ($4K+)
            elif any(a >= 4000 for a in amounts):
                pay_ok = True
                pay_note = combined_pay_text.strip() or "Paid"
            # Has dollar amounts but all below threshold
            else:
                pay_note = f"Below threshold (max ${max_amt})"
                pay_ok = False
        elif combined_pay_text.strip():
            # Has text but no dollar amounts - might be "Paid" etc.
            pay_ok = True
            pay_note = combined_pay_text.strip()
        else:
            # Paid but no amount info at all
            pay_ok = True
            pay_note = "Paid (amount not listed)"

    if not pay_ok:
        continue

    matching.append({
        "id": job_id,
        "company": company,
        "title": name,
        "location": j.get("location"),
        "stipend": stipend or "Paid",
        "pay_note": pay_note,
        "tags": tags,
        "apply_link": apply_link,
        "apply_email": apply_email,
        "desc": desc,
        "created": created,
        "status": status,
    })

print(f"All remote roles: {len(all_remote)}")
for r in all_remote:
    print(f"  ID={r['id']} | {r['company']} | {r['title']} | {r['stipend']} | {r['location']} | tags={r['tags']} | type={r['role_type']}")
print()
print(f"Remote crypto/tech internships matching all criteria: {len(matching)}")
for m in matching:
    print(f"\n=== {m['company']} — {m['title']} ===")
    print(f"  Location: {m['location']}")
    print(f"  Pay: {m['pay_note']}")
    print(f"  Tags: {m['tags']}")
    print(f"  Description: {(m['desc'] or '')[:300]}")
    print(f"  Apply: {m['apply_link'] or m['apply_email']}")
    print(f"  Created: {m['created']}")
    print(f"  Job ID: {m['id']}")

output_path = "/root/vaults/gentech/03-Strategies/college_xyz_latest.json"
with open(output_path, "w") as f:
    json.dump({
        "scan_date": "2026-06-23",
        "total_jobs": len(jobs),
        "all_remote": all_remote,
        "matching_jobs": matching,
    }, f, indent=2)
print(f"\nResults saved to {output_path}")
