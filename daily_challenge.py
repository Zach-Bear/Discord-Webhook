import os
from datetime import datetime, timezone

import requests

NCFA_TOKEN = os.environ["NCFA_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
# MAP_ID = os.environ["MAP_ID"]

MAP_ID = "62a44b22040f04bd36e8a914"
geo_url = "https://www.geoguessr.com/api/v3/challenges"
headers = {
    "Cookie": f"_ncfa={NCFA_TOKEN}",
    "Content-Type": "application/json",
    "Origin": "https://www.geoguessr.com",
    "Referer": f"https://www.geoguessr.com/maps/{MAP_ID}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

}


# Customise rules 
payload = {
    "map": MAP_ID,
    "forbidMoving": False,
    "forbidZooming": False,
    "forbidRotating": False,
    "timeLimit": 120
}

response = requests.post(geo_url, json=payload, headers=headers)

if not response.ok or "application/json" not in response.headers.get("Content-Type", ""):
    print("STATUS:", response.status_code)
    print("FINAL URL:", response.url)
    print("BODY:", response.text[:500])
    response.raise_for_status()
    raise SystemExit("GeoGuessr did not return JSON - check that NCFA_TOKEN is still valid")

data = response.json()
challenge_token = data["token"]
challenge_link = f"https://www.geoguessr.com/challenge/{challenge_token}"

def rule(forbidden):
    return "❌ Off" if forbidden else "✅ On"

minutes, seconds = divmod(payload["timeLimit"], 60)
time_limit = f"{minutes}:{seconds:02d}" if payload["timeLimit"] else "Unlimited"

discord_data = {
    "username": "GeoGuessr Daily",
    "embeds": [
        {
            "title": "🌍 Today's GeoGuessr Challenge",
            "url": challenge_link,
            "description": f"A new daily challenge is ready!\n**[▶ Play now]({challenge_link})**",
            "color": 0x7950E5,
            "fields": [
                {"name": "⏱️ Time limit", "value": time_limit, "inline": True},
                {"name": "🚶 Moving", "value": rule(payload["forbidMoving"]), "inline": True},
                {"name": "🔍 Zooming", "value": rule(payload["forbidZooming"]), "inline": True},
                {"name": "🔄 Panning", "value": rule(payload["forbidRotating"]), "inline": True},
                {"name": "🗺️ Map", "value": f"[View map](https://www.geoguessr.com/maps/{MAP_ID})", "inline": True},
            ],
            "footer": {"text": "Good luck! Post your score below 👇"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    ],
}

requests.post(WEBHOOK_URL, json=discord_data).raise_for_status()