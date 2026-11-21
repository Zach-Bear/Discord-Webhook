import os
import requests

NCFA_TOKEN = os.environ["NCFA_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
# MAP_ID = os.environ["MAP_ID"]

MAP_ID = "62a44b22040f04bd36e8a914"
geo_url = "https://geoguessr.com"
headers = {
    "Cookie": f"_ncfa={NCFA_TOKEN}",
    "Content-Type": "application/json",
    "Origin": "https://geoguessr.com",
    "Referer": f"https://geoguessr.com/maps/{MAP_ID}",
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

print("STATUS:", response.status_code)
print("FINAL URL:", response.url)
print("BODY:", response.text[:500])

data = response.json()
challenge_token = data["token"]
challenge_link = f"https://geoguessr.com/challenge/{challenge_token}"

discord_data = {
    "content": f"Play today's geoguessr challenge here: {challenge_link}"
}

requests.pot(WEBHOOK_URL, json=discord_data).raise_for_status()