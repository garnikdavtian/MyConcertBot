import os
from langchain.vectorstores import FAISS
from typing import Optional
from llm_utils import summarize_text, language_model


def is_concert_related(text, language_model):    
    prompt = (
        "Is the following text related to concerts, tours, venues, performers, schedules, or logistics? "
        "Reply only 'yes' or 'no'.\n\n"
        f"{text}"
    )
    response = language_model.invoke(prompt)
    response_text = response.content if hasattr(response, 'content') else str(response)
    print(f"LLM Response: {response_text}")
    return "yes" in response_text.lower()


def ingest_document(text, faiss_db_dir, language_model, embedding_model, filename):
    summary_text = summarize_text(text, language_model)
    if not summary_text:
        summary_text = text[:1000]  # fallback


    if os.path.exists(faiss_db_dir) and os.path.exists(os.path.join(faiss_db_dir, "index.faiss")):
        db = FAISS.load_local(faiss_db_dir, embedding_model, allow_dangerous_deserialization=True)
        db.add_texts(texts=[summary_text], metadatas=[{"source": filename}])
    else:
        db = FAISS.from_texts([summary_text], embedding=embedding_model, metadatas=[{"source": filename}])

    db.add_texts(texts=[summary_text], metadatas=[{"source": filename}])
    db.save_local(faiss_db_dir)
    print("📦 Ingested and stored successfully.")
