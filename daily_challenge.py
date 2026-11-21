import os
import requests

NCFA_TOKEN = os.environ["NCFA_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
# MAP_ID = os.environ["MAP_ID"]

MAP_ID = "62a44b22040f04bd36e8a914"
geo_url = "https://geoguessr.com"
headers = {
    "Cookie": f"_ncfa={NCFA_COOKIE}",
    "Content-Type": "application/json",
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

# res = session.post("https://geoguessr.com", json=payload)
# res.raise_for_status()

if not response.ok or not response.text:
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    response.raise_for_status()

challenge_token = response.json()["token"]
challenge_url = f"https://geoguessr.com{challenge_token}"

discord_data = {
    "content": f"Play today's geoguessr challenge here: {challenge_url}"
}

requests.pot(WEBHOOK_URL, json=discord_data).raise_for_status()