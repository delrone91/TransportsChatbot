import requests
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL

FALLBACK_MODELS = [
    'openai/gpt-oss-120b:free',
    OPENROUTER_MODEL,
    'liquid/lfm-2.5-1.2b-instruct:free',
    'nvidia/nemotron-3-super-120b-a12b:free',
    'qwen/qwen3-next-80b-a3b-instruct:free',
]


def call_llm(messages: list) -> str:
    if not OPENROUTER_API_KEY:
        return "⚠️ Clé API OpenRouter non configurée."

    for model in FALLBACK_MODELS:
        try:
            resp = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'http://localhost:5173',
                    'X-Title': 'NavigIA',
                },
                json={
                    'model': model,
                    'messages': messages,
                    'max_tokens': 1024,
                    'temperature': 0.3,
                },
                timeout=60,
            )
            if resp.status_code == 429:
                print(f"[OpenRouter] {model} rate-limité, modèle suivant...")
                continue
            if not resp.ok:
                print(f"[OpenRouter] {model} — {resp.status_code}: {resp.text[:300]}")
                continue
            return resp.json()['choices'][0]['message']['content']
        except requests.exceptions.Timeout:
            print(f"[OpenRouter] {model} timeout, modèle suivant...")
        except Exception as e:
            print(f"[OpenRouter] {model} erreur : {e}")

    return "⏱️ Tous les modèles sont temporairement surchargés. Réessayez dans quelques secondes."
