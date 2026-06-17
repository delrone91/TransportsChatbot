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

CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)


@app.route('/')
def health():
    return {'status': 'ok', 'message': 'NavigIA API en ligne'}


if __name__ == '__main__':
    init_db()
    print("Initialisation du système RAG...")
    load_and_index_data()
    port = int(os.getenv('PORT', 5001))
    print(f"Serveur prêt sur http://localhost:{port}")
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'true').lower() == 'true',
        host='0.0.0.0',
        port=port,
    )
