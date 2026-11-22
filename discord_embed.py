from datetime import datetime, timezone


GEO_ORIGIN = "https://www.geoguessr.com"


def format_time_limit(seconds: int) -> str:
    if seconds <= 0:
        return "Unlimited"

    minutes, remaining_seconds = divmod(seconds, 60)
    return f"{minutes}:{remaining_seconds:02d}"


def format_rule(forbidden: bool) -> str:
    return "❌ Off" if forbidden else "✅ On"


def build_embed(challenge_link: str, map_id: str, payload: dict) -> dict:
    return {
        "content": "<@&1260915656035930113>", # @& for role, @ for user, # for channel
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
                        "value": f"[View map]({GEO_ORIGIN}/maps/{map_id})",
                        "inline": True,
                    },
                ],
                "footer": {"text": "Good luck!"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ],
    }
