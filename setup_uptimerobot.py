"""
Automated UptimeRobot monitor setup script for Veritas AI.
URL monitored: https://veritas-ai-3e4e.onrender.com/api/health
Interval: 5 minutes (prevents Render free tier spin-down)
"""

import sys
import requests

MONITOR_URL = "https://veritas-ai-3e4e.onrender.com/api/health"
FRIENDLY_NAME = "Veritas AI (Render)"

def setup_monitor(api_key: str):
    if not api_key:
        print("Error: No UptimeRobot API key provided.")
        return False

    url = "https://api.uptimerobot.com/v2/newMonitor"
    payload = {
        "api_key": api_key.strip(),
        "format": "json",
        "type": "1",  # HTTP(s)
        "url": MONITOR_URL,
        "friendly_name": FRIENDLY_NAME,
        "interval": "300"  # 5 minutes (in seconds)
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "cache-control": "no-cache"
    }

    try:
        response = requests.post(url, data=payload, headers=headers)
        data = response.json()
        if data.get("stat") == "ok":
            print(f"SUCCESS: Monitor created for {FRIENDLY_NAME}!")
            print(f"Monitor ID: {data.get('monitor', {}).get('id')}")
            print(f"Target URL: {MONITOR_URL}")
            print("Render will now stay awake 24/7 without ever spinning down!")
            return True
        else:
            print(f"UptimeRobot Error: {data.get('error', {}).get('message')}")
            return False
    except Exception as e:
        print(f"Request failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        key = sys.argv[1]
    else:
        key = input("Enter your UptimeRobot API Key (uXXXXX-XXXXX...): ").strip()
    setup_monitor(key)
