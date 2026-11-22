import os
import unittest
from dataclasses import fields
from unittest.mock import patch

from challenge_config import ChallengeSettings, load_challenge_settings
from daily_challenge import require_environment


class ChallengeConfigTests(unittest.TestCase):
    def test_loader_reads_optional_settings_from_injected_environment(self):
        environment = {
            "TIME_LIMIT": "120",
            "FORBID_MOVING": "true",
            "FORBID_ZOOMING": "false",
            "FORBID_ROTATING": "true",
        }

        with patch.dict(os.environ, {}, clear=True):
            settings = load_challenge_settings(environment)

        self.assertEqual(
            settings,
            ChallengeSettings(
                time_limit=120,
                forbid_moving=True,
                forbid_zooming=False,
                forbid_rotating=True,
            ),
        )
        self.assertEqual(
            {field.name for field in fields(settings)},
            {
                "time_limit",
                "forbid_moving",
                "forbid_zooming",
                "forbid_rotating",
            },
        )

    def test_required_environment_variables_still_raise_when_missing(self):
        required_variables = ("NCFA_TOKEN", "WEBHOOK_URL", "MAP_ID")

        with patch.dict(os.environ, {}, clear=True):
            for name in required_variables:
                with self.subTest(name=name):
                    with self.assertRaisesRegex(
                        RuntimeError, f"Missing required environment variable: {name}"
                    ):
                        require_environment(name)


if __name__ == "__main__":
    unittest.main()
