import os
from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime, timezone


@dataclass(frozen=True)
class ChallengeSettings:
    time_limit: int = 90
    forbid_moving: bool = False
    forbid_zooming: bool = False
    forbid_rotating: bool = False
    map_ids: tuple[str, ...] = ()


def load_map_ids(environ: Mapping[str, str] | None = None) -> tuple[str, ...]:
    environment = os.environ if environ is None else environ
    value = environment.get("MAP_IDS")
    if value is None or not value.strip():
        return ()

    return tuple(
        map_id
        for entry in value.split(",")
        if (map_id := entry.strip())
    )


def utc_day_number(utc_date: date | datetime | None = None) -> int:
    if utc_date is None:
        utc_date = datetime.now(timezone.utc).date()
    elif isinstance(utc_date, datetime):
        if utc_date.tzinfo is None:
            utc_date = utc_date.replace(tzinfo=timezone.utc)
        utc_date = utc_date.astimezone(timezone.utc).date()
    elif not isinstance(utc_date, date):
        raise TypeError("UTC date must be a date or datetime")

    return utc_date.toordinal()


def select_map_by_utc_date(
    map_ids: Sequence[str],
    utc_date: date | datetime | None = None,
) -> str:
    if not map_ids:
        raise ValueError("MAP_IDS must contain at least one map ID")

    valid_map_ids = tuple(
        map_id.strip()
        for map_id in map_ids
        if isinstance(map_id, str) and map_id.strip()
    )
    if not valid_map_ids:
        raise ValueError("MAP_IDS must contain at least one map ID")

    index = utc_day_number(utc_date) % len(valid_map_ids)
    return valid_map_ids[index]


def select_map(
    map_ids: Sequence[str],
    utc_date: date | datetime | None = None,
) -> str:
    return select_map_by_utc_date(map_ids, utc_date)


get_utc_day_number = utc_day_number
select_rotated_map = select_map_by_utc_date


def resolve_map_id(
    manual_map_id: str | None,
    map_ids: Sequence[str],
    utc_date: date | datetime | None = None,
) -> str:
    if manual_map_id is not None and manual_map_id.strip():
        return manual_map_id.strip()
    return select_map_by_utc_date(map_ids, utc_date)


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
        map_ids=load_map_ids(environment),
    )
