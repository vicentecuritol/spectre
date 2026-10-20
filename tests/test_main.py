import unittest
from unittest.mock import MagicMock
from openai import APIConnectionError, NotFoundError, AuthenticationError, RateLimitError
from main import format_api_error


class TestMain(unittest.TestCase):

    def _make_mock_response(self, status_code: int):
        resp = MagicMock()
        resp.status_code = status_code
        resp.request = MagicMock()
        return resp

    def test_format_api_error_connection(self):
        err = APIConnectionError(request=MagicMock())
        msg = format_api_error(err, "http://localhost:11434/v1", "llama3")
        self.assertIn("Error de conexión", msg)
        self.assertIn("ollama serve", msg)

    def test_format_api_error_not_found(self):
        resp = self._make_mock_response(404)
        err = NotFoundError(message="model not found", response=resp, body=None)
        msg = format_api_error(err, "http://localhost:11434/v1", "llama3")
        self.assertIn("Modelo 'llama3' no encontrado", msg)
        self.assertIn(":models", msg)

    def test_format_api_error_auth(self):
        resp = self._make_mock_response(401)
        err = AuthenticationError(message="invalid key", response=resp, body=None)
        msg = format_api_error(err, "https://api.openai.com/v1", "gpt-4")
        self.assertIn("Error de autenticación (401)", msg)
        self.assertIn("OPENAI_API_KEY", msg)

    def test_format_api_error_rate_limit(self):
        resp = self._make_mock_response(429)
        err = RateLimitError(message="quota exceeded", response=resp, body=None)
        msg = format_api_error(err, "https://api.openai.com/v1", "gpt-4")
        self.assertIn("Límite de tasa (429)", msg)

    def test_format_api_error_generic(self):
        err = ValueError("Error arbitrario")
        msg = format_api_error(err, "http://localhost:11434/v1", "llama3")
        self.assertIn("Error inesperado: Error arbitrario", msg)


if __name__ == "__main__":
    unittest.main()
