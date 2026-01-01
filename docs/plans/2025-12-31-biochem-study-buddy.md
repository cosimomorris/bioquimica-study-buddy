# BioChem Study Buddy Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Streamlit-based AI tutor for medical students using Gemini for reasoning, File Search for RAG, and function calling for biochemical calculations.

**Architecture:** Streamlit frontend with sidebar controls (API key, PDF upload, tool toggles) and chat interface. Backend uses `google-genai` SDK for Gemini client, custom Python tools for biochemistry calculations, and File Search stores for document-based RAG. All tool functions require clear docstrings as Gemini uses them for function selection.

**Tech Stack:** Python 3.11+, google-genai SDK, Streamlit, python-dotenv

---

## Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`

**Step 1: Create requirements.txt**

```txt
google-genai>=1.0.0
streamlit>=1.40.0
python-dotenv>=1.0.0
pytest>=8.0.0
```

**Step 2: Create .env.example**

```txt
GOOGLE_API_KEY=your_gemini_api_key_here
```

**Step 3: Create .gitignore**

```txt
.env
__pycache__/
*.pyc
.pytest_cache/
data/
.streamlit/
```

**Step 4: Commit**

```bash
git add requirements.txt .env.example .gitignore
git commit -m "chore: initial project setup with dependencies"
```

---

## Task 2: Gemini Client Module

**Files:**
- Create: `core/__init__.py`
- Create: `core/client.py`
- Test: `tests/__init__.py`
- Test: `tests/test_client.py`

**Step 1: Create directory structure**

```bash
mkdir -p core tests
touch core/__init__.py tests/__init__.py
```

**Step 2: Write the failing test**

```python
# tests/test_client.py
import pytest
from unittest.mock import patch, MagicMock


def test_get_client_returns_genai_client():
    """Client should be created with API key from environment."""
    with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
        with patch("google.genai.Client") as mock_client:
            mock_client.return_value = MagicMock()
            from core.client import get_client

            client = get_client()

            mock_client.assert_called_once_with(api_key="test-key")
            assert client is not None


def test_get_client_raises_without_api_key():
    """Client should raise ValueError when API key is missing."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
            from importlib import reload
            import core.client
            reload(core.client)
            core.client.get_client()
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/test_client.py -v`
Expected: FAIL with "No module named 'core.client'"

**Step 4: Write minimal implementation**

```python
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
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_client.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add core/ tests/
git commit -m "feat: add Gemini client initialization module"
```

---

## Task 3: Henderson-Hasselbalch pH Calculator

**Files:**
- Create: `core/tools.py`
- Test: `tests/test_tools.py`

**Step 1: Write the failing test**

```python
# tests/test_tools.py
import pytest
import math


def test_calculate_ph_basic_buffer():
    """pH calculation using Henderson-Hasselbalch equation."""
    from core.tools import calculate_ph

    # Acetic acid buffer: pKa=4.76, [A-]=0.05M, [HA]=0.1M
    result = calculate_ph(pka=4.76, acid_conc=0.1, base_conc=0.05)

    # pH = pKa + log([A-]/[HA]) = 4.76 + log(0.5) = 4.76 - 0.301 = 4.459
    assert abs(result - 4.459) < 0.01


def test_calculate_ph_equal_concentrations():
    """When acid and base concentrations are equal, pH equals pKa."""
    from core.tools import calculate_ph

    result = calculate_ph(pka=7.0, acid_conc=0.1, base_conc=0.1)

    assert abs(result - 7.0) < 0.001


def test_calculate_ph_raises_on_zero_concentration():
    """Zero concentration should raise ValueError."""
    from core.tools import calculate_ph

    with pytest.raises(ValueError, match="must be positive"):
        calculate_ph(pka=4.76, acid_conc=0, base_conc=0.1)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_tools.py::test_calculate_ph_basic_buffer -v`
Expected: FAIL with "cannot import name 'calculate_ph'"

**Step 3: Write minimal implementation**

