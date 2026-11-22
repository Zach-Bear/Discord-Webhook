import os
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ChallengeSettings:
    time_limit: int = 90
    forbid_moving: bool = False
    forbid_zooming: bool = False
    forbid_rotating: bool = False


def load_challenge_settings(
    environ: Mapping[str, str] | None = None,
) -> ChallengeSettings:
    environment = os.environ if environ is None else environ
    defaults = ChallengeSettings()

    time_limit_value = environment.get("TIME_LIMIT")
    if time_limit_value is None or not time_limit_value.strip():
        time_limit = defaults.time_limit
    else:
        try:
            time_limit = int(time_limit_value)
        except ValueError as error:
            raise ValueError("TIME_LIMIT must be a non-negative integer") from error
        if time_limit < 0:
            raise ValueError("TIME_LIMIT must be a non-negative integer")

    def parse_boolean(name: str, default: bool) -> bool:
        value = environment.get(name)
        if value is None or not value.strip():
            return default
        if value.strip().lower() == "true":
            return True
        if value.strip().lower() == "false":
            return False
        raise ValueError(f"{name} must be 'true' or 'false'")

    return ChallengeSettings(
        time_limit=time_limit,
        forbid_moving=parse_boolean("FORBID_MOVING", defaults.forbid_moving),
        forbid_zooming=parse_boolean("FORBID_ZOOMING", defaults.forbid_zooming),
        forbid_rotating=parse_boolean("FORBID_ROTATING", defaults.forbid_rotating),
    )
