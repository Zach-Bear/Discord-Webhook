from datetime import datetime, timezone
from typing import Optional

from geoguessr_api import GEO_ORIGIN


def format_time_limit(seconds: int) -> str:
    if seconds <= 0:
        return "Unlimited"

    minutes, remaining_seconds = divmod(seconds, 60)
    return f"{minutes}:{remaining_seconds:02d}"


def format_rule(forbidden: bool) -> str:
    return "❌ Off" if forbidden else "✅ On"


def build_embed(
    challenge_link: str,
    map_id: str,
    map_name: str,
    payload: dict,
    role_id: Optional[str] = None,
) -> dict:
    embed = {
        "username": "GeoGuessr Daily",
        "embeds": [
            {
                "title": "🌍 Today's GeoGuessr Challenge",
                "url": challenge_link,
                "description": (
                    "A new daily challenge is ready!\n"
                    f"**[▶ Play now]({challenge_link})**"
                ),
                "color": 0x360666,
                "fields": [
                    {
                        "name": "⏱️ Time limit",
                        "value": format_time_limit(payload["timeLimit"]),
                        "inline": True,
                    },
                    {
                        "name": "🚶 Moving",
                        "value": format_rule(payload["forbidMoving"]),
                        "inline": True,
                    },
                    {
                        "name": "🔍 Zooming",
                        "value": format_rule(payload["forbidZooming"]),
                        "inline": True,
                    },
                    {
                        "name": "🔄 Panning",
                        "value": format_rule(payload["forbidRotating"]),
                        "inline": True,
                    },
                    {
                        "name": "🗺️ Map",
                        "value": f"[{map_name}]({GEO_ORIGIN}/maps/{map_id})",
                        "inline": True,
                    },
                ],
                "footer": {"text": "Good luck!"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ],
    }

    if role_id:
        embed["content"] = f"<@&{role_id}>"
        embed["allowed_mentions"] = {"roles": [role_id]}

    return embed