```python
# core/tools.py
"""Biochemical calculation tools for Gemini function calling."""
import math


def calculate_ph(pka: float, acid_conc: float, base_conc: float) -> float:
    """
    Calculate pH using the Henderson-Hasselbalch equation.

    This tool calculates the pH of a buffer solution given the pKa of the
    weak acid and the concentrations of the acid and its conjugate base.

    Formula: pH = pKa + log10([conjugate base] / [weak acid])

    Args:
        pka: The pKa value of the weak acid (e.g., 4.76 for acetic acid).
        acid_conc: Concentration of the weak acid in mol/L (must be positive).
        base_conc: Concentration of the conjugate base in mol/L (must be positive).

    Returns:
        The calculated pH value of the buffer solution.

    Raises:
        ValueError: If either concentration is zero or negative.

    Example:
        >>> calculate_ph(pka=4.76, acid_conc=0.1, base_conc=0.05)
        4.459  # Acetic acid buffer
    """
    if acid_conc <= 0 or base_conc <= 0:
        raise ValueError("Concentrations must be positive values")

    return pka + math.log10(base_conc / acid_conc)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_tools.py -v -k "calculate_ph"`
Expected: PASS (all 3 tests)

**Step 5: Commit**

```bash
git add core/tools.py tests/test_tools.py
git commit -m "feat: add Henderson-Hasselbalch pH calculator tool"
```

---

## Task 4: Michaelis-Menten Enzyme Kinetics Calculator

**Files:**
- Modify: `core/tools.py`
- Modify: `tests/test_tools.py`

**Step 1: Write the failing test**

```python
# Add to tests/test_tools.py

def test_enzyme_kinetics_half_vmax():
    """When [S] = Km, velocity should be Vmax/2."""
    from core.tools import enzyme_kinetics

    result = enzyme_kinetics(v_max=100, km=10, substrate_conc=10)

    assert abs(result - 50.0) < 0.01


def test_enzyme_kinetics_high_substrate():
    """At very high [S], velocity approaches Vmax."""
    from core.tools import enzyme_kinetics

    result = enzyme_kinetics(v_max=100, km=10, substrate_conc=1000)

    assert result > 99.0  # Should be close to Vmax


def test_enzyme_kinetics_raises_on_invalid_params():
    """Negative or zero parameters should raise ValueError."""
    from core.tools import enzyme_kinetics

    with pytest.raises(ValueError):
        enzyme_kinetics(v_max=-100, km=10, substrate_conc=5)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_tools.py::test_enzyme_kinetics_half_vmax -v`
Expected: FAIL with "cannot import name 'enzyme_kinetics'"

**Step 3: Write minimal implementation**

```python
# Add to core/tools.py

def enzyme_kinetics(v_max: float, km: float, substrate_conc: float) -> float:
    """
    Calculate reaction velocity using the Michaelis-Menten equation.

    This tool computes the initial velocity of an enzyme-catalyzed reaction
    given the kinetic parameters and substrate concentration.

    Formula: v = (Vmax * [S]) / (Km + [S])

    Args:
        v_max: Maximum reaction velocity (Vmax) in appropriate units (e.g., umol/min).
        km: Michaelis constant (Km) in mol/L or mM.
        substrate_conc: Substrate concentration [S] in same units as Km.

    Returns:
        The calculated reaction velocity in same units as Vmax.

    Raises:
        ValueError: If any parameter is zero or negative.

    Example:
        >>> enzyme_kinetics(v_max=100, km=10, substrate_conc=10)
        50.0  # At [S] = Km, velocity is Vmax/2
    """
    if v_max <= 0 or km <= 0 or substrate_conc <= 0:
        raise ValueError("All parameters must be positive values")

    return (v_max * substrate_conc) / (km + substrate_conc)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_tools.py -v -k "enzyme_kinetics"`
Expected: PASS (all 3 tests)

**Step 5: Commit**

```bash
git add core/tools.py tests/test_tools.py
git commit -m "feat: add Michaelis-Menten enzyme kinetics calculator"
```

---

## Task 5: Isoelectric Point Calculator

**Files:**
- Modify: `core/tools.py`
- Modify: `tests/test_tools.py`

**Step 1: Write the failing test**

