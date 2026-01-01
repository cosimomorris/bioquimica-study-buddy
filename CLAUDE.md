# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BioChem Study Buddy is a Streamlit-based AI tutor for medical students using Google Gemini 3 for reasoning, Managed File Search for RAG (textbooks/lecture notes), and Function Calling for biochemical calculations.

**Current Status:** Functional implementation with core features complete.

## Tech Stack

- **LLM:** Google Gemini 3 Pro/Flash (`google-genai` SDK)
- **UI:** Streamlit
- **RAG:** Gemini Managed File Search (Vector Store)
- **Tools:** Python function calling + Google Search grounding
- **Dependencies:** google-genai, streamlit, pytest

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key (copy template and add your key)
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your Google API key

# Run the application
streamlit run app.py

# Run tests
pytest
```

## Architecture

```
biochem-study-buddy/
├── app.py                # Streamlit UI and orchestration
├── core/
│   ├── client.py         # Gemini client initialization & tool registry
│   ├── tools.py          # Biochemical calculation functions (pH, kinetics, pI)
│   └── rag_manager.py    # File upload & vector store management
├── assets/               # CSS/styles
├── data/                 # Temporary PDF storage
├── requirements.txt
├── .streamlit/
│   ├── secrets.toml          # GOOGLE_API_KEY (git-ignored)
│   └── secrets.toml.example  # Template for secrets
└── tests/                    # pytest test suite
```

### Key Components

**Agentic Tools (`core/tools.py`):** Biochemistry calculators that Gemini calls via function calling:
- `calculate_ph()` - Henderson-Hasselbalch equation
- `enzyme_kinetics()` - Michaelis-Menten kinetics
- `isoelectric_point()` - Amino acid pI calculation

All tool functions require clear docstrings as Gemini uses them to understand when to invoke each tool.

**RAG Manager (`core/rag_manager.py`):** Handles Gemini's Managed File Search:
- Creates permanent vector stores via `client.files.create_file_search_store`
- Uploads user PDFs (textbooks, lecture notes)
- Model uses `file_search_stores` parameter in generation config

**Streamlit App (`app.py`):**
- API key loaded from `.streamlit/secrets.toml` via `st.secrets`
- Sidebar: PDF uploader, tool toggles
- Chat interface: `st.chat_message` + `st.chat_input`
- Citation extraction from `grounding_metadata`

## System Prompt

The app uses this system prompt for medical accuracy:

> "You are an expert Biochemistry Professor for medical students. You provide answers grounded in the provided textbooks. When asked for calculations, you MUST use the provided calculation tools rather than doing math yourself. Always cite your sources using [Source Name] format. If a concept has a clinical correlation (e.g., a specific disease related to an enzyme deficiency), highlight it in a 'Clinical Relevance' box."

## Test Cases

- **Tool invocation:** "Calculate the pH of a solution with 0.1M Acetic Acid (pKa 4.76) and 0.05M Sodium Acetate."
- **RAG retrieval:** "According to the uploaded notes, what is the rate-limiting enzyme of the Pentose Phosphate Pathway?"
- **Google grounding:** "What are the latest clinical findings on G6PD deficiency treatments?"
