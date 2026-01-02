#!/usr/bin/env python3
"""
One-time PDF indexing script for BioChem Study Buddy.

Finds all PDFs in the project root, creates a Gemini File Search store,
uploads each PDF, and saves the store configuration.

Usage:
    python scripts/index_pdfs.py
"""
import os
import sys
import unicodedata
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import tomllib

from core.client import get_client
from core.rag_manager import RAGManager


def load_api_key() -> str:
    """
    Load API key from .streamlit/secrets.toml.

    Returns:
        The Google API key string.

    Raises:
        FileNotFoundError: If secrets.toml doesn't exist.
        KeyError: If GOOGLE_API_KEY is not in secrets.toml.
    """
    secrets_path = PROJECT_ROOT / ".streamlit" / "secrets.toml"

    if not secrets_path.exists():
        raise FileNotFoundError(
            f"Secrets file not found: {secrets_path}\n"
            "Copy .streamlit/secrets.toml.example to .streamlit/secrets.toml "
            "and add your API key."
        )

    with open(secrets_path, "rb") as f:
        secrets = tomllib.load(f)

    api_key = secrets.get("GOOGLE_API_KEY")
    if not api_key or api_key == "tu_api_key_de_gemini_aqui":
        raise KeyError(
            "GOOGLE_API_KEY not configured in .streamlit/secrets.toml"
        )

    return api_key


def find_pdfs() -> list[Path]:
    """
    Find all PDF files in the project root directory.

    Returns:
        List of Path objects for each PDF found.
    """
    pdfs = list(PROJECT_ROOT.glob("*.pdf"))
    return sorted(pdfs, key=lambda p: p.name.lower())


def normalize_filename(name: str) -> str:
    """
    Normalize filename to ASCII-safe characters.

    Removes accents and special Unicode characters that may cause
    encoding issues with the Gemini API.

    Args:
        name: Original filename with possible accents.

    Returns:
        ASCII-safe version of the filename.
    """
    # Normalize to decomposed form (separate base char and accents)
    normalized = unicodedata.normalize('NFD', name)
    # Remove accent marks (combining characters)
    ascii_safe = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    return ascii_safe


def main():
    """Main indexing function."""
    # Find PDFs
    pdfs = find_pdfs()

    if not pdfs:
        print("No se encontraron archivos PDF en el directorio raiz.")
        sys.exit(1)

    print(f"🔍 Encontrados {len(pdfs)} PDFs")

    # Load API key and set environment variable
    try:
        api_key = load_api_key()
        os.environ["GOOGLE_API_KEY"] = api_key
    except (FileNotFoundError, KeyError) as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    # Initialize client and RAG manager
    client = get_client()
    rag_manager = RAGManager(client)

    # Create store
    print("📦 Creando store en Gemini...")
    store_name = "BioChem Study Buddy - Textbooks"
    rag_manager.create_store(display_name=store_name)
    print(f"   Store creado: {rag_manager.store_name}")

    # Upload each PDF
    success_count = 0
    error_count = 0

    for pdf_path in pdfs:
        display_name = normalize_filename(pdf_path.name)
        print(f"📤 Subiendo {pdf_path.name}...", end=" ", flush=True)

        try:
            rag_manager.upload_file(
                file_path=str(pdf_path),
                display_name=display_name,
                timeout=900  # 15 minutes per file for large PDFs
            )
            print("✓")
            success_count += 1
        except TimeoutError as e:
            print(f"⏱️ Timeout: {e}")
            error_count += 1
        except Exception as e:
            print(f"✗ Error: {e}")
            error_count += 1

    # Summary
    config_path = PROJECT_ROOT / ".streamlit" / "rag_store.json"
    print()
    if error_count == 0:
        print(f"✅ Indexacion completa. Store guardado en {config_path.relative_to(PROJECT_ROOT)}")
    else:
        print(f"⚠️ Indexacion completada con {error_count} errores.")
        print(f"   {success_count}/{len(pdfs)} archivos subidos exitosamente.")
        print(f"   Store guardado en {config_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