```python
# Add to tests/test_tools.py

def test_isoelectric_point_glycine():
    """Glycine pI is average of pKa1 (2.34) and pKa2 (9.60)."""
    from core.tools import isoelectric_point

    result = isoelectric_point(pka_values=[2.34, 9.60])

    assert abs(result - 5.97) < 0.01


def test_isoelectric_point_aspartate():
    """Acidic amino acid uses two lowest pKa values."""
    from core.tools import isoelectric_point

    # Aspartate: pKa1=1.88, pKa2=3.65, pKa3=9.60
    # pI = (1.88 + 3.65) / 2 = 2.77
    result = isoelectric_point(pka_values=[1.88, 3.65, 9.60])

    assert abs(result - 2.77) < 0.01


def test_isoelectric_point_raises_on_insufficient_pkas():
    """Need at least 2 pKa values."""
    from core.tools import isoelectric_point

    with pytest.raises(ValueError, match="at least 2"):
        isoelectric_point(pka_values=[4.5])
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_tools.py::test_isoelectric_point_glycine -v`
Expected: FAIL with "cannot import name 'isoelectric_point'"

**Step 3: Write minimal implementation**

```python
# Add to core/tools.py
from typing import List


def isoelectric_point(pka_values: List[float]) -> float:
    """
    Calculate the isoelectric point (pI) of an amino acid.

    The pI is calculated as the average of the two pKa values that bracket
    the zwitterionic form. For simple amino acids, this is the average of
    pKa1 and pKa2. For acidic amino acids (3 pKa values), use the two lowest.
    For basic amino acids (3 pKa values), use the two highest.

    Args:
        pka_values: List of pKa values for the amino acid, sorted ascending.
                   Must contain at least 2 values.

    Returns:
        The calculated isoelectric point.

    Raises:
        ValueError: If fewer than 2 pKa values are provided.

    Example:
        >>> isoelectric_point(pka_values=[2.34, 9.60])  # Glycine
        5.97
        >>> isoelectric_point(pka_values=[1.88, 3.65, 9.60])  # Aspartate
        2.77
    """
    if len(pka_values) < 2:
        raise ValueError("At least 2 pKa values are required")

    sorted_pkas = sorted(pka_values)

    if len(sorted_pkas) == 2:
        return (sorted_pkas[0] + sorted_pkas[1]) / 2
    elif len(sorted_pkas) == 3:
        # Acidic amino acids: average of two lowest
        # Basic amino acids: average of two highest
        # Heuristic: if middle pKa < 7, it's acidic; otherwise basic
        if sorted_pkas[1] < 7:
            return (sorted_pkas[0] + sorted_pkas[1]) / 2
        else:
            return (sorted_pkas[1] + sorted_pkas[2]) / 2
    else:
        raise ValueError("Expected 2 or 3 pKa values")
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_tools.py -v -k "isoelectric_point"`
Expected: PASS (all 3 tests)

**Step 5: Commit**

```bash
git add core/tools.py tests/test_tools.py
git commit -m "feat: add isoelectric point calculator for amino acids"
```

---

## Task 6: RAG Manager - File Search Store Creation

**Files:**
- Create: `core/rag_manager.py`
- Test: `tests/test_rag_manager.py`

**Step 1: Write the failing test**

```python
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

    mock_client.file_search_stores.create.assert_called_once()
    assert store.name == "stores/test-store-123"


def test_rag_manager_requires_client():
    """RAGManager should require a client instance."""
    from core.rag_manager import RAGManager

    with pytest.raises(TypeError):
        RAGManager()  # Missing required client argument
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_rag_manager.py::test_create_file_search_store -v`
Expected: FAIL with "No module named 'core.rag_manager'"

**Step 3: Write minimal implementation**

```python
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

    def create_store(self, display_name: str):
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_rag_manager.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add core/rag_manager.py tests/test_rag_manager.py
git commit -m "feat: add RAGManager with file search store creation"
```

---

## Task 7: RAG Manager - File Upload

**Files:**
- Modify: `core/rag_manager.py`
- Modify: `tests/test_rag_manager.py`

**Step 1: Write the failing test**

```python
# Add to tests/test_rag_manager.py
import time


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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_rag_manager.py::test_upload_file_to_store -v`
Expected: FAIL with "has no attribute 'upload_file'"

**Step 3: Write minimal implementation**

