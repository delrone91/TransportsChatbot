# Dockerfile de deploiement pour Hugging Face Spaces (SDK Docker).
#
# Pourquoi cloner le repo plutot qu'un COPY local ?
# Le git de HF Spaces limite les fichiers a 10 Mo (sans LFS) et un de nos
# fichiers de donnees depasse 10 Mo. On recupere donc le code et les donnees
# depuis le repo GitHub public au moment du build.

FROM python:3.11-slim

# Outils necessaires au clone et a l'installation de certaines dependances
RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Recuperation du code + donnees depuis GitHub (repo public)
RUN git clone --depth 1 https://github.com/delrone91/TransportsChatbot.git .

# Dependances Python du backend
RUN pip install --no-cache-dir -r backend/requirements.txt

WORKDIR /app/backend

# Chemins inscriptibles pour le cache du modele, l'index RAG et les donnees
ENV HF_HOME=/app/backend/hf_cache \
    CHROMA_PATH=/app/backend/chroma_db \
    DATA_PATH=/app/data/json \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1

# Hugging Face Spaces attend l'application sur le port 7860
EXPOSE 7860

CMD ["gunicorn", "wsgi:app", "--workers", "1", "--threads", "4", "--timeout", "600", "--bind", "0.0.0.0:7860"]
