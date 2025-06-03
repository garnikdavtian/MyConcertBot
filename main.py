import os
import shutil
import subprocess
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

from langchain_community.embeddings import OllamaEmbeddings
from llm_utils import summarize_text, language_model, is_concert_related_text
from filter_docs import ingest_document, is_concert_related
from qa_system import answer_query

# Constants
DATA_DIR = "documents"
FAISS_DB_DIR = "faiss_db"
TXT_EXT = "txt"


def ensure_directories() -> None:
    """
    Make sure DATA_DIR and FAISS_DB_DIR exist.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(FAISS_DB_DIR, exist_ok=True)


def is_faiss_index_built(db_dir: str) -> bool:
    """
    Checks if the FAISS index file exists on disk.
    """
    return os.path.exists(os.path.join(db_dir, "index.faiss"))


def start_ollama_if_not_running() -> None:
    """
    Verifies that Ollama is installed and starts the daemon if not already running.
    """
    if shutil.which("ollama") is None:
        raise RuntimeError("❌ Ollama is not installed or not in PATH.")

    try:
        subprocess.run(
            ["ollama", "list"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:

        subprocess.Popen(["ollama", "serve"])


def save_text_file(text: str, filename: str) -> str:
    """
    Save raw text to DATA_DIR/filename. Returns the full path.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    save_path = os.path.join(DATA_DIR, filename)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(text)
    return save_path


def handle_ingestion(
    text: str,
    filename: str,
    language_model,
    embedding_model,
) -> None:
    """
    Wrapper to save, classify, and ingest text if it’s concert-related.
    """
    if not is_concert_related(text, language_model):
        st.error("❌ Not related to concerts. Skipping ingestion.")
        return

    # Save file
    save_path = save_text_file(text, filename)
    try:
        ingest_document(text, FAISS_DB_DIR, language_model, embedding_model, filename)
        st.success(f"📁 '{filename}' ingested successfully.")
    except Exception as e:
        st.error(f"❌ Failed to ingest '{filename}': {e}")
        return

    # Show summary if available
    summary = summarize_text(text, language_model)
    if summary:
        with st.expander("📄 Document Summary"):
            st.write(summary)


def build_faiss_index_if_needed():
    """
    On app startup, if there’s no FAISS index, read every .txt in DATA_DIR and ingest.
    """
    if is_faiss_index_built(FAISS_DB_DIR):
        return

    st.warning("⚠️ FAISS index not found. Building now...")
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(f".{TXT_EXT}"):
            continue

        file_path = os.path.join(DATA_DIR, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            ingest_document(text, FAISS_DB_DIR, language_model, embedding_model, filename)
        except Exception as e:
            st.error(f"❌ Failed to ingest {filename}: {e}")

    st.success("✅ FAISS index built successfully.")


# Ensure folders & start Ollama
ensure_directories()
start_ollama_if_not_running()
embedding_model = OllamaEmbeddings(model="nomic-embed-text")

# Streamlit configuration
st.set_page_config(page_title="🎶 Concerts Assistant", layout="centered")
st.title("🎤 Concert Knowledge Assistant")

# Create Tabs
tabs = st.tabs(["💬 Chat Assistant", "📂 Upload File", "📝 Paste Text"])

# --- Tab 1: Chat Assistant ---
with tabs[0]:
    st.subheader("Chat about Concerts")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous chat messages
    for msg in st.session_state.messages:
        role = msg["role"]
        with st.chat_message(role):
            st.markdown(msg["content"])

    # New user prompt
    prompt = st.chat_input("Ask something about concerts...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Thinking..."):
            try:
                answer = answer_query(
                    language_model, FAISS_DB_DIR, embedding_model, prompt, top_k=4
                )
            except Exception as e:
                answer = f"❌ Error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

# --- Tab 2: Upload File ---
with tabs[1]:
    st.subheader("Upload a Text File")
    uploaded_file = st.file_uploader("Upload .txt file", type=[TXT_EXT])
    if uploaded_file:
        try:
            raw_text = uploaded_file.read().decode("utf-8")
            handle_ingestion(raw_text, uploaded_file.name, language_model, embedding_model)
        except Exception as e:
            st.error(f"❌ Could not read or ingest the file: {e}")

# --- Tab 3: Paste Text ---
with tabs[2]:
    st.subheader("Paste Your Own Text")
    manual_text = st.text_area("Paste concert-related text here")
    if st.button("Ingest Text"):
        if manual_text.strip():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"manual_input_{timestamp}.{TXT_EXT}"
            handle_ingestion(manual_text, filename, language_model, embedding_model)
        else:
            st.warning("⚠️ Please paste some text first.")

# Build FAISS Index if needed on startup
build_faiss_index_if_needed()
