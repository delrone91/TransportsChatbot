from __future__ import annotations
from config import TAVILY_API_KEY


def web_search(query: str, max_results: int = 5) -> tuple[list[str], list[dict]]:
    """Recherche Tavily (Google). Retourne (chunks_pour_llm, sources_pour_ui)."""
    if not TAVILY_API_KEY:
        print("[Tavily] Clé API manquante")
        return [], []
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)
        resp = client.search(
            query=f"{query} France transports SNCF",
            max_results=max_results,
            search_depth="basic",
        )
        chunks, sources = [], []
        for r in resp.get('results', []):
            content = r.get('content', '') or ''
            title = r.get('title', '') or ''
            url = r.get('url', '') or ''
            if content:
                chunks.append(f"[{title}] {content}")
                sources.append({'title': title, 'url': url})
        print(f"[Tavily] {len(chunks)} résultats trouvés")
        return chunks, sources
    except Exception as e:
        print(f"[Tavily] erreur : {e}")
        return [], []
