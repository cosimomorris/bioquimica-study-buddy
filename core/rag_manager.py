# core/rag_manager.py
"""RAG Manager for Gemini File Search stores."""
import json
import os
import time
from pathlib import Path
from typing import Any, Optional

from google import genai
from google.genai import types

# Default path for storing RAG configuration
DEFAULT_CONFIG_PATH = Path(".streamlit/rag_store.json")


class RAGManager:
    """
    Manages Gemini File Search stores for document-based RAG.

    Handles creation of file search stores, file uploads, and
    provides the tool configuration for generate_content calls.
    Supports persistence across sessions.
    """

    def __init__(self, client: genai.Client, config_path: Optional[Path] = None):
        """
        Initialize RAG Manager with a Gemini client.

        Args:
            client: Configured Gemini client instance.
            config_path: Path to store configuration file (default: .streamlit/rag_store.json)
        """
        self.client = client
        self.store = None
        self.store_name: Optional[str] = None
        self.config_path = config_path or DEFAULT_CONFIG_PATH

    def load_existing_store(self) -> bool:
        """
        Load an existing store from saved configuration.

        Returns:
            True if store was loaded successfully, False otherwise.
        """
        if not self.config_path.exists():
            return False

        try:
            with open(self.config_path) as f:
                config = json.load(f)

            store_name = config.get("store_name")
            if not store_name:
                return False

            # Verify the store still exists on Gemini
            self.store = self.client.file_search_stores.get(name=store_name)
            self.store_name = store_name
            return True
        except Exception:
            # Store doesn't exist anymore or config is invalid
            return False

    def _save_config(self):
        """Save store configuration to disk."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump({"store_name": self.store_name}, f)

    def create_store(self, display_name: str) -> Any:
        """
        Create a new file search store and save configuration.

        Args:
            display_name: Human-readable name for the store.

        Returns:
            The created file search store object.
        """
        self.store = self.client.file_search_stores.create(
            config={"display_name": display_name}
        )
        self.store_name = self.store.name
        self._save_config()
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

    def get_file_search_tool(self) -> types.Tool:
        """
        Get the File Search tool configuration for generate_content.

        Returns:
            types.Tool configured with the current file search store.

        Raises:
            ValueError: If no store has been created yet.
        """
        if self.store is None:
            raise ValueError("A file search store must be created first")

        return types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[self.store.name]
            )
        )

    def get_document_count(self) -> int:
        """
        Get the number of documents in the current store.

        Returns:
            Number of documents, or 0 if no store is loaded.
        """
        if self.store is None or self.store_name is None:
            return 0

        try:
            # List files in the store to count them
            files = list(self.client.file_search_stores.files.list(
                file_search_store_name=self.store_name
            ))
            return len(files)
        except Exception:
            return 0
