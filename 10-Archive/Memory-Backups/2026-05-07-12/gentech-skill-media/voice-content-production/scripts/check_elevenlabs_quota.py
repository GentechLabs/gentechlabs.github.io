#!/usr/bin/env python3
"""
Monitor ElevenLabs character quota and alert when low.
Usage: python3 check_elevenlabs_quota.py --threshold 5000
"""

import argparse, subprocess, json, sys, os

def check_quota(threshold=None):
    """Check current ElevenLabs character quota."""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY not set")
        return None

    result = subprocess.run([
        'curl', '-s', '-H', f'xi-api-key: {api_key}',
        'https://api.elevenlabs.io/v1/user'
    ], capture_output=True, text=True, timeout=10)

    if result.returncode != 0:
        print(f"API error: {result.stderr[:200]}")
        return None

    try:
        data = json.loads(result.stdout)
        sub = data.get('subscription', {})
        used = sub.get('character_count', 0)
        limit = sub.get('character_limit', 0)
        plan = sub.get('plan', 'unknown')
        status = sub.get('status', 'unknown')

        remaining = limit - used if limit else 0
        pct_used = (used / limit * 100) if limit else 0

        print(f"\n{'='*50}")
        print(f"ElevenLabs Quota Status")
        print(f"{'='*50}")
        print(f"Plan: {plan} ({status})")
        print(f"Used: {used:,} / {limit:,} characters ({pct_used:.1f}%)")
        print(f"Remaining: {remaining:,} characters")

        if threshold and remaining <= threshold:
            print(f"\n⚠️  ALERT: Only {remaining:,} characters left (threshold: {threshold:,})")
            return "LOW"
        elif threshold and remaining <= threshold * 2:
            print(f"\n⚡ WARNING: {remaining:,} remaining — {threshold*2:,}–{threshold} caution zone")
            return "CAUTION"
        else:
            print(f"\n✅ HEALTHY — {remaining:,} characters available")
            return "OK"

    except json.JSONDecodeError:
        print(f"Failed to parse response: {result.stdout[:200]}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check ElevenLabs character quota")
    parser.add_argument("--threshold", type=int, default=5000,
                       help="Alert threshold (default: 5000)")
    args = parser.parse_args()

    status = check_quota(args.threshold)
    sys.exit(0 if status in ['OK', 'CAUTION'] else 1)
