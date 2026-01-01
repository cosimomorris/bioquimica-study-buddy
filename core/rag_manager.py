# core/rag_manager.py
"""RAG Manager for Gemini File Search stores."""
import time

from google import genai
from google.genai import types


class RAGManager:
    """
    Manages Gemini File Search stores for document-based RAG.

    Handles creation of file search stores, file uploads, and
    provides the tool configuration for generate_content calls.
    """

    def __init__(self, client: genai.Client):
        """
        Initialize RAG Manager with a Gemini client.

        Args:
            client: Configured Gemini client instance.
        """
        self.client = client
        self.store = None

    def create_store(self, display_name: str) -> types.FileSearchStore:
        """
        Create a new file search store.

        Args:
            display_name: Human-readable name for the store.

        Returns:
            The created file search store object.
        """
        self.store = self.client.file_search_stores.create(
            config={"display_name": display_name}
        )
        return self.store

    def upload_file(self, file_path: str, display_name: str, timeout: int = 300) -> bool:
        """
        Upload a file to the current file search store.

        Args:
            file_path: Path to the file to upload (PDF, TXT, MD, etc.).
            display_name: Human-readable name for the file in the store.
            timeout: Maximum seconds to wait for upload completion.

        Returns:
            True if upload completed successfully.

        Raises:
            ValueError: If no store has been created yet.
            TimeoutError: If upload does not complete within timeout.
        """
        if self.store is None:
            raise ValueError("A file search store must be created first")

        operation = self.client.file_search_stores.upload_to_file_search_store(
            file=file_path,
            file_search_store_name=self.store.name,
            config={"display_name": display_name}
        )

        elapsed = 0
        while not operation.done and elapsed < timeout:
            time.sleep(5)
            elapsed += 5
            operation = self.client.operations.get(operation)

        if not operation.done:
            raise TimeoutError(f"File upload did not complete within {timeout} seconds")

        return True
