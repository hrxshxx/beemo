from __future__ import annotations
from ddgs import DDGS


def web_search(query: str, max_results: int = 4) -> list[dict]:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return [{'title': r['title'], 'snippet': r['body'], 'url': r['href']} for r in results]
    except Exception:
        return []
