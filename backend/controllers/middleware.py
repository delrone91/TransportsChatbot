from functools import wraps
from flask import request, jsonify
from database import get_db
from services.auth_service import AuthService


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').removeprefix('Bearer ').strip()
        if not token:
            return jsonify({'error': 'Token requis'}), 401
        db = get_db()
        try:
            request.current_user = AuthService(db).validate_token(token)
            return f(*args, **kwargs)
        except PermissionError as e:
            return jsonify({'error': str(e)}), 401
        finally:
            db.close()
    return decorated
