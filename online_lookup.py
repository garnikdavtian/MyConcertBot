from serpapi import GoogleSearch
import os
from typing import List, Optional


def _get_serpapi_key() -> Optional[str]:
    """
    Retrieve the SERPAPI_KEY from environment variables. Returns None if not found.
    """
    key = os.getenv("SERPAPI_KEY")
    if not key:
        print("[online_lookup] Warning: SERPAPI_KEY not set in environment.")
    return key


def search_artist_online(query: str, num_results: int = 5) -> str:
    """
    Perform a live Google search (via SerpAPI) for the given query
    and return the top snippets in Markdown format.

    Args:
        query (str): The search query (e.g., an artist name).
        num_results (int): How many top organic results to return. Defaults to 5.

    Returns:
        str: Markdown-formatted search results or an error message.
    """
    api_key = _get_serpapi_key()
    if not api_key:
        return "Error: SERPAPI_KEY environment variable is missing."

    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        organic = results.get("organic_results", [])
        if not organic:
            return "No online information found."

        snippets: List[str] = []
        for result in organic[:num_results]:
            title = result.get("title", "No title")
            link = result.get("link", "#")
            snippet = result.get("snippet", "")
            # Format as Markdown link + snippet
            formatted = f"🔗 **[{title}]({link})**\n> {snippet}"
            snippets.append(formatted)

        return "\n\n".join(snippets)

    except Exception as e:
        return f"Error during online search: {e}"