```python
# Add to RAGManager class in core/rag_manager.py
import time


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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_rag_manager.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add core/rag_manager.py tests/test_rag_manager.py
git commit -m "feat: add file upload to RAGManager"
```

---

## Task 8: RAG Manager - Tool Configuration

**Files:**
- Modify: `core/rag_manager.py`
- Modify: `tests/test_rag_manager.py`

**Step 1: Write the failing test**

```python
# Add to tests/test_rag_manager.py

def test_get_file_search_tool():
    """Should return Tool config for generate_content."""
    mock_client = MagicMock()
    mock_store = MagicMock()
    mock_store.name = "stores/test-store-123"
    mock_client.file_search_stores.create.return_value = mock_store

    from core.rag_manager import RAGManager

    manager = RAGManager(client=mock_client)
    manager.create_store("test-store")

    tool = manager.get_file_search_tool()

    assert tool.file_search is not None
    assert "stores/test-store-123" in tool.file_search.file_search_store_names


def test_get_file_search_tool_raises_without_store():
    """Should raise error if no store exists."""
    mock_client = MagicMock()

    from core.rag_manager import RAGManager

    manager = RAGManager(client=mock_client)

    with pytest.raises(ValueError, match="store must be created"):
        manager.get_file_search_tool()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_rag_manager.py::test_get_file_search_tool -v`
Expected: FAIL with "has no attribute 'get_file_search_tool'"

**Step 3: Write minimal implementation**

```python
# Add to RAGManager class in core/rag_manager.py

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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_rag_manager.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add core/rag_manager.py tests/test_rag_manager.py
git commit -m "feat: add file search tool config to RAGManager"
```

---

## Task 9: Streamlit App - Basic Structure

**Files:**
- Create: `app.py`

**Step 1: Create the basic Streamlit structure**

```python
# app.py
"""BioChem Study Buddy - Streamlit Application."""
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="BioChem Study Buddy",
    page_icon="🧬",
    layout="wide"
)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client" not in st.session_state:
    st.session_state.client = None
if "rag_manager" not in st.session_state:
    st.session_state.rag_manager = None

# Sidebar
with st.sidebar:
    st.header("Configuration")

    api_key = st.text_input(
        "Google API Key",
        type="password",
        help="Enter your Gemini API key"
    )

    if api_key:
        import os
        os.environ["GOOGLE_API_KEY"] = api_key

        if st.session_state.client is None:
            from core.client import get_client
            from core.rag_manager import RAGManager

            st.session_state.client = get_client()
            st.session_state.rag_manager = RAGManager(st.session_state.client)
            st.success("Connected to Gemini!")

    st.divider()

    # PDF Upload
    st.subheader("Upload Documents")
    uploaded_file = st.file_uploader(
        "Upload PDF textbooks or notes",
        type=["pdf", "txt", "md"],
        help="Documents will be indexed for RAG"
    )

    if uploaded_file and st.session_state.rag_manager:
        if st.button("Index Document"):
            with st.spinner("Indexing document..."):
                # Save to temp file and upload
                import tempfile
                import os

                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as f:
                    f.write(uploaded_file.getvalue())
                    temp_path = f.name

                try:
                    if st.session_state.rag_manager.store is None:
                        st.session_state.rag_manager.create_store("biochem-study-buddy")

                    st.session_state.rag_manager.upload_file(
                        file_path=temp_path,
                        display_name=uploaded_file.name
                    )
                    st.success(f"Indexed: {uploaded_file.name}")
                finally:
                    os.unlink(temp_path)

    st.divider()

    # Tool toggles
    st.subheader("Calculator Tools")
    use_ph_calc = st.checkbox("pH Calculator", value=True)
    use_kinetics = st.checkbox("Enzyme Kinetics", value=True)
    use_pi_calc = st.checkbox("Isoelectric Point", value=True)

# Main chat interface
st.title("🧬 BioChem Study Buddy")
st.caption("AI-powered biochemistry tutor for medical students")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a biochemistry question..."):
    if not st.session_state.client:
        st.error("Please enter your API key in the sidebar first.")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                from google.genai import types
                from core.tools import calculate_ph, enzyme_kinetics, isoelectric_point

                # Build tools list based on toggles
                tools = []
                if use_ph_calc:
                    tools.append(calculate_ph)
                if use_kinetics:
                    tools.append(enzyme_kinetics)
                if use_pi_calc:
                    tools.append(isoelectric_point)

                # Add RAG tool if available
                if st.session_state.rag_manager and st.session_state.rag_manager.store:
                    tools.append(st.session_state.rag_manager.get_file_search_tool())

                # System prompt
                system_instruction = """You are an expert Biochemistry Professor for medical students.
You provide answers grounded in the provided textbooks. When asked for calculations,
you MUST use the provided calculation tools rather than doing math yourself.
Always cite your sources using [Source Name] format. If a concept has a clinical
correlation (e.g., a specific disease related to an enzyme deficiency),
highlight it in a 'Clinical Relevance' box."""

                # Generate response
                response = st.session_state.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        tools=tools if tools else None
                    )
                )

                assistant_message = response.text
                st.markdown(assistant_message)

                # Show citations if available
                if hasattr(response, 'grounding_metadata') and response.grounding_metadata:
                    with st.expander("Sources"):
                        for source in response.grounding_metadata.get('sources', []):
                            st.write(f"- {source}")

        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
```

