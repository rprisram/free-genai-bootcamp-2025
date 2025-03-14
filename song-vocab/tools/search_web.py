from typing import List, Dict
import asyncio
import random
from duckduckgo_search import AsyncDDGS

from duckduckgo_search import DDGS
import asyncio

async def search_web(query: str, lyrics_language: str = "english"):
    search_query = f"{query} lyrics in {lyrics_language}"
    
    # Use Tor Browser proxy
    def perform_search():
        with DDGS(proxy="tb", timeout=20) as ddgs:  # "tb" is an alias for Tor Browser proxy
            results = list(ddgs.text(search_query, max_results=5))
            # Format results
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append({
                    "index": i,
                    "title": result.get("title", ""),
                    "link": result.get("href", ""),
                    "snippet": result.get("body", "")
                })
                print(f"Formatted Result {i}: {result}")
            return formatted_results
    return await asyncio.to_thread(perform_search)




           