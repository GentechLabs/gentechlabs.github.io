# Social Layer POC — Configuration
# Edit these to customize what the social layer monitors

# --- Security Radar Keywords ---
SECURITY_KEYWORDS=(
    "smart contract exploit"
    "vulnerability disclosed"
    "rug pull"
    "flash loan attack"
    "reentrancy"
    "private key leak"
    "protocol hack"
    "funds stolen"
)

# --- Security Researchers to Watch ---
SECURITY_RESEARCHERS=(
    "samczsun"
    "ZachXBT"
    "pcaversaccio"
    "tayvano"
    "SlowMist_Team"
    "PeckShieldAlert"
    "CertiKAlert"
    "0xfoobar"
    "OfficerCia"
    "MEVGuard"
)

# --- DeFi Protocols to Monitor ---
DEFI_PROTOCOLS=(
    "aaboraave"
    "Uniswap"
    "LidoFinance"
    "CurveFinance"
    "Avalancheavax"
    "base"
    "chainlink"
    "Optimism"
    "GMX_IO"
    "Balancer"
)

# --- Hackathon / Builder Accounts ---
HACKATHON_ACCOUNTS=(
    "ETHGlobal"
    "SolanaConflicts"
    "EthDenver"
    "gitcoin"
    "Kernel"
    "aaboragrants"
)

# --- Cron Schedules ---
# Feed monitor: every 2 hours
FEED_SCHEDULE="0 */2 * * *"

# Security radar: every 4 hours
SECURITY_SCHEDULE="0 */4 * * *"

# Crypto intel: twice daily (9am, 6pm UTC)
INTEL_SCHEDULE="0 9,18 * * *"

# --- Alert Thresholds ---
# Minimum new items to trigger Telegram alert
ALERT_THRESHOLD=1
