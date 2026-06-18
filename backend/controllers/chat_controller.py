from flask import Blueprint, request, jsonify
from database import get_db
from services.chat_service import ChatService
from controllers.middleware import require_auth

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')


@chat_bp.route('/sessions', methods=['GET'])
@require_auth
def list_sessions():
    db = get_db()
    try:
        return jsonify(ChatService(db).list_sessions(request.current_user.id))
    finally:
        db.close()


@chat_bp.route('/sessions', methods=['POST'])
@require_auth
def create_session():
    data = request.get_json() or {}
    db = get_db()
    try:
        session = ChatService(db).create_session(
            request.current_user.id,
            data.get('title', 'Nouvelle conversation'),
        )
        return jsonify(session), 201
    finally:
        db.close()


@chat_bp.route('/sessions/<int:session_id>', methods=['GET'])
@require_auth
def get_session(session_id):
    db = get_db()
    try:
        return jsonify(ChatService(db).get_session(session_id, request.current_user.id))
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
    finally:
        db.close()


@chat_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@require_auth
def delete_session(session_id):
    db = get_db()
    try:
        ChatService(db).delete_session(session_id, request.current_user.id)
        return jsonify({'message': 'Conversation supprimée'})
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
    finally:
        db.close()


@chat_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@require_auth
def rename_session(session_id):
    data = request.get_json() or {}
    db = get_db()
    try:
        session = ChatService(db).rename_session(
            session_id,
            request.current_user.id,
            data.get('title', ''),
        )
        return jsonify(session)
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
    finally:
        db.close()


@chat_bp.route('/sessions/<int:session_id>/messages', methods=['POST'])
@require_auth
def send_message(session_id):
    data = request.get_json() or {}
    db = get_db()
    try:
        result = ChatService(db).send_message(
            session_id,
            request.current_user.id,
            data.get('content', ''),
            use_web=data.get('use_web', False),
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
