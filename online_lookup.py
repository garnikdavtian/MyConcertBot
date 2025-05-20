from serpapi import GoogleSearch
import os


def search_artist_online(query: str) -> str:
    params = {
        "engine": "google",
        "q": query,
        "api_key": os.getenv("SERPAPI_KEY")
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        snippets = []
        for result in results.get("organic_results", [])[:5]:
            snippet = result.get("snippet")
            if snippet:
                snippets.append(snippet)

        if not snippets:
            return "No online information found."

        return "\n\n".join(snippets)

    except Exception as e:
        return f"Error during online search: {e}"