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

    mock_client.file_search_stores.create.assert_called_once_with(config={"display_name": "biochemistry-notes"})
    assert store.name == "stores/test-store-123"


def test_rag_manager_requires_client():
    """RAGManager should require a client instance."""
    from core.rag_manager import RAGManager

    with pytest.raises(TypeError):
        RAGManager()  # Missing required client argument


def test_upload_file_to_store():
    """Should upload a file to the store and wait for completion."""
    mock_client = MagicMock()
    mock_store = MagicMock()
    mock_store.name = "stores/test-store-123"
    mock_client.file_search_stores.create.return_value = mock_store

    # Mock the upload operation
    mock_operation = MagicMock()
    mock_operation.done = True
    mock_client.file_search_stores.upload_to_file_search_store.return_value = mock_operation

    from core.rag_manager import RAGManager

    manager = RAGManager(client=mock_client)
    manager.create_store("test-store")

    result = manager.upload_file(file_path="/path/to/textbook.pdf", display_name="Lehninger Ch1")

    mock_client.file_search_stores.upload_to_file_search_store.assert_called_once()
    assert result is True


def test_upload_file_raises_without_store():
    """Should raise error if no store has been created."""
    mock_client = MagicMock()

    from core.rag_manager import RAGManager

    manager = RAGManager(client=mock_client)

    with pytest.raises(ValueError, match="store must be created"):
        manager.upload_file(file_path="/path/to/file.pdf", display_name="test")
