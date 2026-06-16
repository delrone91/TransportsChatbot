from flask import Flask
from flask_cors import CORS
from config import SECRET_KEY
from database import init_db
from rag import load_and_index_data
from auth import auth_bp
from chat import chat_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

# On autorise les requêtes venant du frontend React (port 5173)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

# Enregistrement des routes d'authentification et de chat
app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)


# Route simple pour vérifier que le serveur tourne bien
@app.route('/')
def health():
    return {'status': 'ok', 'message': 'TransportBot API en ligne'}


if __name__ == '__main__':
    # Création des tables en base de données si elles n'existent pas encore
    init_db()

    # Chargement et indexation des données SNCF/IDFM pour le RAG
    print("Initialisation du système RAG...")
    load_and_index_data()

    print("Serveur prêt sur http://localhost:5000")
    app.run(debug=True, port=5000)
