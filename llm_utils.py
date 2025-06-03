from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from typing import Optional, Union

language_model = ChatOllama(model="llama3")


def summarize_text(text: str, language_model: ChatOllama) -> Optional[str]:
    """
    Summarize a chunk of text (specifically focused on concert-related documents)
    into 3–4 sentences using the provided LLM. If the document is unrelated to concerts,
    returns exactly "This document does not appear to be concert-related.".

    Args:
        text (str): The raw document text.
        language_model (ChatOllama): An instance of the Ollama-based chat model.

    Returns:
        Optional[str]: The summary (3–4 sentences) or None if something goes wrong.
    """
    prompt = f"""
You are a helpful assistant that summarizes concert tour documents.
Summarize the content below into 3–4 sentences.

If the content is not related to concerts, tours, schedules, venues, or performers,
respond exactly with:
"This document does not appear to be concert-related."

Document:
{text}

Summary:"""

    try:
        response = language_model.invoke(prompt)
        # Depending on how ChatOllama returns, pull out “content”
        if hasattr(response, "content"):
            return response.content.strip()
        elif isinstance(response, dict) and "content" in response:
            return response["content"].strip()
        else:
            return None
    except Exception as e:
        # Log the exception somewhere or print it for debugging
        print(f"[summarize_text] Exception: {e}")
        return None


def is_concert_related_text(text: str, language_model: ChatOllama) -> bool:
    """
    Ask the LLM whether a given text is concert-related (venues, performers, tours, etc.).
    Returns True if the LLM says “yes”.

    Args:
        text (str): The raw text to classify.
        language_model (ChatOllama): An instance of the Ollama-based chat model.

    Returns:
        bool: True if the LLM answers “yes”, False otherwise.
    """
    prompt = (
        "Is the following text related to concerts, tours, venues, performers, schedules, or logistics? "
        "Reply only 'yes' or 'no'.\n\n"
        f"{text}"
    )
    try:
        response = language_model.invoke(prompt)
        response_text = ""
        if hasattr(response, "content"):
            response_text = response.content
        elif isinstance(response, dict) and "content" in response:
            response_text = response["content"]
        else:
            response_text = str(response)
        print(f"[is_concert_related_text] LLM Response: {response_text}")
        return "yes" in response_text.lower()
    except Exception as e:
        print(f"[is_concert_related_text] Exception: {e}")
        return False
