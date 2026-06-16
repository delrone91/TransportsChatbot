import os
from dotenv import load_dotenv

# On charge les variables d'environnement depuis le fichier .env
# Comme ça on ne met pas les clés API directement dans le code
load_dotenv()

# Clé pour accéder à OpenRouter (le service qui nous donne accès aux LLMs)
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')

# Le modèle de langage qu'on utilise pour générer les réponses
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'openrouter/auto:free')

# Base de données SQLite, stockée localement dans le dossier backend
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///chatbot.db')

# Clé secrète Flask pour sécuriser les sessions
SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')

# Dossier où ChromaDB sauvegarde la base vectorielle (pour le RAG)
CHROMA_PATH = os.getenv('CHROMA_PATH', './chroma_db')

# Chemin vers les fichiers JSON contenant les données SNCF/IDFM
DATA_PATH = os.getenv('DATA_PATH', '../data/json')
