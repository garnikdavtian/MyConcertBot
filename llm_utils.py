from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from typing import Optional

language_model = ChatOllama(model="llama3")

def summarize_text(text: str, language_model) -> Optional[str]:
    prompt = f"""
    Summarize the following concert tour document in 3-4 sentences. Focus on dates, performers, venues, and logistics.

    Document:
    {text}

    Summary:"""

    response = language_model.invoke(prompt)
    if hasattr(response, "content"):
        return response.content.strip()
    elif isinstance(response, dict) and "content" in response:
        return response["content"].strip()
    return None


