import os
import unittest
from dataclasses import fields
from unittest.mock import patch

from challenge_config import ChallengeSettings, load_challenge_settings
from daily_challenge import require_environment


class ChallengeConfigTests(unittest.TestCase):
    def test_omitted_optional_settings_use_defaults(self):
        self.assertEqual(
            load_challenge_settings({}),
            ChallengeSettings(),
        )

    def test_empty_optional_settings_use_defaults(self):
        environment = {
            "TIME_LIMIT": "",
            "FORBID_MOVING": "",
            "FORBID_ZOOMING": "",
            "FORBID_ROTATING": "",
        }

        self.assertEqual(
            load_challenge_settings(environment),
            ChallengeSettings(),
        )

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

    def test_zero_time_limit_is_valid(self):
        settings = load_challenge_settings({"TIME_LIMIT": "0"})

        self.assertEqual(settings.time_limit, 0)

    def test_invalid_time_limits_raise_clear_errors(self):
        for value in ("not-a-number", "-1", "1.5"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    ValueError, "TIME_LIMIT must be a non-negative integer"
                ):
                    load_challenge_settings({"TIME_LIMIT": value})

    def test_invalid_boolean_values_raise_clear_errors(self):
        for name in ("FORBID_MOVING", "FORBID_ZOOMING", "FORBID_ROTATING"):
            with self.subTest(name=name):
                with self.assertRaisesRegex(
                    ValueError, f"{name} must be 'true' or 'false'"
                ):
                    load_challenge_settings({name: "yes"})

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
