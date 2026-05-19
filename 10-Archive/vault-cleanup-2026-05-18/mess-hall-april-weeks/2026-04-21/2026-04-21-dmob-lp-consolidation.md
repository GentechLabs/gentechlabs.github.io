## DMOB — LP Monitor + Watchlist Consolidation (Apr 21, 6:42 PM EDT)

**Status:** Waiting on YoYo

Jordan asked me to collaborate with YoYo on combining the LP watcher cron with the crypto watchlist. Ran an audit:

- The "consolidated" `crypto-watchlist.py` script doesn't actually exist — docs reference it but no file found
- The consolidated cron job IDs in `Cron-Jobs-Reference.md` aren't in the active cron list
- Only `lp-range-monitor.py` (v1 + v2) scripts exist

Pinged YoYo in Strategies to confirm his cron state. Once he replies, I'll build the consolidated script: CMC token prices + DexScreener LP pool data in one cron.

**Pool:** `0x864d4e5ee7318e97483db7eb0912e09f161516ea` (LFJ AVAX/USDC 5bps)
