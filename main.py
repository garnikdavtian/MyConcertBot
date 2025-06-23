import os
import logging
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from langchain_community.embeddings import OllamaEmbeddings

from llm_utils import summarize_text, language_model
from filter_docs import ingest_document, is_concert_related
from qa_system import answer_query

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
DATA_DIR = "documents"
FAISS_DB_DIR = os.getenv("FAISS_DB_DIR", "faiss_db")
TXT_EXT = "txt"
embedding_model = None

def ensure_directories():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(FAISS_DB_DIR, exist_ok=True)
    logging.info(f"Ensured directories: {DATA_DIR}, {FAISS_DB_DIR}")

st.set_page_config(page_title="MyConcertBot", layout="wide")
st.title("MyConcertBot 🎶")
st.markdown("""
Upload text files and get concert-related content automatically filtered, indexed, and summarized.
""")

ensure_directories()

st.sidebar.header("Options")
selected_action = st.sidebar.radio("Choose an action:", ["Upload Document", "Ask a Question"])

if embedding_model is None:
    embedding_model = OllamaEmbeddings(model="nomic-embed-text")

if selected_action == "Upload Document":
    uploaded_files = st.file_uploader("📂 Upload one or more .txt files", type=[TXT_EXT], accept_multiple_files=True)

    if uploaded_files:
        summaries = []
        progress = st.progress(0, text="🔍 Processing uploaded documents...")

        for i, file in enumerate(uploaded_files):
            filename = file.name
            filepath = os.path.join(DATA_DIR, filename)

            try:
                # Temporary save documents for checking if document is related
                with open(filepath, "wb") as f:
                    f.write(file.getbuffer())

                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                if is_concert_related(content):
                    with st.spinner(f"📥 Indexing {filename}..."):
                        ingest_document(filepath, embedding_model, FAISS_DB_DIR)

                    summary = summarize_text(content, language_model)
                    summaries.append((filename, summary))
                    st.success(f"✅ {filename} indexed and kept.")
                else:
                    # Delete if not related
                    os.remove(filepath)
                    summaries.append((filename, "⚠️ Not concert-related. Deleted."))
                    st.info(f"ℹ️ {filename} was not concert-related and was removed.")

            except Exception as e:
                summaries.append((filename, f"❌ Error: {e}"))
                st.error(f"Error while processing {filename}: {e}")
                if os.path.exists(filepath):
                    os.remove(filepath)

            progress.progress((i + 1) / len(uploaded_files), text=f"📄 Processed: {filename}")

        progress.empty()

        st.subheader("📝 Summary of processed documents:")
        for name, summ in summaries:
            st.markdown(f"**{name}**")
            st.markdown("```text\n" + summ.strip() + "\n```")

elif selected_action == "Ask a Question":
    user_query = st.text_input("Enter your question:")

    if user_query:
        with st.spinner("Searching for the answer..."):
            response = answer_query(user_query, embedding_model, FAISS_DB_DIR)
        st.markdown("### Answer")
        st.write(response)
        if response.startswith("🔎 Here's what I found online"):
            st.info("🔍 I used online search (SerpAPI) for this answer.")

        with st.expander("Show Summary of the Answer"):
            summary = summarize_text(response, language_model)
            st.info(summary)
