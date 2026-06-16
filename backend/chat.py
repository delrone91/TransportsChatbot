from datetime import datetime, timezone
import requests
from flask import Blueprint, request, jsonify
from database import get_db
from models import ConversationSession, Message
from auth import require_auth
from rag import retrieve
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

# Instructions données au LLM pour qu'il se comporte comme TransportBot
# Ce prompt est envoyé à chaque requête pour cadrer les réponses
SYSTEM_PROMPT = (
    "Tu es TransportBot, un assistant spécialisé dans les transports en commun français, "
    "notamment la SNCF et le réseau Île-de-France Mobilités (RATP/IDFM).\n"
    "Tu aides les utilisateurs avec :\n"
    "- Les tarifs et titres de transport (Navigo, tickets, pass)\n"
    "- L'accessibilité dans les gares SNCF\n"
    "- Les équipements disponibles en gare\n"
    "- La fréquentation et la propreté des gares\n"
    "- Les horaires des gares SNCF\n\n"
    "Réponds toujours en français, de façon claire et concise. "
    "Si l'information n'est pas disponible dans le contexte fourni, dis-le honnêtement "
    "et oriente l'utilisateur vers les sites officiels (sncf.com, iledefrance-mobilites.fr)."
)


def call_llm(messages: list) -> str:
    # Si la clé API n'est pas configurée, on retourne un message d'aide
    if not OPENROUTER_API_KEY:
        return "⚠️ Clé API OpenRouter non configurée."
    try:
        resp = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'http://localhost:5173',
                'X-Title': 'TransportBot',
            },
            json={
                'model': OPENROUTER_MODEL,
                'messages': messages,
                'max_tokens': 1024,
                'temperature': 0.3,  # Valeur basse pour des réponses plus précises et moins créatives
            },
            timeout=60,
        )
        # Si OpenRouter renvoie une erreur, on affiche le détail pour déboguer
        if not resp.ok:
            detail = resp.text[:500]
            print(f"[OpenRouter] {resp.status_code}: {detail}")
            return f"❌ Erreur {resp.status_code} OpenRouter : {detail}"
        return resp.json()['choices'][0]['message']['content']
    except requests.exceptions.Timeout:
        return "⏱️ Le modèle met trop de temps à répondre. Réessayez."
    except Exception as e:
        return f"❌ Erreur lors de l'appel au modèle : {e}"


# Liste toutes les conversations de l'utilisateur connecté
@chat_bp.route('/sessions', methods=['GET'])
@require_auth
def list_sessions():
    user = request.current_user
    db = get_db()
    try:
        sessions = (
            db.query(ConversationSession)
            .filter_by(user_id=user.id)
            .order_by(ConversationSession.updated_at.desc())
            .all()
        )
        return jsonify([{
            'id': s.id,
            'title': s.title,
            'created_at': s.created_at.isoformat(),
            'updated_at': s.updated_at.isoformat(),
        } for s in sessions])
    finally:
        db.close()


# Crée une nouvelle session de conversation
@chat_bp.route('/sessions', methods=['POST'])
@require_auth
def create_session():
    user = request.current_user
    data = request.get_json() or {}
    db = get_db()
    try:
        session = ConversationSession(
            title=data.get('title', 'Nouvelle conversation'),
            user_id=user.id,
        )
        db.add(session)
        db.commit()
        return jsonify({
            'id': session.id,
            'title': session.title,
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat(),
        }), 201
    finally:
        db.close()


# Récupère une session avec tous ses messages (pour recharger une conversation)
@chat_bp.route('/sessions/<int:session_id>', methods=['GET'])
@require_auth
def get_session(session_id):
    user = request.current_user
    db = get_db()
    try:
        session = db.query(ConversationSession).filter_by(id=session_id, user_id=user.id).first()
        if not session:
            return jsonify({'error': 'Session introuvable'}), 404
        return jsonify({
            'id': session.id,
            'title': session.title,
            'messages': [{
                'id': m.id,
                'role': m.role,
                'content': m.content,
                'created_at': m.created_at.isoformat(),
            } for m in session.messages],
        })
    finally:
        db.close()


# Supprime une conversation et tous ses messages
@chat_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@require_auth
def delete_session(session_id):
    user = request.current_user
    db = get_db()
    try:
        session = db.query(ConversationSession).filter_by(id=session_id, user_id=user.id).first()
        if not session:
            return jsonify({'error': 'Session introuvable'}), 404
        db.delete(session)
        db.commit()
        return jsonify({'message': 'Conversation supprimée'})
    finally:
        db.close()


# Renomme une conversation
@chat_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@require_auth
def rename_session(session_id):
    user = request.current_user
    data = request.get_json() or {}
    db = get_db()
    try:
        session = db.query(ConversationSession).filter_by(id=session_id, user_id=user.id).first()
        if not session:
            return jsonify({'error': 'Session introuvable'}), 404
        if 'title' in data:
            session.title = data['title'][:200]
        db.commit()
        return jsonify({'id': session.id, 'title': session.title})
    finally:
        db.close()


# Envoie un message et récupère la réponse du bot
@chat_bp.route('/sessions/<int:session_id>/messages', methods=['POST'])
@require_auth
def send_message(session_id):
    user = request.current_user
    data = request.get_json() or {}
    user_content = data.get('content', '').strip()

    if not user_content:
        return jsonify({'error': 'Le message ne peut pas être vide'}), 400

    db = get_db()
    try:
        session = db.query(ConversationSession).filter_by(id=session_id, user_id=user.id).first()
        if not session:
            return jsonify({'error': 'Session introuvable'}), 404

        # On récupère l'historique AVANT d'ajouter le nouveau message
        history = list(session.messages)
        is_first_message = len(history) == 0

        # On utilise le premier message comme titre de la conversation
        if is_first_message:
            session.title = user_content[:60] + ('...' if len(user_content) > 60 else '')

        # Sauvegarde du message utilisateur
        user_msg = Message(role='user', content=user_content, session_id=session_id)
        db.add(user_msg)
        db.flush()

        # Étape RAG : on cherche les extraits les plus pertinents dans nos données
        context_docs = retrieve(user_content, n_results=5)
        context_text = "\n".join(f"- {doc}" for doc in context_docs) if context_docs else ""

        # On ajoute le contexte RAG au prompt système si on a trouvé des données utiles
        system_content = SYSTEM_PROMPT
        if context_text:
            system_content += f"\n\nContexte extrait des données SNCF/IDFM :\n{context_text}"

        # On construit la liste de messages à envoyer au LLM
        # (système + historique + nouveau message)
        llm_messages = [{'role': 'system', 'content': system_content}]
        for msg in history:
            llm_messages.append({'role': msg.role, 'content': msg.content})
        llm_messages.append({'role': 'user', 'content': user_content})

        # Appel au LLM via OpenRouter
        assistant_content = call_llm(llm_messages)

        # Sauvegarde de la réponse du bot
        assistant_msg = Message(role='assistant', content=assistant_content, session_id=session_id)
        db.add(assistant_msg)
        session.updated_at = datetime.now(timezone.utc)
        db.commit()

        return jsonify({
            'user_message': {'id': user_msg.id, 'role': 'user', 'content': user_content},
            'assistant_message': {'id': assistant_msg.id, 'role': 'assistant', 'content': assistant_content},
            'session_title': session.title,
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
