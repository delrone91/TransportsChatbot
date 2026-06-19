from __future__ import annotations
from urllib.parse import urlparse
from config import TAVILY_API_KEY

TRUSTED_DOMAINS = {
    'sncf.com',
    'www.sncf.com',
    'transilien.com',
    'www.transilien.com',
    'iledefrance-mobilites.fr',
    'www.iledefrance-mobilites.fr',
    'ratp.fr',
    'www.ratp.fr',
    'service-public.fr',
    'www.service-public.fr',
}


def _is_trusted_source(url: str) -> bool:
    hostname = urlparse(url).hostname or ''
    return hostname.lower() in TRUSTED_DOMAINS


def web_search(query: str, max_results: int = 5) -> tuple[list[str], list[dict]]:
    """Recherche web limitee aux sites officiels utiles au projet."""
    if not TAVILY_API_KEY:
        print("[Tavily] Cle API manquante")
        return [], []

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=TAVILY_API_KEY)
        resp = client.search(
            query=(
                f"{query} "
                "site:sncf.com OR site:transilien.com OR "
                "site:iledefrance-mobilites.fr OR site:ratp.fr"
            ),
            max_results=max_results * 2,
            search_depth="basic",
        )

        chunks, sources = [], []
        for result in resp.get('results', []):
            content = result.get('content', '') or ''
            title = result.get('title', '') or ''
            url = result.get('url', '') or ''

            if not content or not _is_trusted_source(url):
                continue

            chunks.append(f"[{title}] {content}")
            sources.append({'title': title, 'url': url})

            if len(chunks) >= max_results:
                break

        print(f"[Tavily] {len(chunks)} resultats fiables trouves")
        return chunks, sources
    except Exception as e:
        print(f"[Tavily] erreur : {e}")
        return [], []
