import os
from datetime import datetime, timezone
from typing import NoReturn
from discord_embed import GEO_ORIGIN, build_embed

import requests

GEO_URL = "https://www.geoguessr.com/api/v3/challenges"
MAP_URL = f"{GEO_ORIGIN}/api/maps"

NCFA_TOKEN = os.environ["NCFA_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
MAP_ID = os.environ["MAP_ID"]


def require_environment(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def format_time_limit(seconds: int) -> str:
    if seconds <= 0:
        return "Unlimited"

    minutes, remaining_seconds = divmod(seconds, 60)
    return f"{minutes}:{remaining_seconds:02d}"


def format_rule(forbidden: bool) -> str:
    return "❌ Off" if forbidden else "✅ On"


def get_map_name(map_id: str, ncfa_token: str) -> str:
    response = requests.get(
        f"{MAP_URL}/{map_id}",
        headers={"Cookie": f"_ncfa={ncfa_token}"},
        timeout=30,
    )
    response.raise_for_status()

    try:
        map_name = response.json()["name"]
    except (requests.exceptions.JSONDecodeError, KeyError, TypeError) as error:
        raise RuntimeError("GeoGuessr map response did not contain a map name") from error

    if not isinstance(map_name, str) or not map_name.strip():
        raise RuntimeError("GeoGuessr map response did not contain a valid map name")

    return map_name


def create_challenge(payload: dict, ncfa_token: str) -> str:
    headers = {
        "Cookie": f"_ncfa={ncfa_token}",
        "Content-Type": "application/json",
        "Origin": GEO_ORIGIN,
        "Referer": f"{GEO_ORIGIN}/maps/{payload['map']}",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
    }

    response = requests.post(
        GEO_URL,
        json=payload,
        headers=headers,
        timeout=30,
    )

    content_type = response.headers.get("Content-Type", "")
    if not response.ok or "application/json" not in content_type:
        print("STATUS:", response.status_code)
        print("FINAL URL:", response.url)
        print("BODY:", response.text[:500])
        response.raise_for_status()

        raise RuntimeError(
            "GeoGuessr did not return JSON - check that NCFA_TOKEN is still valid"
        )

    try:
        challenge_token = response.json()["token"]
    except (requests.exceptions.JSONDecodeError, KeyError) as error:
        raise RuntimeError("GeoGuessr response did not contain a challenge token") from error

    return f"{GEO_ORIGIN}/challenge/{challenge_token}"

def main() -> None:
    ncfa_token = require_environment("NCFA_TOKEN")
    webhook_url = require_environment("WEBHOOK_URL")
    map_id = require_environment("MAP_ID")

    payload = {
        "map": map_id,
        "forbidMoving": False,
        "forbidZooming": False,
        "forbidRotating": False,
        "timeLimit": 90,
    }

    map_name = get_map_name(map_id, ncfa_token)
    challenge_link = create_challenge(payload, ncfa_token)
    discord_data = build_embed(challenge_link, map_id, map_name, payload)

    requests.post(webhook_url, json=discord_data, timeout=30).raise_for_status()


if __name__ == "__main__":
    main()
