import unittest

from discord_embed import GEO_ORIGIN, build_embed, format_rule, format_time_limit


class DiscordEmbedTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "timeLimit": 90,
            "forbidMoving": False,
            "forbidZooming": True,
            "forbidRotating": False,
        }

    def test_embed_shows_map_name_as_link_and_formats_rules(self):
        result = build_embed(
            "challenge-url", "map-123", "World map", self.payload
        )

        embed = result["embeds"][0]
        fields = {field["name"]: field["value"] for field in embed["fields"]}
        self.assertEqual(
            fields["🗺️ Map"], f"[World map]({GEO_ORIGIN}/maps/map-123)"
        )
        self.assertEqual(fields["⏱️ Time limit"], "1:30")
        self.assertEqual(fields["🚶 Moving"], "✅ On")
        self.assertEqual(fields["🔍 Zooming"], "❌ Off")
        self.assertNotIn("content", result)

    def test_role_mention_is_included_and_allowed_only_for_that_role(self):
        result = build_embed(
            "challenge-url", "map-123", "World map", self.payload, "role-456"
        )

        self.assertEqual(result["content"], "<@&role-456>")
        self.assertEqual(result["allowed_mentions"], {"roles": ["role-456"]})

    def test_empty_role_id_does_not_add_mention(self):
        result = build_embed(
            "challenge-url", "map-123", "World map", self.payload, ""
        )

        self.assertNotIn("content", result)
        self.assertNotIn("allowed_mentions", result)

    def test_format_helpers_handle_unlimited_time_and_rules(self):
        self.assertEqual(format_time_limit(0), "Unlimited")
        self.assertEqual(format_rule(True), "❌ Off")
        self.assertEqual(format_rule(False), "✅ On")


if __name__ == "__main__":
    unittest.main()
