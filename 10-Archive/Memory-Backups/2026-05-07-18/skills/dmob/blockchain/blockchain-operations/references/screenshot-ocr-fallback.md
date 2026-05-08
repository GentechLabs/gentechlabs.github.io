# Screenshot OCR Fallback Pattern

## When to Use
Vision model (`browser_vision`) fails with model errors. Jordan sends a screenshot of a trading UI (LFJ, DexScreener, etc.) and you need to extract data.

## Workflow
```bash
# 1. Verify image exists
file /root/.hermes/profiles/dmob/cache/images/<image_hash>.jpg

# 2. OCR with tesseract (works well for clean trading UIs)
tesseract /root/.hermes/profiles/dmob/cache/images/<image_hash>.jpg stdout 2>/dev/null | head -80

# 3. Parse key fields from messy OCR output
# Common patterns in LFJ/LP UIs:
#   "Deposit Balance" -> position size in USD
#   "Current Price" / "AVAX" numbers -> pool price
#   "Total Fees Earned" -> cumulative fees
#   "Fees Earned (24H)" -> daily fee estimate
#   "ByRange" / "Radius" / "Curve" -> liquidity shape
#   Range values often appear as decimal numbers (e.g., 9.00578, 9.59400)
```

## Known Issues
- Tesseract mangles special characters, small fonts, and overlapping text
- Price values like "9.46004000" may be concatenated with labels
- Balance values may appear as "$9858" instead of "$98.58" (missing decimal)
- Shape labels ("ByRange", "Radius", "Curve") are usually readable
- Decorative/colored text produces garbage -- focus on numeric patterns

## Fallback Chain
1. `browser_vision` -> if model error, continue
2. `tesseract` OCR -> parse key numbers manually
3. Ask Jordan to type the specific values you need
4. Check on-chain via `lp-position-reader.py` script (most reliable for position data)

## Example Output Recovery
```
# Raw OCR might produce:
# "Deposit Balance Betnce $9858 SOAS"
# Parse as: Balance ~ $98.58

# "Price ByRange Sy Radius"
# Parse as: Shape options = ByRange, Radius

# "Total Fes Famed 20 $048"
# Parse as: Total Fees Earned ~ $0.48
```
