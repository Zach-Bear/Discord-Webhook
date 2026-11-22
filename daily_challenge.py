import os
import requests

from challenge_config import (
    ChallengeSettings,
    load_challenge_settings,
    resolve_map_id,
    select_map,
    select_map_by_utc_date,
    utc_day_number,
)
from discord_embed import build_embed
from geoguessr_api import create_challenge, get_map_name


def require_environment(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def create_challenge_payload(
    map_id: str,
    settings: ChallengeSettings,
) -> dict:
    return {
        "map": map_id,
        "forbidMoving": settings.forbid_moving,
        "forbidZooming": settings.forbid_zooming,
        "forbidRotating": settings.forbid_rotating,
        "timeLimit": settings.time_limit,
    }


def send_discord_message(webhook_url: str, message: dict) -> None:
    requests.post(webhook_url, json=message, timeout=30).raise_for_status()


def run_daily_challenge(
    ncfa_token: str,
    webhook_url: str,
    map_id: str,
    settings: ChallengeSettings,
    role_id: str | None = None,
) -> None:
    payload = create_challenge_payload(map_id, settings)
    map_name = get_map_name(map_id, ncfa_token)
    challenge_link = create_challenge(payload, ncfa_token)
    discord_message = build_embed(
        challenge_link, map_id, map_name, payload, role_id
    )
    send_discord_message(webhook_url, discord_message)


def main() -> None:
    challenge_settings = load_challenge_settings()
    ncfa_token = require_environment("NCFA_TOKEN")
    webhook_url = require_environment("WEBHOOK_URL")
    manual_map_id = os.environ.get("MAP_ID")

    try:
        map_id = resolve_map_id(
            manual_map_id,
            challenge_settings.map_ids,
        )
    except ValueError as error:
        raise RuntimeError(
            "Missing required environment variable: MAP_ID or MAP_IDS"
        ) from error

    run_daily_challenge(
        ncfa_token,
        webhook_url,
        map_id,
        challenge_settings,
        role_id=os.environ.get("ROLE_ID"),
    )


if __name__ == "__main__":
    main()
