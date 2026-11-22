import os
import unittest
from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch

from challenge_config import ChallengeSettings
import daily_challenge


class DailyChallengeTests(unittest.TestCase):
    def test_select_map_by_utc_date_is_deterministic_and_preserves_order(self):
        map_ids = ("map-a", "map-b", "map-c")
        utc_date = datetime(
            2026, 11, 22, 23, 59,
            tzinfo=timezone(timedelta(hours=-5)),
        )

        first = daily_challenge.select_map_by_utc_date(map_ids, utc_date)
        second = daily_challenge.select_map_by_utc_date(map_ids, utc_date)

        self.assertEqual(first, second)
        self.assertEqual(map_ids, ("map-a", "map-b", "map-c"))

    def test_known_utc_dates_select_expected_modulo_index(self):
        map_ids = ("map-a", "map-b", "map-c")

        for utc_date in (date(2026, 11, 22), date(2026, 11, 23), date(2026, 11, 24)):
            with self.subTest(utc_date=utc_date):
                expected = map_ids[
                    daily_challenge.utc_day_number(utc_date) % len(map_ids)
                ]
                self.assertEqual(
                    daily_challenge.select_map_by_utc_date(map_ids, utc_date),
                    expected,
                )

    def test_empty_map_rotation_list_has_clear_error(self):
        with self.assertRaisesRegex(
            ValueError, "MAP_IDS must contain at least one map ID"
        ):
            daily_challenge.select_map_by_utc_date(())

    def test_manual_map_id_takes_precedence_over_rotation(self):
        self.assertEqual(
            daily_challenge.resolve_map_id(
                "manual-map",
                ("map-a", "map-b"),
                date(2026, 11, 22),
            ),
            "manual-map",
        )

    def test_invalid_settings_fail_before_external_calls(self):
        environment = {
            "NCFA_TOKEN": "token",
            "WEBHOOK_URL": "webhook-url",
            "MAP_ID": "map-123",
            "TIME_LIMIT": "invalid",
        }

        with patch.dict(os.environ, environment, clear=True):
            with patch("daily_challenge.get_map_name") as get_map_name:
                with patch("daily_challenge.create_challenge") as create_challenge:
                    with patch("daily_challenge.send_discord_message") as send_message:
                        with self.assertRaisesRegex(
                            ValueError, "TIME_LIMIT must be a non-negative integer"
                        ):
                            daily_challenge.main()

        get_map_name.assert_not_called()
        create_challenge.assert_not_called()
        send_message.assert_not_called()

    def test_create_challenge_payload_uses_default_settings(self):
        self.assertEqual(
            daily_challenge.create_challenge_payload(
                "map-123", ChallengeSettings()
            ),
            {
                "map": "map-123",
                "forbidMoving": False,
                "forbidZooming": False,
                "forbidRotating": False,
                "timeLimit": 90,
            },
        )

    @patch("daily_challenge.send_discord_message")
    @patch("daily_challenge.create_challenge", return_value="challenge-url")
    @patch("daily_challenge.get_map_name", return_value="Map name")
    def test_run_daily_challenge_passes_data_through_pipeline(
        self,
        get_map_name,
        create_challenge,
        send_discord_message,
    ):
        settings = ChallengeSettings(
            time_limit=120,
            forbid_moving=True,
            forbid_zooming=False,
            forbid_rotating=True,
        )
        daily_challenge.run_daily_challenge(
            "token", "webhook-url", "map-123", settings, "role-456"
        )

        payload = {
            "map": "map-123",
            "forbidMoving": True,
            "forbidZooming": False,
            "forbidRotating": True,
            "timeLimit": 120,
        }
        get_map_name.assert_called_once_with("map-123", "token")
        create_challenge.assert_called_once_with(payload, "token")
        send_discord_message.assert_called_once()
        webhook_url, message = send_discord_message.call_args.args
        self.assertEqual(webhook_url, "webhook-url")
        self.assertEqual(message["content"], "<@&role-456>")
        fields = {
            field["name"]: field["value"]
            for field in message["embeds"][0]["fields"]
        }
        self.assertEqual(fields["⏱️ Time limit"], "2:00")
        self.assertEqual(fields["🚶 Moving"], "❌ Off")
        self.assertEqual(fields["🔍 Zooming"], "✅ On")
        self.assertEqual(fields["🔄 Panning"], "❌ Off")

    @patch("daily_challenge.requests.post")
    def test_send_discord_message_raises_http_errors(self, post):
        response = post.return_value
        response.raise_for_status.side_effect = RuntimeError("request failed")

        with self.assertRaisesRegex(RuntimeError, "request failed"):
            daily_challenge.send_discord_message("webhook-url", {"content": "test"})

        post.assert_called_once_with(
            "webhook-url", json={"content": "test"}, timeout=30
        )


if __name__ == "__main__":
    unittest.main()
