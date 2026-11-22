import os
import unittest
from unittest.mock import patch

from challenge_config import ChallengeSettings
import daily_challenge


class DailyChallengeTests(unittest.TestCase):
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
