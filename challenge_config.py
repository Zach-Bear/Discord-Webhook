from dataclasses import dataclass

@dataclass(frozen=True)
class ChallengeSettings:
    time_limit: int = 90
    forbid_moving: bool = False
    forbid_zooming: bool = False
    forbid_rotating: bool = False
