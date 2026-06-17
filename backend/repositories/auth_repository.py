from __future__ import annotations
from models import AuthToken


class AuthRepository:
    def __init__(self, db):
        self.db = db

    def find_by_token(self, token: str) -> AuthToken | None:
        return self.db.query(AuthToken).filter_by(token=token).first()

    def create(self, token: str, user_id: int) -> AuthToken:
        auth_token = AuthToken(token=token, user_id=user_id)
        self.db.add(auth_token)
        return auth_token

    def delete_by_token(self, token: str) -> None:
        self.db.query(AuthToken).filter_by(token=token).delete()
