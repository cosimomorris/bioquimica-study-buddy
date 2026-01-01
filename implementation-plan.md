This implementation plan is designed to be used with **Claude Code** (or any agentic IDE). It provides a structured roadmap, file architecture, and specific logic patterns required to build the **BioChem Study Buddy** using Gemini's 2025 toolset.

Save the content below as `implementation_plan.md` in your project root.

---

# Implementation Plan: Gemini BioChem Study Buddy

## 1. Project Overview
A Streamlit-based AI tutor for medical students. It uses Gemini 3 for reasoning, Managed File Search for RAG (textbooks/lecture notes), and Function Calling for biochemical calculations.

### Tech Stack
- **LLM:** Gemini 3 Pro / Flash (via `google-genai` SDK)
- **UI:** Streamlit
- **RAG:** Gemini Managed File Search (Vector Store)
- **Tools:** Python-based function calling (Calculators) + Google Search Grounding

---

## 2. Project Structure
```text
biochem-study-buddy/
├── app.py                # Main Streamlit UI and Orchestration
├── core/
│   ├── client.py         # Gemini Client initialization & Tool Registry
│   ├── tools.py          # Custom biochemical functions (pH, Kinetics)
│   └── rag_manager.py    # Logic for file uploads and store management
├── assets/               # Local styles/CSS
├── data/                 # Temporary storage for uploaded PDFs
├── requirements.txt      # Dependencies
└── .env                  # API Keys
```

---

## 3. Implementation Phases

### Phase 1: Environment & SDK Setup
**Task:** Configure the environment and initialize the Gemini client.
- Install `google-genai`, `streamlit`, `python-dotenv`.
- Create `.env` for `GOOGLE_API_KEY`.
- Define the `client.py` to return a configured Gemini client with `thinking_mode` capabilities if available.

### Phase 2: Agentic Tool Development (`core/tools.py`)
**Task:** Create the "calculators" the agent will use for precise biochemistry math.
- **`calculate_ph(pka, acid_conc, base_conc)`**: Implements Henderson-Hasselbalch.
- **`enzyme_kinetics(v_max, km, substrate_conc)`**: Implements Michaelis-Menten.
- **`isoelectric_point(pka_values)`**: Calculates pI for amino acids.
- **Instruction:** All functions must include docstrings, as Gemini uses these to understand when to call the tool.

### Phase 3: Managed RAG Implementation (`core/rag_manager.py`)
**Task:** Implement the "File Search" capability.
- Use `client.files.create_file_search_store` to create a permanent vector store for the session.
- Create a function to upload user-provided PDFs (e.g., *Lehninger Principles of Biochemistry*) to this store.
- Ensure the model is configured to use the `file_search_stores` parameter in its generation config.

### Phase 4: Core Orchestration (`app.py`)
**Task:** Build the Streamlit interface and chat loop.
- **Sidebar:** API Key input, PDF Uploader (triggers RAG indexing), and Tool Toggle.
- **Chat Interface:** Use `st.chat_message` and `st.chat_input`.
- **Logic:** 
    1. Capture user input.
    2. Call `client.models.generate_content`.
    3. Pass `tools=[calculate_ph, ...]` and `tool_config`.
    4. Handle the response, specifically extracting `grounding_metadata` to display citations from the textbooks.

### Phase 5: UI/UX for Medical Students
**Task:** Add specialized medical visualization.
- Implement "Thought Process" expanders to show Gemini's step-by-step reasoning (using `thought=True` in the API).
- Add a "Citation View" that maps RAG sources back to the uploaded PDF filenames.

---

## 4. Prompt Engineering & System Instructions
The system prompt is critical for medical accuracy. Use the following:
> "You are an expert Biochemistry Professor for medical students. You provide answers grounded in the provided textbooks. When asked for calculations, you MUST use the provided calculation tools rather than doing math yourself. Always cite your sources using [Source Name] format. If a concept has a clinical correlation (e.g., a specific disease related to an enzyme deficiency), highlight it in a 'Clinical Relevance' box."

---

## 5. Claude Code Action Commands
*Run these instructions sequentially with Claude Code:*

1. **Setup:** "Create a requirements.txt file with `google-genai`, `streamlit`, `python-dotenv`, and `reactome2py`. Then create a .env template."
2. **Tools:** "Write a Python script `core/tools.py` containing biochemistry functions for Henderson-Hasselbalch and Michaelis-Menten equations with clear docstrings."
3. **RAG:** "Write `core/rag_manager.py` using the `google-genai` SDK to handle creating a File Search Store and uploading PDF files."
4. **App:** "Build a Streamlit app in `app.py` that integrates the tools and the RAG manager, allowing users to upload documents and chat with Gemini 3 Flash. Ensure it displays citations from the grounding metadata."

---

## 6. Verification & Testing
- **Test Case 1 (Agentic):** "Calculate the pH of a solution with 0.1M Acetic Acid (pKa 4.76) and 0.05M Sodium Acetate." -> *Verify tool use.*
- **Test Case 2 (RAG):** "According to the uploaded notes, what is the rate-limiting enzyme of the Pentose Phosphate Pathway?" -> *Verify citation link.*
- **Test Case 3 (Grounding):** "What are the latest clinical findings on G6PD deficiency treatments?" -> *Verify Google Search tool usage.*