import requests


GEO_ORIGIN = "https://www.geoguessr.com"
MAP_API_URL = f"{GEO_ORIGIN}/api/maps"
CHALLENGE_API_URL = f"{GEO_ORIGIN}/api/v3/challenges"
REQUEST_TIMEOUT = 30


def get_map_name(map_id: str, ncfa_token: str) -> str:
    response = requests.get(
        f"{MAP_API_URL}/{map_id}",
        headers={"Cookie": f"_ncfa={ncfa_token}"},
        timeout=REQUEST_TIMEOUT,
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
        CHALLENGE_API_URL,
        json=payload,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
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
    except (requests.exceptions.JSONDecodeError, KeyError, TypeError) as error:
        raise RuntimeError("GeoGuessr response did not contain a challenge token") from error

    return f"{GEO_ORIGIN}/challenge/{challenge_token}"
