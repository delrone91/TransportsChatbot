from __future__ import annotations
from datetime import datetime, timezone
from models import ConversationSession, Message


class ChatRepository:
    def __init__(self, db):
        self.db = db

    def get_user_sessions(self, user_id: int) -> list:
        return (
            self.db.query(ConversationSession)
            .filter_by(user_id=user_id)
            .order_by(ConversationSession.updated_at.desc())
            .all()
        )

    def get_session(self, session_id: int, user_id: int) -> ConversationSession | None:
        return self.db.query(ConversationSession).filter_by(id=session_id, user_id=user_id).first()

    def create_session(self, user_id: int, title: str = 'Nouvelle conversation') -> ConversationSession:
        session = ConversationSession(title=title, user_id=user_id)
        self.db.add(session)
        self.db.commit()
        return session

    def update_session_title(self, session: ConversationSession, title: str) -> None:
        session.title = title[:200]

    def touch_session(self, session: ConversationSession) -> None:
        session.updated_at = datetime.now(timezone.utc)

    def delete_session(self, session: ConversationSession) -> None:
        self.db.delete(session)

    def add_message(self, session_id: int, role: str, content: str, source: str | None = None) -> Message:
        msg = Message(role=role, content=content, session_id=session_id, source=source)
        self.db.add(msg)
        return msg

    def flush(self) -> None:
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
