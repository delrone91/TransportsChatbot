from __future__ import annotations
import secrets
import bcrypt
from repositories.user_repository import UserRepository
from repositories.auth_repository import AuthRepository


class AuthService:
    def __init__(self, db):
        self.user_repo = UserRepository(db)
        self.auth_repo = AuthRepository(db)
        self.db = db

    def register(self, username: str, email: str, password: str) -> dict:
        username = username.strip()
        email = email.strip().lower()

        if not username or not email or not password:
            raise ValueError('Tous les champs sont requis')
        if len(password) < 6:
            raise ValueError('Mot de passe trop court (minimum 6 caractères)')
        if self.user_repo.find_by_email(email):
            raise ValueError('Cette adresse email est déjà utilisée')
        if self.user_repo.find_by_username(username):
            raise ValueError("Ce nom d'utilisateur est déjà pris")

        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = self.user_repo.create(username, email, pw_hash)

        token = secrets.token_urlsafe(32)
        self.auth_repo.create(token, user.id)
        self.db.commit()

        return {'token': token, 'user': {'id': user.id, 'username': user.username, 'email': user.email}}

    def login(self, email: str, password: str) -> dict:
        email = email.strip().lower()

        if not email or not password:
            raise ValueError('Email et mot de passe requis')

        user = self.user_repo.find_by_email(email)
        if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            raise PermissionError('Email ou mot de passe incorrect')

        token = secrets.token_urlsafe(32)
        self.auth_repo.create(token, user.id)
        self.db.commit()

        return {'token': token, 'user': {'id': user.id, 'username': user.username, 'email': user.email}}

    def validate_token(self, token: str):
        auth_token = self.auth_repo.find_by_token(token)
        if not auth_token:
            raise PermissionError('Token invalide ou expiré')
        return auth_token.user

    def logout(self, token: str) -> None:
        self.auth_repo.delete_by_token(token)
        self.db.commit()
