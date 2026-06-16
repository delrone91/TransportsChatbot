import secrets
from functools import wraps
from flask import Blueprint, request, jsonify
import bcrypt
from database import get_db
from models import User, AuthToken

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# Décorateur qu'on met sur les routes qui nécessitent d'être connecté
# Il vérifie que le token envoyé dans le header Authorization est valide
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').removeprefix('Bearer ').strip()
        if not token:
            return jsonify({'error': 'Token requis'}), 401
        db = get_db()
        try:
            auth_token = db.query(AuthToken).filter_by(token=token).first()
            if not auth_token:
                return jsonify({'error': 'Token invalide ou expiré'}), 401
            # On attache l'utilisateur à la requête pour pouvoir l'utiliser dans la route
            request.current_user = auth_token.user
            return f(*args, **kwargs)
        finally:
            db.close()
    return decorated


# Inscription d'un nouvel utilisateur
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'Tous les champs sont requis'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Mot de passe trop court (minimum 6 caractères)'}), 400

    db = get_db()
    try:
        # Vérification que l'email et le pseudo ne sont pas déjà pris
        if db.query(User).filter_by(email=email).first():
            return jsonify({'error': 'Cette adresse email est déjà utilisée'}), 409
        if db.query(User).filter_by(username=username).first():
            return jsonify({'error': "Ce nom d'utilisateur est déjà pris"}), 409

        # On hash le mot de passe avec bcrypt avant de le stocker
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = User(username=username, email=email, password_hash=pw_hash)
        db.add(user)
        db.flush()

        # On génère un token aléatoire et on le sauvegarde en base
        token = secrets.token_urlsafe(32)
        db.add(AuthToken(token=token, user_id=user.id))
        db.commit()

        return jsonify({
            'token': token,
            'user': {'id': user.id, 'username': user.username, 'email': user.email}
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


# Connexion d'un utilisateur existant
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email et mot de passe requis'}), 400

    db = get_db()
    try:
        user = db.query(User).filter_by(email=email).first()
        # On compare le mot de passe saisi avec le hash stocké
        if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401

        # Nouveau token à chaque connexion
        token = secrets.token_urlsafe(32)
        db.add(AuthToken(token=token, user_id=user.id))
        db.commit()

        return jsonify({
            'token': token,
            'user': {'id': user.id, 'username': user.username, 'email': user.email}
        })
    finally:
        db.close()


# Récupère les infos de l'utilisateur connecté (utile au chargement de la page)
@auth_bp.route('/me', methods=['GET'])
@require_auth
def me():
    u = request.current_user
    return jsonify({'id': u.id, 'username': u.username, 'email': u.email})


# Déconnexion : on supprime le token de la base pour l'invalider
@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    token = request.headers.get('Authorization', '').removeprefix('Bearer ').strip()
    db = get_db()
    try:
        db.query(AuthToken).filter_by(token=token).delete()
        db.commit()
        return jsonify({'message': 'Déconnecté avec succès'})
    finally:
        db.close()
