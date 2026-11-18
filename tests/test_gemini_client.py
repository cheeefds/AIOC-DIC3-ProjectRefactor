"""Unit tests for Google AI Studio GeminiClient and .env loading."""
import os
import tempfile
import unittest

from src.agent.gemini_client import GeminiClient, load_dotenv

class TestGeminiClient(unittest.TestCase):

    def test_load_dotenv_custom(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tmp:
            tmp.write("# Test comment\n")
            tmp.write("TEST_ENV_KEY_AQI=my_secret_token_123\n")
            tmp.write("TEST_MODEL_NAME=gemini-2.5-flash-lite\n")
            tmp_path = tmp.name

        try:
            load_dotenv(tmp_path)
            self.assertEqual(os.environ.get("TEST_ENV_KEY_AQI"), "my_secret_token_123")
            self.assertEqual(os.environ.get("TEST_MODEL_NAME"), "gemini-2.5-flash-lite")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_gemini_client_availability(self):
        # Without key
        client_empty = GeminiClient(api_key="")
        self.assertFalse(client_empty.is_available())
        self.assertIsNone(client_empty.generate("Test prompt"))

        # With mock key
        client_mock = GeminiClient(api_key="AIzaSyDummyKeyForTestingOnly", model="gemini-2.5-flash-lite")
        self.assertTrue(client_mock.is_available())
        self.assertEqual(client_mock.model, "gemini-2.5-flash-lite")

if __name__ == "__main__":
    unittest.main()
