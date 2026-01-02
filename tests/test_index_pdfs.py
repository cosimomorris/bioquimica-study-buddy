"""Tests for the PDF indexing script."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from index_pdfs import find_pdfs, load_api_key, PROJECT_ROOT


class TestFindPdfs:
    """Tests for find_pdfs function."""

    def test_finds_pdfs_in_project_root(self):
        """Should find PDF files in project root."""
        pdfs = find_pdfs()
        # We know there are PDFs in the project root
        assert len(pdfs) > 0
        assert all(p.suffix.lower() == ".pdf" for p in pdfs)

    def test_returns_sorted_list(self):
        """Should return PDFs sorted by name (case-insensitive)."""
        pdfs = find_pdfs()
        names = [p.name.lower() for p in pdfs]
        assert names == sorted(names)

    def test_returns_path_objects(self):
        """Should return Path objects."""
        pdfs = find_pdfs()
        assert all(isinstance(p, Path) for p in pdfs)


class TestLoadApiKey:
    """Tests for load_api_key function."""

    def test_raises_if_secrets_not_found(self, tmp_path):
        """Should raise FileNotFoundError if secrets.toml doesn't exist."""
        with patch("index_pdfs.PROJECT_ROOT", tmp_path):
            with pytest.raises(FileNotFoundError):
                load_api_key()

    def test_raises_if_api_key_is_placeholder(self, tmp_path):
        """Should raise KeyError if API key is the example placeholder."""
        secrets_dir = tmp_path / ".streamlit"
        secrets_dir.mkdir()
        secrets_file = secrets_dir / "secrets.toml"
        secrets_file.write_text('GOOGLE_API_KEY = "tu_api_key_de_gemini_aqui"')

        with patch("index_pdfs.PROJECT_ROOT", tmp_path):
            with pytest.raises(KeyError):
                load_api_key()

    def test_returns_api_key_when_configured(self, tmp_path):
        """Should return API key when properly configured."""
        secrets_dir = tmp_path / ".streamlit"
        secrets_dir.mkdir()
        secrets_file = secrets_dir / "secrets.toml"
        secrets_file.write_text('GOOGLE_API_KEY = "test-api-key-123"')

        with patch("index_pdfs.PROJECT_ROOT", tmp_path):
            api_key = load_api_key()
            assert api_key == "test-api-key-123"
