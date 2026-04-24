# TraderJoe LP Tracking Configuration

## Pool Details
- **Pair**: AVAX / USDC
- **Version**: v2.2 (5 bps)
- **Pool Address**: `0x864d4e50e7318e97483db7cb0912e09f161516ea`
- **WAVAX Address**: `0x31f66aa3c1e785363f0875b17ba74e27b85fd66c7`
- **USDC Address**: `0x9b7e9f9ef8734c71904d002f8b6bc66dd9c48a6e`

## Strategy Configuration
- **Target Range**: 9.36 - 9.53 USDC per AVAX
- **Monitoring Frequency**: Every 2 hours (7 AM - 9 PM EDT)
- **Data Sources**: DexScreener API, LFI API

## Status
- Migrating to API-based monitoring to remove dependency on vision-analysis tools for cron updates.
