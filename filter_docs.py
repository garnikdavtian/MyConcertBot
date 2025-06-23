import os
import logging
from time import sleep 
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama

from llm_utils import summarize_text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def is_concert_related(text: str) -> bool:
    """
    Returns True if the document content is concert-related.
    This relies on the LLM summary indicating relevance.
    """
    try:
        model = ChatOllama(model="llama3")
        summary = summarize_text(text, model)
        return not summary.strip().startswith("This document does not appear to be concert-related.")
    except Exception as e:
        logging.error(f"Concert relevance check failed: {e}")
        return False
    

def is_concert_question(text: str) -> bool:
    """
    Returns True if the input is a concert-related user question.
    Uses LLM to classify based on semantics.
    """
    try:
        model = ChatOllama(model="llama3")

        prompt = f"""
You are a helpful assistant.

Determine whether the following user question is related to music concerts, live performances, tours, or ticket-related information.

Only respond with a single word: Yes or No.

Question: "{text}"
Answer:
"""
        response = model.invoke(prompt).content.strip().lower()
        return response.startswith("yes")

    except Exception as e:
        logging.error(f"Concert question classification failed: {e}")
        return False



def ingest_document(
    filepath: str,
    embedding_model: OllamaEmbeddings,
    faiss_db_dir: str,
) -> None:
    """
    Ingests a document into FAISS after summarizing its content.

    Args:
        filepath (str): Path to the uploaded document.
        embedding_model (OllamaEmbeddings): Embedding model.
        faiss_db_dir (str): Path to FAISS vector store.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Document not found: {filepath}")

    os.makedirs(faiss_db_dir, exist_ok=True)
    logging.info(f"Ingesting document: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    model = ChatOllama(model="llama3")
    summary = summarize_text(text, model)

    if not summary or summary.strip().startswith("This document does not appear to be concert-related."):
        logging.warning(f"Skipped ingestion — not concert-related: {filepath}")
        return

    # Create and persist FAISS vector DB
    vector_db = FAISS.from_texts([summary], embedding_model, metadatas=[{"source": filepath}])
    vector_db.save_local(faiss_db_dir)
    logging.info(f"Document ingested and indexed in FAISS: {filepath}")


