# core/client.py
"""Gemini client initialization."""
import os
from google import genai


def get_client() -> genai.Client:
    """
    Create and return a configured Gemini client.

    Returns:
        genai.Client: Configured Gemini client instance.

    Raises:
        ValueError: If GOOGLE_API_KEY environment variable is not set.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")

    return genai.Client(api_key=api_key)
