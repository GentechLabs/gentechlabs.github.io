# Filtering Decision Tree — From Raw Hit to Qualified Opportunity

## Step 1: Initial Collection
Gather all events matching user domain keywords from platform homepages and search results.

## Step 2: Barrier Screening (EXIT IF ANY TRUE)
Check each event's description/requirements page:

```
Does the event REQUIRE ANY of the following?
├─ Staking/deposit? → FILTER OUT
├─ Portfolio submission? → FILTER OUT
├─ 2+ years experience? → FILTER OUT
├─ Specific certifications? → FILTER OUT
├─ Invite-only application? → FILTER OUT
└─ Domain-restricted email (.edu/corp)? → FILTER OUT
```

If YES to any → STOP analyzing this event, add to "Filtered Out" list with reason.

## Step 3: Eligibility Confirmation (CONTINUE ONLY IF ALL FALSE)
```
Is the event:
├─ Open to target geography? → YES
├─ Compatible with user's skill level? → "Beginner-friendly" stated → YES
├─ Free to enter (no monetary stake)? → YES
└─ Public submission (not invite-only)? → YES
```
All YES → Proceed to enrichment.

## Step 4: Enrichment & Categorization
Extract structured data:
- Prize Pool: Total USD value (convert from crypto/other currencies if needed)
- Deadline: Date + timezone (calculate days remaining from current date)
- Stack: Technologies explicitly mentioned (SDKs, protocols, languages)
- Format: Online vs In-person, team size limits
- Submission: Code repo? Video? Demo? Live presentation?

## Step 5: Quality Check
Before including in final report:
- Verify links are live (not 404)
- Confirm deadline hasn't already passed
- Double-check barrier status (re-read requirements page)
- Cross-reference prize pool against multiple sources if possible

## Edge Cases & How to Handle

| Scenario | Decision Rule |
|----------|---------------|
| "Wallet recommended but not required" | INCLUDE — barrier not mandatory |
| "Students preferred but professionals welcome" | INCLUDE — open entry |
| "First-time hackathon encouraged" | INCLUDE — beginner-friendly signal |
| "Open to all countries (exceptions apply)" | INCLUDE unless user has geo-restrictions |
| "Staking required but financial aid available" | FILTER OUT — barrier still exists even with aid |
| "Portfolio preferred but not required" | FILTER OUT — "preferred" creates de facto barrier |

## Confidence Scoring
Rate each event's open-entry status:
- **High Confidence (✓✓✓)**: Explicit "no experience required" + free registration
- **Medium Confidence (✓✓)**: No barriers stated, but ambiguity in requirements
- **Low Confidence (✓)**: Requires interpretation ("open to all skill levels" but asks for GitHub)
When in doubt, FILTER OUT and note uncertainty in "Filtered Out" section.
