# NavigIA — Assistant Transports Île-de-France

Chatbot spécialisé dans les transports en commun français (SNCF, RATP, IDFM).  
Architecture Full Stack : React + Flask + RAG (ChromaDB) + LLM (OpenRouter) + Recherche web (Tavily).

---

## Prérequis

- **Python 3.9+**
- **Node.js 18+**
- Un compte gratuit sur [openrouter.ai](https://openrouter.ai) → pour le LLM
- Un compte gratuit sur [tavily.com](https://tavily.com) → pour la recherche web

---

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/Selma-mtch/TransportsChatbot.git
cd TransportsChatbot
```

---

### 2. Configurer le backend

```bash
cd backend
```

#### Créer l'environnement virtuel Python

> Le venv doit obligatoirement s'appeler `chatbot`

```bash
python3 -m venv chatbot
```

#### Installer les dépendances

```bash
chatbot/bin/pip install -r requirements.txt
```

> Sur Windows : `chatbot\Scripts\pip install -r requirements.txt`

#### Créer le fichier `.env`

```bash
cp .env.example .env
```

Puis ouvrir `.env` et renseigner :

```env
SECRET_KEY=une-chaine-aleatoire-longue
OPENROUTER_API_KEY=sk-or-v1-...   # Récupérer sur openrouter.ai → Keys
TAVILY_API_KEY=tvly-dev-...       # Récupérer sur tavily.com → API Keys
```

Les autres valeurs peuvent rester telles quelles.

#### Lancer le backend

```bash
chatbot/bin/python3 app.py
```

> Sur Windows : `chatbot\Scripts\python app.py`

Le backend démarre sur `http://localhost:5001`.  
**Au premier démarrage**, l'indexation RAG se lance automatiquement (~2 minutes). C'est normal.

---

### 3. Configurer le frontend

Dans un **nouveau terminal**, depuis la racine du projet :

```bash
cd frontend
npm install
npm run dev
```

Le frontend démarre sur `http://localhost:5173`.

---

### 4. Ouvrir l'application

Aller sur [http://localhost:5173](http://localhost:5173), créer un compte et commencer à discuter.

---

## Fonctionnalités

| Fonctionnalité | Description |
|---------------|-------------|
| 💬 Chat | Conversations persistantes avec historique |
| 📊 RAG | Données officielles SNCF/IDFM (tarifs, horaires, fréquentation, propreté) |
| 🌐 Recherche web | Résultats temps réel via Tavily si le RAG ne trouve pas |
| 🎤 Voix | Dictée vocale via Web Speech API (Chrome/Edge/Safari) |
| 🔐 Auth | Inscription / connexion sécurisée |

---

## Structure du projet

```
TransportsChatbot/
├── data/json/              ← Données SNCF/IDFM
├── backend/
│   ├── app.py              ← Point d'entrée Flask
│   ├── .env.example        ← Template de configuration
│   ├── requirements.txt    ← Dépendances Python
│   ├── core/               ← LLM, RAG, recherche web
│   ├── repositories/       ← Accès base de données
│   ├── services/           ← Logique métier
│   └── controllers/        ← Routes HTTP
└── frontend/
    └── src/
        ├── components/
        ├── pages/
        └── context/
```

---

## Problèmes fréquents

**Le backend ne démarre pas**
→ Vérifier que le venv s'appelle bien `chatbot` et que `.env` existe avec les clés API.

**L'indexation prend longtemps**
→ Normal au premier démarrage. Elle ne se refait pas aux démarrages suivants.

**Le bot répond "tous les modèles sont surchargés"**
→ Les modèles gratuits OpenRouter ont des limites. Réessayer dans 30 secondes.

**La dictée vocale ne fonctionne pas**
→ Uniquement disponible sur Chrome, Edge et Safari. Pas sur Firefox.
