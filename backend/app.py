import os
from flask import Flask
from flask_cors import CORS
from config import SECRET_KEY
from database import init_db
from core.rag import load_and_index_data
from controllers.auth_controller import auth_bp
from controllers.chat_controller import chat_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

# CORS : en prod, restreindre aux origines autorisées via CORS_ORIGINS
# (URLs séparées par des virgules). Par défaut "*" pour le développement.
cors_origins = [o.strip() for o in os.getenv('CORS_ORIGINS', '*').split(',')]
CORS(app, resources={r"/*": {"origins": cors_origins}})

app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)


@app.route('/')
def health():
    return {'status': 'ok', 'message': 'NavigIA API en ligne'}


def initialize():
    """Crée la base de données et construit l'index RAG.

    Appelée par le bloc __main__ (dev local : `python app.py`) et par
    wsgi.py (prod : `gunicorn wsgi:app`), car gunicorn importe le module
    sans exécuter le bloc __main__.
    """
    init_db()
    print("Initialisation du système RAG...")
    load_and_index_data()


if __name__ == '__main__':
    initialize()
    port = int(os.getenv('PORT', 5001))
    print(f"Serveur prêt sur http://localhost:{port}")
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'true').lower() == 'true',
        host='0.0.0.0',
        port=port,
    )
