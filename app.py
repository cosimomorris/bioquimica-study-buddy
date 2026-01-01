# app.py
"""BioChem Study Buddy - Streamlit Application."""
import os
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="BioChem Study Buddy",
    page_icon="🧬",
    layout="wide"
)

# Load API key from secrets.toml
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    os.environ["GOOGLE_API_KEY"] = api_key
except KeyError:
    st.error("Missing API key. Create `.streamlit/secrets.toml` with:\n\n```\nGOOGLE_API_KEY = \"your_key_here\"\n```")
    st.stop()

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client" not in st.session_state:
    st.session_state.client = None
if "rag_manager" not in st.session_state:
    st.session_state.rag_manager = None

# Initialize client once
if st.session_state.client is None:
    from core.client import get_client
    from core.rag_manager import RAGManager

    try:
        st.session_state.client = get_client()
        st.session_state.rag_manager = RAGManager(st.session_state.client)
    except Exception as e:
        st.error(f"Connection failed: {e}")
        st.stop()

# Sidebar
with st.sidebar:
    st.header("Configuration")
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
                except Exception as e:
                    st.error(f"Indexing failed: {e}")
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
highlight it in a 'Clinical Relevance' box.

When explaining metabolic pathways, reaction mechanisms, enzyme cascades, or
biological processes, include a Mermaid diagram to visualize the concept.
Use ```mermaid code blocks with graph TD (top-down) or graph LR (left-right) syntax.
Keep diagrams clear and focused on the key steps."""

            # Generate response
            response = None
            try:
                response = st.session_state.client.models.generate_content(
                    model="gemini-3-pro-preview",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        tools=tools if tools else None
                    )
                )
                assistant_message = response.text if response.text else "I couldn't generate a response."
            except Exception as e:
                assistant_message = f"Error: {e}"

            st.markdown(assistant_message)

            # Show citations if available
            if response and hasattr(response, 'grounding_metadata') and response.grounding_metadata:
                with st.expander("Sources"):
                    for source in response.grounding_metadata.get('sources', []):
                        st.write(f"- {source}")

    st.session_state.messages.append({"role": "assistant", "content": assistant_message})
