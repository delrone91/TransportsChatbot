# KitchenChatbot 🍳🤖

![CI](https://github.com/Selma-mtch/KitchenChatbot/actions/workflows/ci.yml/badge.svg)

Chatbot spécialisé dans le domaine de la cuisine utilisant une architecture Full Stack avec React, Flask et une approche RAG (Retrieval-Augmented Generation).

# 📁 Structure du projet

```bash
KitchenChatbot/
│
├── backend/
│   ├── app.py                 # Point d'entrée Flask
│   ├── chatbot/               # Environnement virtuel Python
│   ├── db/                    # Base de données
│   ├── models/                # Modèles SQLAlchemy
│   ├── rag/                   # Logique RAG
│   ├── routes/                # Routes API Flask
│   ├── services/              # Services métier
│   └── requirements.txt       # Dépendances Python
│
├── frontend/
│   ├── public/
│   ├── src/                   # Code source React
│   ├── package.json
│   └── vite.config.js
│   
│
├── data/                      # PDFs / documents culinaires
│
├── .gitignore
├── package.json
└── README.md
```

---

# ⚙️ Installation du projet

## 1️⃣ Cloner le projet

```bash
git clone git@github.com:Selma-mtch/KitchenChatbot.git
```

Puis :

```bash
cd KitchenChatbot
```

---

# 🐍 Backend - Flask

## 2️⃣ Aller dans le dossier backend

```bash
cd backend
```

---

## 3️⃣ Créer l’environnement virtuel Python

```bash
python3 -m venv chatbot
```

---

## 4️⃣ Activer l’environnement virtuel

### Linux / WSL

```bash
source chatbot/bin/activate
```

### Windows

```bash
chatbot\\Scripts\\activate
```

Le terminal doit afficher :

```bash
(chatbot)
```

---

## 5️⃣ Installer les dépendances Python

```bash
pip install -r requirements.txt
```

---

## 6️⃣ Lancer le backend Flask

```bash
python app.py
```

Backend disponible sur :

```txt
http://127.0.0.1:5000
```

---

# ⚛️ Frontend - React

## 7️⃣ Ouvrir un nouveau terminal

Depuis la racine du projet :

```bash
cd frontend
```

---

## 8️⃣ Installer les dépendances NodeJS

```bash
npm install
```

---

## 9️⃣ Lancer le frontend React

```bash
npm run dev
```

Frontend disponible sur :

```txt
http://localhost:5173
```
---

# 🔥 Workflow de développement

## ▶️ Workflow recommandé

1. Lancer le backend Flask
2. Lancer le frontend React
3. Développer les routes API Flask
4. Connecter React ↔ Flask
5. Ajouter le système RAG
6. Tester les fonctionnalités

---

# 🧠 Fonctionnalités prévues

## 🔐 Authentification

- Création de compte
- Connexion utilisateur
- Gestion des sessions

---

## 💬 Chatbot

- Discussions style ChatGPT
- Historique des conversations
- Suppression des conversations
- Création de nouvelles sessions

---

## 🍳 Domaine spécialisé : Cuisine

- Questions culinaires
- Conseils recettes
- Techniques de cuisine
- Recherche d’informations dans les documents

---

## 🧠 Intelligence Artificielle

- Intégration d’un LLM
- Système RAG
- Embeddings HuggingFace
- Recherche contextuelle

---

## 🌍 Recherche web (option bonus)

- Recherche internet via DuckDuckGo
- Complément d’informations externes

---

## 🎤 Option voix

- Transcription audio avec Whisper
- Interaction vocale utilisateur

---

# 📦 Dépendances principales

## 🐍 Backend

```txt
Flask
Flask-CORS
SQLAlchemy
LangChain
ChromaDB
sentence-transformers
transformers
```

---

## ⚛️ Frontend

```txt
ReactJS
Vite
Axios
```

---

# 🛠️ Commandes utiles

## ▶️ Activer le venv Python

```bash
source chatbot/bin/activate
```

---

## ⛔ Désactiver le venv

```bash
deactivate
```

---

## 📦 Installer une nouvelle dépendance Python

```bash
pip install nom_du_package
```

Puis mettre à jour :

```bash
pip freeze > requirements.txt
```

---

## 📦 Installer une dépendance React

```bash
npm install nom-du-package
```

---

## 🔄 Réinstaller les dépendances frontend

```bash
rm -rf node_modules
npm install
```

---

## 🚀 Lancer le frontend

```bash
npm run dev
```

---

## 🚀 Lancer le backend

```bash
python app.py
```

---

## 📋 Vérifier les fichiers suivis par Git

```bash
git status
```

---

## 📤 Push sur GitHub

```bash
git add .
git commit -m "message"
git push
```
