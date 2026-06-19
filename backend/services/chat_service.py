from __future__ import annotations
from datetime import datetime
from repositories.chat_repository import ChatRepository
from core.rag import retrieve
from core.llm import call_llm
from core.search import web_search

SYSTEM_PROMPT = (
    "Tu es un assistant spécialisé dans le transport public en France. "
    "Tu réponds uniquement à partir du contexte fourni, qui peut venir de la base documentaire ou d'une recherche web officielle. "
    "Si l'information n'est pas présente dans le contexte, tu dis clairement que tu ne peux pas répondre avec certitude. "
    "Tu ne donnes pas d'horaires précis ni d'informations temps réel. "
    "Si le contexte vient du web, tu précises que la réponse s'appuie sur une source web. "
    "Réponds toujours en français de façon claire et structurée."
)


class ChatService:
    def __init__(self, db):
        self.repo = ChatRepository(db)

    def list_sessions(self, user_id: int) -> list[dict]:
        return [self._serialize_session(s) for s in self.repo.get_user_sessions(user_id)]

    def create_session(self, user_id: int, title: str = 'Nouvelle conversation') -> dict:
        return self._serialize_session(self.repo.create_session(user_id, title))

    def get_session(self, session_id: int, user_id: int) -> dict:
        session = self._get_or_404(session_id, user_id)
        return {
            'id': session.id,
            'title': session.title,
            'messages': [self._serialize_message(m) for m in session.messages],
        }

    def delete_session(self, session_id: int, user_id: int) -> None:
        session = self._get_or_404(session_id, user_id)
        self.repo.delete_session(session)
        self.repo.commit()

    def rename_session(self, session_id: int, user_id: int, title: str) -> dict:
        session = self._get_or_404(session_id, user_id)
        self.repo.update_session_title(session, title)
        self.repo.commit()
        return self._serialize_session(session)

    def send_message(self, session_id: int, user_id: int, content: str, use_web: bool = False) -> dict:
        content = content.strip()
        if not content:
            raise ValueError('Le message ne peut pas être vide')

        session = self._get_or_404(session_id, user_id)
        history = list(session.messages)

        if not history:
            self.repo.update_session_title(session, content[:60] + ('...' if len(content) > 60 else ''))

        user_msg = self.repo.add_message(session_id, 'user', content)
        self.repo.flush()

        context_docs, web_sources, source = self._resolve_context(content, use_web)
        llm_messages = self._build_llm_messages(history, content, context_docs)
        reply = call_llm(llm_messages)

        assistant_msg = self.repo.add_message(session_id, 'assistant', reply, source)
        self.repo.touch_session(session)
        self.repo.commit()

        return {
            'user_message': {'id': user_msg.id, 'role': 'user', 'content': content},
            'assistant_message': {
                'id': assistant_msg.id,
                'role': 'assistant',
                'content': reply,
                'source': source,
                'web_sources': web_sources,
                'rag_sources': [
                {
                    "source": doc.get("source"),
                    "type": doc.get("type"),
                    "score": doc.get("score"),
                }
                for doc in context_docs
            ] if source == "rag" else [],
            },
            'session_title': session.title,
        }

    def _resolve_context(self, query: str, use_web: bool) -> tuple[list, list, str | None]:
        if use_web:
            print(f"[Web] Recherche forcee : {query[:60]}")
            docs, sources = web_search(query)
            return docs, sources, 'web' if docs else None

        docs = retrieve(query, n_results=6)
        if docs:
            return docs, [], 'rag'

        print(f"[RAG] Aucun resultat, fallback web : {query[:60]}")
        docs, sources = web_search(query)
        return docs, sources, 'web' if docs else None

    def _build_llm_messages(self, history: list, user_content: str, context_docs: list) -> list:
        today = datetime.now().strftime("%d/%m/%Y")
        system = f"Nous sommes le {today}.\n\n{SYSTEM_PROMPT}"
        if context_docs:
            context_text = "\n".join(f"- {self._format_context_doc(doc)}" for doc in context_docs)
            system += f"\n\nContexte disponible :\n{context_text}"

        messages = [{'role': 'system', 'content': system}]
        for msg in history:
            messages.append({'role': msg.role, 'content': msg.content})
        messages.append({'role': 'user', 'content': user_content})
        return messages

    @staticmethod
    def _format_context_doc(doc) -> str:
        if isinstance(doc, dict):
            content = doc.get('content') or doc.get('text') or ''
            source = doc.get('source')
            if source:
                return f"{content} (source: {source})"
            return content
        return str(doc)

    def _get_or_404(self, session_id: int, user_id: int):
        session = self.repo.get_session(session_id, user_id)
        if not session:
            raise LookupError('Session introuvable')
        return session

    @staticmethod
    def _serialize_session(s) -> dict:
        return {
            'id': s.id,
            'title': s.title,
            'created_at': s.created_at.isoformat(),
            'updated_at': s.updated_at.isoformat(),
        }

    @staticmethod
    def _serialize_message(m) -> dict:
        return {
            'id': m.id,
            'role': m.role,
            'content': m.content,
            'source': m.source,
            'created_at': m.created_at.isoformat(),
        }
