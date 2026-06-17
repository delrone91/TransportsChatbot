from flask import Blueprint, request, jsonify
from database import get_db
from services.auth_service import AuthService
from controllers.middleware import require_auth

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    db = get_db()
    try:
        result = AuthService(db).register(
            data.get('username', ''),
            data.get('email', ''),
            data.get('password', ''),
        )
        return jsonify(result), 201
    except ValueError as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    db = get_db()
    try:
        result = AuthService(db).login(
            data.get('email', ''),
            data.get('password', ''),
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except PermissionError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@auth_bp.route('/me', methods=['GET'])
@require_auth
def me():
    u = request.current_user
    return jsonify({'id': u.id, 'username': u.username, 'email': u.email})


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    token = request.headers.get('Authorization', '').removeprefix('Bearer ').strip()
    db = get_db()
    try:
        AuthService(db).logout(token)
        return jsonify({'message': 'Déconnecté avec succès'})
    finally:
        db.close()
