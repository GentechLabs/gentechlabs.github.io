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
FEED_SCHEDULE="0 */2 * * *"
SECURITY_SCHEDULE="0 */4 * * *"
INTEL_SCHEDULE="0 9,18 * * *"

# --- Alert Thresholds ---
ALERT_THRESHOLD=1
