# tests/test_client.py
import pytest
from unittest.mock import patch, MagicMock


def test_get_client_returns_genai_client():
    """Client should be created with API key from environment."""
    with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
        with patch("google.genai.Client") as mock_client:
            mock_client.return_value = MagicMock()
            from core.client import get_client

            client = get_client()

            mock_client.assert_called_once_with(api_key="test-key")
            assert client is not None


def test_get_client_raises_without_api_key():
    """Client should raise ValueError when API key is missing."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
            from importlib import reload
            import core.client
            reload(core.client)
            core.client.get_client()
