# tests/test_rag_manager.py
import pytest
from unittest.mock import MagicMock, patch


def test_create_file_search_store():
    """Should create a file search store with given name."""
    mock_client = MagicMock()
    mock_store = MagicMock()
    mock_store.name = "stores/test-store-123"
    mock_client.file_search_stores.create.return_value = mock_store

    from core.rag_manager import RAGManager

    manager = RAGManager(client=mock_client)
    store = manager.create_store(display_name="biochemistry-notes")

    mock_client.file_search_stores.create.assert_called_once()
    assert store.name == "stores/test-store-123"


def test_rag_manager_requires_client():
    """RAGManager should require a client instance."""
    from core.rag_manager import RAGManager

    with pytest.raises(TypeError):
        RAGManager()  # Missing required client argument
