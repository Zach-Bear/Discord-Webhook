import os
import requests

NCFA_TOKEN = os.environ["NCFA_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
MAP_ID = os.environ["MAP_ID"]

session = requests.session()
session.cookies.set("__ncfa", NCFA_TOKEN, domain=".geoguessr.com")

# Customise rules 
payload = {
    "map": MAP_ID,
    "forbidMoving": False,
    "forbidZooming": False,
    "forbidRotating": False,
    "timeLimit": 120
}

res = session.post("https://geoguessr.com", json=payload)
res.raise_for_status()

challenge_token = res.json()["token"]
challenge_url = f"https://geoguessr.com{challenge_token}"

discord_data = {
    "content": f"Play today's geoguessr challenge here: {challenge_url}"
}

requests.pot(WEBHOOK_URL, json=discord_data).raise_for_status()