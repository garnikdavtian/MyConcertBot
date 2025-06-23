import os
import logging  
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
import traceback
from online_lookup import search_artist_online, format_online_result
from filter_docs import is_concert_question

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_vector_db(faiss_db_dir: str, embedding_model: OllamaEmbeddings) -> FAISS:
    """
    Load the FAISS vector database from disk.
    Throws an error if the directory is missing or empty.
    """
    if not os.path.exists(faiss_db_dir) or not os.listdir(faiss_db_dir):
        logging.warning(f"FAISS directory '{faiss_db_dir}' is empty or does not exist.")
        raise FileNotFoundError(f"FAISS database not found at '{faiss_db_dir}'")

    return FAISS.load_local(
        faiss_db_dir,
        embedding_model,
        allow_dangerous_deserialization=True
    )


def format_online_result(user_question: str, online_result: str) -> str:
    """
    Format fallback answer from online search.
    """
    if "No online information found" in online_result or "Error during online search" in online_result:
        return f"ℹ️ I couldn't find relevant information in the local database or online for **{user_question.strip()}**."

    return f"🔎 Here's what I found online for **{user_question.strip()}**:\n\n{online_result.strip()}"


def answer_query(
    user_question: str,
    embedding_model,
    faiss_db_dir: str,
) -> str:
    """
    Answer concert-related questions using FAISS + LLM.
    Fallback to SerpAPI if needed. Reject unrelated questions with few words only.
    """

def answer_query(user_question: str, embedding_model, faiss_db_dir: str) -> str:
    try:
        if not is_concert_question(user_question):
            logging.info("Rejected non-concert-related question.")
            return "🎤 I'm designed to answer only concert-related questions like tour dates, ticket info, or performances."
        
        db = FAISS.load_local(faiss_db_dir, embedding_model, allow_dangerous_deserialization=True)
        retriever = db.as_retriever(
            search_type="similarity_score_threshold", 
            search_kwargs={"score_threshold": 0.6, "k": 5}
        )
        docs = retriever.invoke(user_question)
        MIN_CONTENT_LENGTH = 30
        relevant_docs = [doc for doc in docs if len(doc.page_content.strip()) > MIN_CONTENT_LENGTH]

        if not relevant_docs:
            logging.info("❌ FAISS returned no relevant content. Fallback to online search.")
            online = search_artist_online(user_question)
            return format_online_result(user_question, online)

        llm = ChatOllama(model="llama3")
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=False,
        )

        response = qa_chain.invoke({"query": user_question})["result"]

        if response and len(response.strip()) > 10 and "don't know" not in response.lower():
            return response
        else:
            logging.info("⚠️ LLM gave weak answer. Fallback to online.")
            online = search_artist_online(user_question)
            return format_online_result(user_question, online)
                
    except Exception as e:
        logging.error(f"[qa_system] RAG error: {e}")
        traceback.print_exc()
        try:
            online = search_artist_online(user_question)
            return format_online_result(user_question, online)
        except Exception as fallback_error:
            logging.error(f"[qa_system] Fallback failed: {fallback_error}")
            return "❌ Both local and online search failed. Try again later."
