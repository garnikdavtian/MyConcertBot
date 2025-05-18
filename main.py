import streamlit as st
import os
from datetime import datetime
import subprocess
import shutil
from langchain_community.embeddings import OllamaEmbeddings
from llm_utils import summarize_text
from llm_utils import language_model
from filter_docs import ingest_document, is_concert_related
from qa_system import answer_query



def is_faiss_index_built(db_dir):
    return os.path.exists(os.path.join(db_dir, "index.faiss"))



def start_ollama_if_not_running():
    ollama_binary = shutil.which("ollama")
    if ollama_binary is None:
        raise RuntimeError("❌ Ollama is not installed or not in PATH.")
    
    try:
        subprocess.run(["ollama", "list"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("🚀 Starting Ollama server...")
        subprocess.Popen(["ollama", "serve"])



start_ollama_if_not_running()


DATA_DIR = "documents"
FAISS_DB_DIR = "faiss_db"

embedding_model = OllamaEmbeddings(model="nomic-embed-text")

st.set_page_config(page_title="Concert Document Ingestion", layout="centered")
st.title("🌟 Concert Document Ingestion")



if not is_faiss_index_built(FAISS_DB_DIR):
    st.warning("🔄 Creating FAISS index (not found)...")
    for filename in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            ingest_document(text, FAISS_DB_DIR, language_model, embedding_model, filename)
    st.success("✅ Index built.")


st.header("📂 Upload a .txt File")
uploaded_file = st.file_uploader("Choose a .txt file", type="txt")


if uploaded_file is not None:
    text = uploaded_file.read().decode("utf-8")
    if not is_concert_related(text, language_model):
        st.write("❌ Skipped: Not related to concert/tour. File was NOT saved.")
    else:
        save_path = os.path.join(DATA_DIR, uploaded_file.name)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(text)
        st.success(f"Saved {uploaded_file.name} to disk.")

        with st.spinner("Analyzing and ingesting the document..."):
            ingest_document(text, FAISS_DB_DIR, language_model, embedding_model, uploaded_file.name)
            st.success("✅ Document processed!")

            summary = summarize_text(text, language_model)
            if summary:
                st.markdown("### 📄 Document Summary:")
                st.write(summary)


st.header("📝 Or Enter Text Manually")
user_text = st.text_area("Paste your concert-related document here:")

if st.button("Submit Text"):
    if user_text.strip():
        if not is_concert_related(user_text, language_model):
            st.write("❌ Skipped: Not related to concert/tour. Text not saved.")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"manual_input_{timestamp}.txt"
            save_path = os.path.join(DATA_DIR, filename)

            with open(save_path, "w", encoding="utf-8") as f:
                f.write(user_text)

            st.success(f"Text saved as {filename}.")

            with st.spinner("Analyzing and ingesting the document..."):
                ingest_document(user_text, FAISS_DB_DIR, language_model, embedding_model, filename)
                st.success("📦 Ingested and stored successfully.")

                summary = summarize_text(user_text, language_model)
                if summary:
                    st.markdown("### 📄 Document Summary:")
                    st.write(summary)

    else:
        st.warning("Please enter some text before submitting.")



st.header("🤖 Ask a Question about Concerts")
user_question = st.text_input("Enter your question:")

if st.button("Get Answer"):
    if user_question.strip():
        with st.spinner("Searching and generating answer..."):
            answer = answer_query(language_model, FAISS_DB_DIR, embedding_model, user_question, top_k=4)
            st.markdown(f"**Answer:** {answer}")
    else:
        st.warning("Please enter a question.")
