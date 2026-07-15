#!/usr/bin/env python3
"""Forge Desktop Heartbeat — writes a timestamp every 5 min so Forge-cloud knows the PC is on."""
import os
from datetime import datetime, timezone

path = "/root/vaults/gentech/scripts/.desktop-heartbeat"
ts = datetime.now(timezone.utc).timestamp()

with open(path, "w") as f:
    f.write(str(ts))

print(f"❤️  Heartbeat written: {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
