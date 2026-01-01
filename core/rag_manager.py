# core/rag_manager.py
"""RAG Manager for Gemini File Search stores."""
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
