# Static PDFs Pre-indexing Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace file upload functionality with a one-time script that indexes 10 static PDF files.

**Architecture:** A script runs once to upload all PDFs to Gemini File Search, storing the reference. The app loads this store on startup without any upload UI.

---

## Context

The file upload and indexing feature was not working reliably. Instead, we have 10 static PDF files (biochemistry course units) that should be pre-indexed once.

## PDFs to Index

Located in project root:
1. UNIDAD 1 AGUA Y pH (version ACTUALIZADA).pdf
2. UNIDAD 2 BIOENERGETICA.pdf
3. UNIDAD 3 ENZIMAS.pdf
4. UNIDAD 3 ENZIMASred.pdf
5. UNIDAD 4 CHOS (ok).pdf
6. Unidad 4 CHOS (material extra).pdf
7. Unidad 5 LIPIDOS (ok).pdf
8. Unidad 6 Aminoacidos y Proteinas (ok).pdf
9. Unidad 7 Ácidos nucleicos (final).pdf
10. Unidad 8 Vitaminas (final).pdf

## Design Decisions

1. **One-time script** - Index PDFs once with `python scripts/index_pdfs.py`
2. **All 10 PDFs** - Include all files, even duplicates/extras
3. **PDFs stay in root** - No reorganization
4. **Simple retry** - If script fails, run again from scratch
5. **Remove uploader** - Clean UI, no file upload option

## Changes Required

### 1. New: `scripts/index_pdfs.py`

Script that:
- Finds all `*.pdf` files in project root
- Creates a new File Search Store in Gemini
- Uploads each PDF with display_name = filename
- Saves store_name to `.streamlit/rag_store.json`
- Prints progress with emoji indicators

### 2. Modify: `app.py`

Remove from sidebar:
- `st.file_uploader()`
- "Indexar Documento" button
- Temporary file handling code

Add:
- Show count of indexed documents: "📚 10 documentos listos"
- Error if store not found: "⚠️ Ejecuta: python scripts/index_pdfs.py"

### 3. Update: `.gitignore`

Add `*.pdf` to prevent large files from being committed.

## Usage

```bash
# First time setup
python scripts/index_pdfs.py

# Run app
streamlit run app.py
```

## Verification

Ask Rosalind questions that require PDF content:
- "¿Cuáles son las características del agua según la unidad 1?"
- "Explícame la glucólisis según los apuntes"
