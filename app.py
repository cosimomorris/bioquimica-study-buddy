# app.py
"""Compañero de Estudio de Bioquímica - Aplicación Streamlit."""
import os
import re
import requests
import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_mermaid import st_mermaid


@st.cache_data
def load_lottie_url(url: str):
    """Cargar animación Lottie desde URL."""
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


# URL de animación de Rosalind (robot/asistente animado)
ROSALIND_ANIMATION = "https://assets5.lottiefiles.com/packages/lf20_tutvdkg0.json"


def render_message_with_diagrams(content: str):
    """Render message content, converting Mermaid blocks to diagrams."""
    # Pattern to match ```mermaid ... ``` blocks
    pattern = r'```mermaid\s*([\s\S]*?)```'

    parts = re.split(pattern, content)

    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Text content
            if part.strip():
                st.markdown(part)
        else:
            # Mermaid diagram - render with streamlit-mermaid
            st_mermaid(part.strip())


# Configuración de página
st.set_page_config(
    page_title="Rosalind - Tu Tutora de Bioquímica",
    page_icon="🧬",
    layout="wide"
)

# Cargar API key desde secrets.toml
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    os.environ["GOOGLE_API_KEY"] = api_key
except KeyError:
    st.error("Falta la API key. Crea `.streamlit/secrets.toml` con:\n\n```\nGOOGLE_API_KEY = \"tu_api_key_aqui\"\n```")
    st.stop()

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client" not in st.session_state:
    st.session_state.client = None
if "rag_manager" not in st.session_state:
    st.session_state.rag_manager = None
if "store_loaded" not in st.session_state:
    st.session_state.store_loaded = False

# Inicializar cliente una vez
if st.session_state.client is None:
    from core.client import get_client
    from core.rag_manager import RAGManager

    try:
        st.session_state.client = get_client()
        st.session_state.rag_manager = RAGManager(st.session_state.client)
        # Intentar cargar almacén de documentos existente
        if st.session_state.rag_manager.load_existing_store():
            st.session_state.store_loaded = True
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.stop()

# Barra lateral
with st.sidebar:
    st.header("Configuración")
    st.success("¡Conectado a Gemini!")

    # Mostrar estado del almacén de documentos
    if st.session_state.store_loaded:
        st.info("📚 Documentos cargados de la sesión anterior")
    st.divider()

    # Subir PDFs
    st.subheader("Subir Documentos")
    uploaded_file = st.file_uploader(
        "Sube libros de texto o apuntes en PDF",
        type=["pdf", "txt", "md"],
        help="Los documentos serán indexados para búsqueda"
    )

    if uploaded_file and st.session_state.rag_manager:
        if st.button("Indexar Documento"):
            with st.spinner("Indexando documento..."):
                # Guardar en archivo temporal y subir
                import tempfile
                import os

                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as f:
                    f.write(uploaded_file.getvalue())
                    temp_path = f.name

                try:
                    if st.session_state.rag_manager.store is None:
                        st.session_state.rag_manager.create_store("bioquimica-study-buddy")

                    st.session_state.rag_manager.upload_file(
                        file_path=temp_path,
                        display_name=uploaded_file.name
                    )
                    st.success(f"Indexado: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"Error al indexar: {e}")
                finally:
                    os.unlink(temp_path)

    st.divider()

    # Herramientas de cálculo
    st.subheader("Calculadoras")
    use_ph_calc = st.checkbox("Calculadora de pH", value=True)
    use_kinetics = st.checkbox("Cinética Enzimática", value=True)
    use_pi_calc = st.checkbox("Punto Isoeléctrico", value=True)

# Interfaz principal de chat
col1, col2 = st.columns([1, 4])
with col1:
    lottie_rosalind = load_lottie_url(ROSALIND_ANIMATION)
    if lottie_rosalind:
        st_lottie(lottie_rosalind, height=120, key="rosalind_avatar")
    else:
        st.markdown("## 👩‍🔬")  # Fallback si no carga la animación
with col2:
    st.title("🧬 Rosalind")
    st.caption("Tu tutora de bioquímica personal • Creada con 💕 por Cosimo para Jimena")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            render_message_with_diagrams(message["content"])
        else:
            st.markdown(message["content"])

# Entrada de chat
if prompt := st.chat_input("¿En qué te ayudo, Jimena? 💬"):
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            from google.genai import types
            from core.tools import calculate_ph, enzyme_kinetics, isoelectric_point

            # Construir lista de herramientas según toggles
            tools = []
            if use_ph_calc:
                tools.append(calculate_ph)
            if use_kinetics:
                tools.append(enzyme_kinetics)
            if use_pi_calc:
                tools.append(isoelectric_point)

            # Agregar herramienta RAG si está disponible
            if st.session_state.rag_manager and st.session_state.rag_manager.store:
                tools.append(st.session_state.rag_manager.get_file_search_tool())

            # Prompt del sistema - Rosalind
            system_instruction = """Eres Rosalind, tutora de bioquímica y buena amiga.
Fuiste creada por Cosimo para ayudar a Jimena (el amor de su vida) a pasar su examen de bioquímica.

## Tu personalidad:
- Tono amigable pero enfocado: cercana sin ser demasiado informal
- Puedes usar expresiones como "¡Muy bien!", "¡Exacto!", "Ojo con esto"
- Eres directa y clara, siempre motivando a Jimena
- Eres PROACTIVA: al final haces una pregunta de seguimiento o mini-reto
  Ejemplo: "¿Te quedó claro? ¿Le damos otra vuelta? 🤔"
- Si se equivoca, corriges con buena onda: "No exactamente, pero vas por buen camino. Mira:"
- Cuando le atina: "¡Exacto, Jimena! 🎯" o "¡Muy bien!"

## Tu estilo de enseñanza:
- Explicaciones CLARAS y DIRECTAS - al punto
- Usa analogías prácticas para conceptos difíciles
- Marca lo que es "pregunta clásica de examen" o "esto es importante"
- Si hay correlación clínica: '🏥 Relevancia clínica:'

## Herramientas:
- Para cálculos (pH, cinética, pI), USA las calculadoras proporcionadas
- Para vías metabólicas o procesos, incluye diagramas Mermaid (```mermaid)
- Cita fuentes con [Nombre de la Fuente] cuando uses los libros

## Tu misión:
- Que Jimena APRUEBE su examen
- Siempre en español
- Directo al punto - ella necesita estudiar eficientemente
- Termina con algo que la mantenga enganchada: pregunta, reto, dato interesante"""

            # Generar respuesta
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
                assistant_message = response.text if response.text else "No pude generar una respuesta."
            except Exception as e:
                assistant_message = f"Error: {e}"

            render_message_with_diagrams(assistant_message)

            # Mostrar citas si están disponibles
            if response and hasattr(response, 'grounding_metadata') and response.grounding_metadata:
                with st.expander("Fuentes"):
                    for source in response.grounding_metadata.get('sources', []):
                        st.write(f"- {source}")

    st.session_state.messages.append({"role": "assistant", "content": assistant_message})
