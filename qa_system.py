from langchain.vectorstores import FAISS
from online_lookup import search_artist_online

def load_vector_db(faiss_db_dir, embedding_model):
    return FAISS.load_local(faiss_db_dir, embedding_model, allow_dangerous_deserialization=True)


def answer_query(language_model, faiss_db_dir, embedding_model, user_question: str, top_k: int = 4) -> str:
    db = load_vector_db(faiss_db_dir, embedding_model)
    results = db.similarity_search(user_question, k=top_k)

    context = "\n\n".join([doc.page_content for doc in results if doc.page_content.strip()])

    prompt = f"""You are a helpful assistant who only answers questions about concerts, tours, venues, performers, schedules, and related logistics.
Use ONLY the information from the context below to answer the question.
If you cannot find relevant information in the context, respond EXACTLY with:
'I don't have any information about concerts related to your question.'

Context:
{context}

Question:
{user_question}

Answer:"""

    response = language_model.invoke(prompt)
    if hasattr(response, "content"):
        answer = response.content.strip()
    elif isinstance(response, dict) and "content" in response:
        answer = response["content"].strip()
    else:
        answer = str(response).strip()

    if answer == "I don't have any information about concerts related to your question.":
        online_result = search_artist_online(user_question)
        return f"I didn't find anything in the local database. Here's what I found online:\n\n{online_result}"

    return answer


