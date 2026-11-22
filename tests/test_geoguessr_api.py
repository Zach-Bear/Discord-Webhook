import unittest
from unittest.mock import patch

import geoguessr_api


class GeoGuessrApiTests(unittest.TestCase):
    @patch("geoguessr_api.requests.get")
    def test_get_map_name_returns_name_and_sends_authentication(self, get):
        response = get.return_value
        response.json.return_value = {"name": "World map"}

        map_name = geoguessr_api.get_map_name("map-123", "token")

        self.assertEqual(map_name, "World map")
        get.assert_called_once_with(
            f"{geoguessr_api.MAP_API_URL}/map-123",
            headers={"Cookie": "_ncfa=token"},
            timeout=geoguessr_api.REQUEST_TIMEOUT,
        )
        response.raise_for_status.assert_called_once_with()

    @patch("geoguessr_api.requests.get")
    def test_get_map_name_rejects_missing_name(self, get):
        get.return_value.json.return_value = {}

        with self.assertRaisesRegex(RuntimeError, "did not contain a map name"):
            geoguessr_api.get_map_name("map-123", "token")

    @patch("geoguessr_api.requests.get")
    def test_get_map_name_rejects_blank_name(self, get):
        get.return_value.json.return_value = {"name": "  "}

        with self.assertRaisesRegex(RuntimeError, "valid map name"):
            geoguessr_api.get_map_name("map-123", "token")

    @patch("geoguessr_api.requests.post")
    def test_create_challenge_returns_url_and_sends_payload(self, post):
        response = post.return_value
        response.ok = True
        response.headers = {"Content-Type": "application/json"}
        response.json.return_value = {"token": "challenge-token"}
        payload = {"map": "map-123"}

        challenge_url = geoguessr_api.create_challenge(payload, "token")

        self.assertEqual(
            challenge_url,
            f"{geoguessr_api.GEO_ORIGIN}/challenge/challenge-token",
        )
        post.assert_called_once()
        self.assertEqual(post.call_args.kwargs["json"], payload)
        self.assertEqual(
            post.call_args.kwargs["headers"]["Cookie"], "_ncfa=token"
        )
        response.raise_for_status.assert_not_called()

    @patch("builtins.print")
    @patch("geoguessr_api.requests.post")
    def test_create_challenge_rejects_non_json_response(self, post, _print):
        response = post.return_value
        response.ok = True
        response.headers = {"Content-Type": "text/html"}
        response.status_code = 200
        response.url = "response-url"
        response.text = "not json"

        with self.assertRaisesRegex(RuntimeError, "did not return JSON"):
            geoguessr_api.create_challenge({"map": "map-123"}, "token")

        response.raise_for_status.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
