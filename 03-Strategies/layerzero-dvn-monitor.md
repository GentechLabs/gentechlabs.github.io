# LayerZero DVN Security Monitor Report
**Date Checked**: May 6, 2026

## Executive Summary
LayerZero's DVN security model remains unchanged since the April 2026 KelpDAO incident. The protocol continues to recommend multi-DVN configurations for production applications, with no new mandatory requirements introduced.

## Key Findings

### 1. KelpDAO Incident Analysis
- **Date**: April 18, 2026
- **Impact**: ~$290M exploit
- **Root Cause**: KelpDAO used a 1-of-1 DVN setup with LayerZero Labs as the sole verifier
- **LayerZero's Position**: Protocol functioned as intended; no vulnerability found
- **Attribution**: Likely DPRK's Lazarus Group (TraderTraitor)

### 2. Current DVN Requirements
**Official Documentation Status**: No changes detected since incident

**Critical Requirements (from Integration Checklist)**:
- DVN configuration must be explicitly set on all pathways
- Applications must configure their own DVNs (LayerZero maintains neutral stance)
- **Production pathways must use more than one DVN**
- Single DVN configurations are not considered production-ready

**Configuration Process**:
- Manual setup via `setConfig` function
- Both send and receive configurations must match
- DVNs must be provided in alphabetical order
- Block confirmations must be correctly set

### 3. Dune Analytics Statistics
**Unable to verify current stats** due to access restrictions. Historical distribution (as of early 2026):
- 47% of pathways: 1-of-1 DVN
- 45% of pathways: 2-of-2 DVN  
- ~5% of pathways: 3-of-3+ DVN

**Note**: This distribution likely remains similar given the short time since the incident.

### 4. Competitor Response
No significant changes detected from Wormhole, Axelar, or Hyperlane. No major security overhauls or marketing campaigns capitalizing on the LayerZero incident observed.

## Risk Assessment
**Risk Level**: Unchanged

**Factors**:
- Protocol security model remains robust and unchanged
- Incident attributed to user configuration error, not protocol vulnerability
- Clear recommendations for multi-DVN setups already existed
- No indication of widespread adoption of improved DVN configurations yet

## Action Items
None required. Current LayerZero DVN requirements remain appropriate. Continue monitoring for any protocol-level changes or adoption of multi-DVN configurations.

## Sources
- LayerZero Blog: KelpDAO Incident Statement (April 19, 2026)
- LayerZero Documentation: Integration Checklist, DVN Configuration Guides
- Historical Dune Analytics data