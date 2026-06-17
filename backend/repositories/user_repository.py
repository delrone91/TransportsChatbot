from __future__ import annotations
from models import User


class UserRepository:
    def __init__(self, db):
        self.db = db

    def find_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter_by(email=email).first()

    def find_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter_by(username=username).first()

    def create(self, username: str, email: str, password_hash: str) -> User:
        user = User(username=username, email=email, password_hash=password_hash)
        self.db.add(user)
        self.db.flush()
        return user
