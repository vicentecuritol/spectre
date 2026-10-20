import unittest
from unittest.mock import patch, MagicMock
import urllib.error
import ai_engine


class TestAiEngine(unittest.TestCase):

    def test_is_local_endpoint(self):
        # Casos locales
        self.assertTrue(ai_engine._is_local_endpoint("http://localhost:11434/v1"))
        self.assertTrue(ai_engine._is_local_endpoint("http://127.0.0.1:11434/v1"))
        self.assertTrue(ai_engine._is_local_endpoint("http://[::1]:11434/v1"))
        self.assertTrue(ai_engine._is_local_endpoint("http://localhost:8080/v1"))
        self.assertTrue(ai_engine._is_local_endpoint("http://192.168.1.50:11434/v1"))

        # Casos remotos / externos
        self.assertFalse(ai_engine._is_local_endpoint("https://api.openai.com/v1"))
        self.assertFalse(ai_engine._is_local_endpoint("https://api.groq.com/openai/v1"))
        self.assertFalse(ai_engine._is_local_endpoint("https://openrouter.ai/api/v1"))

        # Entrada malformada o inválida
        self.assertFalse(ai_engine._is_local_endpoint(""))
        self.assertFalse(ai_engine._is_local_endpoint("not_a_valid_url:::"))

    def test_set_model(self):
        original_model = ai_engine.MODEL
        try:
            new_model = ai_engine.set_model("  deepseek-coder:6.7b  ")
            self.assertEqual(new_model, "deepseek-coder:6.7b")
            self.assertEqual(ai_engine.MODEL, "deepseek-coder:6.7b")
        finally:
            ai_engine.set_model(original_model)

    def test_get_engine_info(self):
        info = ai_engine.get_engine_info()
        self.assertIsInstance(info, dict)
        self.assertIn("base_url", info)
        self.assertIn("model", info)
        self.assertIn("is_local", info)
        self.assertIsInstance(info["is_local"], bool)

    @patch("ai_engine.urllib.request.urlopen")
    def test_list_available_models_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"models": [{"name": "llama3:latest"}, {"name": "codellama:7b"}]}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Forzar un endpoint local para la prueba
        with patch.object(ai_engine, "BASE_URL", "http://localhost:11434/v1"):
            models = ai_engine.list_available_models()
            self.assertEqual(models, ["llama3:latest", "codellama:7b"])

    @patch("ai_engine.urllib.request.urlopen")
    def test_list_available_models_connection_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        with patch.object(ai_engine, "BASE_URL", "http://localhost:11434/v1"):
            models = ai_engine.list_available_models()
            self.assertEqual(models, [])

    def test_list_available_models_non_local(self):
        with patch.object(ai_engine, "BASE_URL", "https://api.openai.com/v1"):
            models = ai_engine.list_available_models()
            self.assertEqual(models, [])


if __name__ == "__main__":
    unittest.main()
