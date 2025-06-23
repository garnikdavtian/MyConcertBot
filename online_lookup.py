import os
import logging
from typing import Optional

from dotenv import load_dotenv
from serpapi import GoogleSearch

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def _get_serpapi_key() -> str:
    """
    Retrieve the SERPAPI_KEY from environment variables.
    Raise an error if not found.
    """
    key = os.getenv("SERPAPI_KEY")
    if not key:
        logging.error("[online_lookup] SERPAPI_KEY is not set. Online search will not work.")
        raise ValueError("Missing SERPAPI_KEY in environment. Set it before using online search.")
    return key


def search_artist_online(query: str, num_results: int = 5) -> str:
    """
    Perform a Google search using SerpAPI for artist-related queries.

    Args:
        query (str): User's question or search string.
        num_results (int): Number of top search results to return.

    Returns:
        str: Search results in Markdown format or error message.
    """
    try:
        api_key = _get_serpapi_key()
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "num": num_results
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        organic = results.get("organic_results", [])

        if not organic:
            logging.info("[online_lookup] No search results returned from SerpAPI.")
            return "🔎 No online results were found for your question."

        output = "🔎 Here's what I found online:\n\n"
        for i, result in enumerate(organic[:num_results], 1):
            title = result.get("title", "No title")
            link = result.get("link", "")
            snippet = result.get("snippet", "No description.")
            output += f"**{i}. [{title}]({link})**\n\n{snippet}\n\n"

        return output.strip()

    except Exception as e:
        logging.error(f"[online_lookup] Online search failed: {e}")
        return "❌ Error during online search. Please try again later."


def format_online_result(query: str, result: str) -> str:
    """
    Format the online search result with a user-friendly header.
    """
    return f"🌐 Here's what I found online about: **{query}**\n\n{result}"
