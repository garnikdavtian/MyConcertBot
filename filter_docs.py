import os
from typing import Optional
from langchain.vectorstores import FAISS
from llm_utils import summarize_text, is_concert_related_text, language_model
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama 


def ingest_document(
    text: str,
    faiss_db_dir: str,
    language_model: ChatOllama,
    embedding_model: OllamaEmbeddings,
    filename: str,
) -> None:
    """
    Summarize the given text, then upsert it into a FAISS vector store under faiss_db_dir.
    Creates the directory if it doesn't exist. Uses summary as the indexed text.

    Args:
        text (str): The full raw document text.
        faiss_db_dir (str): Path to the FAISS database folder.
        language_model (ChatOllama): Ollama-based LLM for summarization.
        embedding_model (OllamaEmbeddings): Ollama-based embeddings.
        filename (str): The source filename (used as metadata).
    """
    # Make sure the FAISS directory exists
    os.makedirs(faiss_db_dir, exist_ok=True)

    # Generate or fallback to raw text if summarization fails
    summary = summarize_text(text, language_model)
    if not summary or summary.strip().startswith("This document does not appear"):
        # If the doc is not about concerts or summarization failed, store the first 1000 chars
        summary = text[:1000]

    try:
        # If index already exists, load and add, otherwise create a new DB
        index_path = os.path.join(faiss_db_dir, "index.faiss")
        if os.path.exists(index_path):
            db = FAISS.load_local(
                faiss_db_dir,
                embedding_model,
                allow_dangerous_deserialization=True,
            )
            db.add_texts([summary], metadatas=[{"source": filename}])
        else:
            db = FAISS.from_texts(
                texts=[summary],
                embedding=embedding_model,
                metadatas=[{"source": filename}],
            )

        # Save updates back to disk
        db.save_local(faiss_db_dir)
        print(f"[ingest_document] Ingested '{filename}' successfully.")
    except Exception as e:
        print(f"[ingest_document] Error ingesting '{filename}': {e}")


def is_concert_related(
    text: str,
    language_model: ChatOllama = language_model,
) -> bool:
    """
    Check via the LLM if the given text is related to concerts, tours, venues, etc.

    Args:
        text (str): The raw text to check.
        language_model (ChatOllama): Ollama-based LLM. Defaults to the global instance.

    Returns:
        bool: True if related, False otherwise.
    """
    return is_concert_related_text(text, language_model)
