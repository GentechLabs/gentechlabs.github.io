#!/usr/bin/env python3
"""
Agent Node Heartbeat — Proof of Liveness
Pings every 60s, logs uptime, tracks task completion.
Part of GenTech Agent Node Network.
"""

import json
import os
import time
import urllib.request
from datetime import datetime, timezone

# Config
AGENT_ID = os.environ.get("AGENT_ID", "gentech-001")
HEARTBEAT_INTERVAL = 60  # seconds
HEARTBEAT_LOG = os.path.expanduser("~/.hermes/scripts/heartbeat-log.json")
STATE_FILE = os.path.expanduser("~/.hermes/scripts/heartbeat-state.json")

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {
            "agent_id": AGENT_ID,
            "started_at": now_iso(),
            "total_heartbeats": 0,
            "total_tasks": 0,
            "failed_tasks": 0,
            "last_heartbeat": None,
            "consecutive_failures": 0
        }

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def log_heartbeat(heartbeat_data):
    os.makedirs(os.path.dirname(HEARTBEAT_LOG), exist_ok=True)
    try:
        with open(HEARTBEAT_LOG) as f:
            logs = json.load(f)
    except:
        logs = []
    
    logs.append(heartbeat_data)
    # Keep last 24h only (1440 entries at 60s interval)
    logs = logs[-1440:]
    with open(HEARTBEAT_LOG, "w") as f:
        json.dump(logs, f, indent=2)

def get_system_info():
    """Basic system metrics"""
    import subprocess
    info = {}
    try:
        result = subprocess.run(["free", "-m"], capture_output=True, text=True)
        lines = result.stdout.split("\n")
        if len(lines) > 1:
            parts = lines[1].split()
            info["memory_total_mb"] = int(parts[1])
            info["memory_used_mb"] = int(parts[2])
    except:
        pass
    
    try:
        result = subprocess.run(["uptime", "-p"], capture_output=True, text=True)
        info["uptime_raw"] = result.stdout.strip()
    except:
        pass
    
    return info

def send_heartbeat(state):
    """Create and log heartbeat"""
    sys_info = get_system_info()
    
    heartbeat = {
        "agent_id": state["agent_id"],
        "timestamp": now_iso(),
        "status": "active",
        "tasks_completed": state["total_tasks"],
        "tasks_failed": state["failed_tasks"],
        "accuracy": round(
            (state["total_tasks"] / max(state["total_tasks"] + state["failed_tasks"], 1)) * 100, 1
        ),
        "heartbeat_count": state["total_heartbeats"] + 1,
        "memory_usage_mb": sys_info.get("memory_used_mb", 0),
        "system_uptime": sys_info.get("uptime_raw", "unknown"),
        "consecutive_failures": state["consecutive_failures"]
    }
    
    # Update state
    state["total_heartbeats"] += 1
    state["last_heartbeat"] = heartbeat["timestamp"]
    state["consecutive_failures"] = 0
    
    # Log
    log_heartbeat(heartbeat)
    save_state(state)
    
    return heartbeat

def report_task(task_type, success=True):
    """Record a completed task"""
    state = load_state()
    if success:
        state["total_tasks"] += 1
    else:
        state["failed_tasks"] += 1
        state["consecutive_failures"] += 1
    save_state(state)

def get_uptime_stats():
    """Calculate uptime percentage"""
    state = load_state()
    try:
        with open(HEARTBEAT_LOG) as f:
            logs = json.load(f)
    except:
        return {"uptime_pct": 100.0, "total_heartbeats": 0, "days_running": 0}
    
    if not logs:
        return {"uptime_pct": 100.0, "total_heartbeats": 0, "days_running": 0}
    
    # Count expected heartbeats in period
    if len(logs) < 2:
        return {"uptime_pct": 100.0, "total_heartbeats": len(logs), "days_running": 0}
    
    first = datetime.fromisoformat(logs[0]["timestamp"].replace("Z", "+00:00"))
    last = datetime.fromisoformat(logs[-1]["timestamp"].replace("Z", "+00:00"))
    seconds_running = (last - first).total_seconds()
    expected_heartbeats = seconds_running / HEARTBEAT_INTERVAL
    
    uptime_pct = (len(logs) / max(expected_heartbeats, 1)) * 100
    days_running = seconds_running / 86400
    
    return {
        "uptime_pct": round(min(uptime_pct, 100.0), 2),
        "total_heartbeats": len(logs),
        "days_running": round(days_running, 1),
        "tasks_completed": state["total_tasks"],
        "tasks_failed": state["failed_tasks"],
        "accuracy": round(
            (state["total_tasks"] / max(state["total_tasks"] + state["failed_tasks"], 1)) * 100, 1
        )
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "status":
            stats = get_uptime_stats()
            print(json.dumps(stats, indent=2))
        elif cmd == "task":
            # Report a task completion
            success = sys.argv[2] != "fail" if len(sys.argv) > 2 else True
            report_task("general", success)
            print(f"Task reported: {'success' if success else 'fail'}")
        elif cmd == "heartbeat":
            state = load_state()
            hb = send_heartbeat(state)
            print(json.dumps(hb, indent=2))
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: heartbeat.py [heartbeat|status|task]")
    else:
        # Default: send heartbeat
        state = load_state()
        hb = send_heartbeat(state)
        print(json.dumps(hb, indent=2))