**Step 2: Run the app manually to verify**

Run: `streamlit run app.py`
Expected: App loads with sidebar and chat interface

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add main Streamlit application with chat interface"
```

---

## Task 10: Integration Test - Full Workflow

**Files:**
- Create: `tests/test_integration.py`

**Step 1: Write integration test (requires API key)**

```python
# tests/test_integration.py
"""Integration tests - require GOOGLE_API_KEY environment variable."""
import pytest
import os


@pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY"),
    reason="GOOGLE_API_KEY not set"
)
class TestIntegration:
    """Integration tests that hit the real Gemini API."""

    def test_tool_invocation_ph_calculation(self):
        """Verify Gemini calls our pH tool correctly."""
        from core.client import get_client
        from core.tools import calculate_ph
        from google.genai import types

        client = get_client()

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Calculate the pH of a buffer with pKa=4.76, 0.1M acetic acid, and 0.05M acetate.",
            config=types.GenerateContentConfig(
                tools=[calculate_ph]
            )
        )

        # Response should contain the calculated pH value ~4.46
        assert "4.4" in response.text or "4.5" in response.text

    def test_system_prompt_enforces_tool_use(self):
        """Verify system prompt makes Gemini use tools for calculations."""
        from core.client import get_client
        from core.tools import calculate_ph, enzyme_kinetics
        from google.genai import types

        client = get_client()

        system_instruction = """When asked for calculations, you MUST use the provided
        calculation tools rather than doing math yourself."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="What is the reaction velocity when Vmax=100, Km=10, and [S]=10?",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[calculate_ph, enzyme_kinetics]
            )
        )

        # Response should contain 50 (Vmax/2 when [S]=Km)
        assert "50" in response.text
```

**Step 2: Run integration tests (if API key available)**

Run: `GOOGLE_API_KEY=your_key pytest tests/test_integration.py -v`
Expected: PASS (if API key is valid)

**Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration tests for Gemini tool invocation"
```

---

## Task 11: Final Cleanup and Documentation

**Files:**
- Update: `requirements.txt` (add any missing deps discovered)
- Verify: All tests pass

**Step 1: Run full test suite**

Run: `pytest tests/ -v --ignore=tests/test_integration.py`
Expected: All unit tests PASS

**Step 2: Verify app runs**

Run: `streamlit run app.py`
Expected: No errors, app is functional

**Step 3: Final commit**

```bash
git add -A
git commit -m "chore: finalize initial implementation"
```

---

## Verification Checklist

After completing all tasks, verify:

- [ ] `pytest tests/ -v` passes (unit tests)
- [ ] `streamlit run app.py` launches without errors
- [ ] Sidebar shows API key input, file uploader, tool toggles
- [ ] Chat interface accepts messages
- [ ] With valid API key, responses are generated
- [ ] pH calculation query triggers tool use
- [ ] Enzyme kinetics query triggers tool use
- [ ] Uploaded PDF appears in file search store
