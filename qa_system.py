from typing import List
from langchain.vectorstores import FAISS
from online_lookup import search_artist_online
from filter_docs import is_concert_related
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings


def load_vector_db(
    faiss_db_dir: str,
    embedding_model: OllamaEmbeddings,
) -> FAISS:
    """
    Load an existing FAISS vector store from disk. Raises an error if not found.
    """
    return FAISS.load_local(
        faiss_db_dir, embedding_model, allow_dangerous_deserialization=True
    )


def format_online_result(user_question: str, online_result: str) -> str:
    """
    Format fallback online search results when the local DB has no answer.
    """
    return (
        f"ℹ️ I couldn't find relevant information in the local database, "
        f"but here's what I found online for **{user_question.strip()}**:\n\n"
        f"{online_result}\n\n🔗 More info may be available from official concert/ticket platforms."
    )


def answer_query(
    language_model: ChatOllama,
    faiss_db_dir: str,
    embedding_model: OllamaEmbeddings,
    user_question: str,
    top_k: int = 4,
) -> str:
    """
    Given a user question, first check if it’s concert-related (using LLM).
    If not, reply with a warning. Otherwise, retrieve top_k similar docs from FAISS.
    If no relevant context is found, do a live Google search as fallback.

    Returns a string answer (either from context or an online snippet).
    """
    # 1. Check if the question is about concerts
    if not is_concert_related(user_question, language_model):
        return "⚠️ I can only answer questions about concerts, tours, venues, performers, and related topics."

    # 2. Attempt to load the FAISS DB
    try:
        db = load_vector_db(faiss_db_dir, embedding_model)
    except Exception as e:
        print(f"[answer_query] Failed to load FAISS DB: {e}")
        # Fallback to an online search if the DB doesn’t exist
        fallback = search_artist_online(user_question)
        return format_online_result(user_question, fallback)

    # 3. Do a similarity search
    try:
        results = db.similarity_search(user_question, k=top_k)
    except Exception as e:
        print(f"[answer_query] Similarity search error: {e}")
        results = []

    # 4. Extract the content
    relevant_contexts: List[str] = [
        doc.page_content.strip() for doc in results if doc.page_content.strip()
    ]

    # 5. If no local context, fallback to online
    if not relevant_contexts:
        online_result = search_artist_online(user_question)
        return format_online_result(user_question, online_result)

    # 6. Construct the prompt with retrieved context
    context = "\n\n".join(relevant_contexts)
    prompt = f"""
You are a helpful assistant who only answers questions about concerts, tours, venues, performers, schedules, and related logistics.
Use ONLY the information from the context below to answer the question. 
If you cannot find relevant information in the context, respond EXACTLY with:
'I don't have any information about concerts related to your question.'

Context:
{context}

Question:
{user_question}

Answer:"""

    # 7. Invoke the LLM
    try:
        response = language_model.invoke(prompt)
        if hasattr(response, "content"):
            answer = response.content.strip()
        elif isinstance(response, dict) and "content" in response:
            answer = response["content"].strip()
        else:
            answer = str(response).strip()
    except Exception as e:
        print(f"[answer_query] LLM invocation error: {e}")
        return "❌ Error: Failed to generate answer from language model."

    # 8. If LLM says it has no info, fallback to online
    if answer.lower().startswith("i don't have any information about concerts"):
        online_result = search_artist_online(user_question)
        return (
            "I didn't find anything in the local database. "
            "Here's what I found online:\n\n" + online_result
        )

    return answer
