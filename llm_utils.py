import logging
from typing import Optional

from langchain_community.chat_models import ChatOllama

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the global language model instance
language_model = ChatOllama(model="llama3")


def summarize_text(text: str, language_model: ChatOllama) -> Optional[str]:
    """
    Summarize the given text into 1-2 sentences with a concert-specific focus.

    If the document does not relate to concerts or music events,
    the function returns a predefined rejection message.

    Args:
        text (str): Full input document content.
        language_model (ChatOllama): Ollama-based LLM instance.

    Returns:
        Optional[str]: A summary or specific rejection message.
    """
    prompt = f"""
Extract only the technical event details from the following concert-related text. Include the following fields only if they appear explicitly or implicitly in the text (e.g., inferred from date formats or phrases like "tickets start at..."):

- Event name:
- Artist/Band:
- Venue:
- City/Country:
- Date:
- Time:
- Ticket price(s):
- Age restriction:
- Ticket link:

If the document contains vague or partial information (e.g., "returning in 2026", "concert in London this summer"), include the field with that phrasing.

Return your answer as a bullet list in this exact format, AND LEAVE OUT ONLY THE LINES THAT ARE ABSOLUTELY NOT MENTIONED.
Do not explain or comment. Do not mention speculation.

If the text is not related to music events, reply with exactly:
"This document does not appear to be concert-related."

Text:
{text.strip()}
"""
    try:
        result = language_model.invoke(prompt)
        return result.content.strip()
    except Exception as e:
        logging.error(f"Summarization error: {e}")
        return None
