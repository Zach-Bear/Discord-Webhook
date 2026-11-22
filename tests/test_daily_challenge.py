import unittest
from unittest.mock import patch

import daily_challenge


class DailyChallengeTests(unittest.TestCase):
    def test_create_challenge_payload_uses_map_and_current_rules(self):
        self.assertEqual(
            daily_challenge.create_challenge_payload("map-123"),
            {
                "map": "map-123",
                "forbidMoving": False,
                "forbidZooming": False,
                "forbidRotating": False,
                "timeLimit": 90,
            },
        )

    @patch("daily_challenge.send_discord_message")
    @patch("daily_challenge.build_embed", return_value={"content": "<@&role>"})
    @patch("daily_challenge.create_challenge", return_value="challenge-url")
    @patch("daily_challenge.get_map_name", return_value="Map name")
    def test_run_daily_challenge_passes_data_through_pipeline(
        self,
        get_map_name,
        create_challenge,
        build_embed,
        send_discord_message,
    ):
        daily_challenge.run_daily_challenge(
            "token", "webhook-url", "map-123", "role-456"
        )

        payload = daily_challenge.create_challenge_payload("map-123")
        get_map_name.assert_called_once_with("map-123", "token")
        create_challenge.assert_called_once_with(payload, "token")
        build_embed.assert_called_once_with(
            "challenge-url", "map-123", "Map name", payload, "role-456"
        )
        send_discord_message.assert_called_once_with(
            "webhook-url", {"content": "<@&role>"}
        )

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
