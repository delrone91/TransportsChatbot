from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


def _now():
    # Retourne l'heure actuelle en UTC pour horodater les enregistrements
    return datetime.now(timezone.utc)


# Table des utilisateurs
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)  # On ne stocke jamais le mot de passe en clair
    created_at = Column(DateTime, default=_now)

    # Un utilisateur peut avoir plusieurs sessions et plusieurs tokens
    sessions = relationship('ConversationSession', back_populates='user', cascade='all, delete-orphan')
    tokens = relationship('AuthToken', back_populates='user', cascade='all, delete-orphan')


# Table des tokens d'authentification
# Chaque connexion génère un nouveau token, stocké ici
class AuthToken(Base):
    __tablename__ = 'auth_tokens'
    id = Column(Integer, primary_key=True)
    token = Column(String(256), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='tokens')

    # Index sur le token pour que les recherches soient rapides
    __table_args__ = (Index('ix_auth_tokens_token', 'token'),)


# Table des sessions de conversation (chaque "chat" est une session)
class ConversationSession(Base):
    __tablename__ = 'conversation_sessions'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False, default='Nouvelle conversation')
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='sessions')

    # Les messages sont ordonnés par id pour garder l'ordre chronologique
    messages = relationship(
        'Message', back_populates='session',
        cascade='all, delete-orphan',
        order_by='Message.id'
    )


# Table des messages échangés dans une session
class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    role = Column(String(20), nullable=False)  # 'user' pour l'humain, 'assistant' pour le bot
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_now)
    session_id = Column(Integer, ForeignKey('conversation_sessions.id'), nullable=False)
    session = relationship('ConversationSession', back_populates='messages')
