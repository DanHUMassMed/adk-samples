import glob
import os

from ddgs import DDGS
from typing import List, Dict
    
def duckduckgo_search_tool(query: str, max_results: int = 10) -> List[Dict]:
    """
    DuckDuckGo search returning only JSON-serializable dicts.
    """
    ddg = DDGS()
    results_gen = ddg.text(query, max_results=max_results)

    clean_results = []
    for r in results_gen:
        # Convert result to a sanitized dict
        clean_results.append({
            "title": r.get("title", ""),
            "href": r.get("href", ""),
            "snippet": r.get("body", ""),   # rename "body" to avoid conflicts
        })

    return clean_results