# NavigIA - Assistant transports Ile-de-France

NavigIA est une application full stack de chatbot specialise dans les transports en commun en France, avec un focus sur les donnees SNCF, Transilien, RATP et Ile-de-France Mobilites.

Le projet combine une interface React, une API Flask, une base SQLite, un pipeline RAG avec LangChain et ChromaDB, et un LLM appele via OpenRouter.

## Architecture

```text
React / Vite
    |
API Flask
    |
SQLAlchemy + SQLite
    |
LangChain + ChromaDB + Hugging Face Embeddings
    |
OpenRouter
```

Technologies principales :

| Partie | Technologie |
| --- | --- |
| Frontend | React, Vite, react-markdown, remark-gfm |
| Backend | Flask, Flask-CORS |
| Base applicative | SQLite, SQLAlchemy |
| RAG | LangChain, ChromaDB |
| Embeddings | Hugging Face, `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| LLM | OpenRouter |
| Recherche web | Tavily, limitee aux sources fiables |

## Fonctionnalites

| Fonctionnalite | Description |
| --- | --- |
| Authentification | Inscription et connexion utilisateur |
| Sessions | Creation, liste, renommage et suppression de conversations |
| Historique | Sauvegarde des messages utilisateur et assistant |
| Chatbot RAG | Recherche dans une base documentaire locale avant generation |
| Sources | Affichage des sources RAG et web utilisees |
| Fallback web | Recherche web si le RAG ne trouve pas de contexte pertinent |
| Markdown | Affichage lisible des listes et tableaux dans les reponses |

## Donnees utilisees

Les donnees locales sont stockees dans :

```text
data/json/
```

Elles contiennent notamment :

- titres et tarifs Ile-de-France Mobilites ;
- horaires de gares SNCF ;
- frequentation des gares SNCF ;
- equipements d'accessibilite SNCF ;
- donnees de proprete en gare.

Le projet n'utilise pas de donnees GTFS.

## RAG avec LangChain

Le pipeline RAG est implemente dans :

```text
backend/core/rag.py
```

Il fait les etapes suivantes :

1. Chargement des fichiers JSON.
2. Transformation des lignes en objets `Document` LangChain.
3. Ajout de metadonnees : source, type de document, identifiant.
4. Generation d'embeddings avec Hugging Face.
5. Stockage des vecteurs dans ChromaDB.
6. Recherche des documents pertinents pour chaque question.
7. Envoi du contexte recupere au LLM via OpenRouter.

Des aliases sont ajoutes pour ameliorer la recherche. Exemple :

```text
Forfait Navigo Mois
→ forfait Navigo mensuel
→ abonnement Navigo mensuel
→ Navigo mensuel
```

Cela permet au chatbot de retrouver une information meme si l'utilisateur n'emploie pas exactement le meme vocabulaire que le fichier source.

## Recherche web filtree

Si le RAG ne trouve pas de contexte pertinent, le backend peut utiliser Tavily.

Les resultats web sont filtres pour ne garder que des domaines fiables :

```text
sncf.com
transilien.com
iledefrance-mobilites.fr
ratp.fr
service-public.fr
```

Le filtrage est implemente dans :

```text
backend/core/search.py
```

## Prerequis

- Python 3.9 ou plus
- Node.js 18 ou plus
- Une cle OpenRouter
- Une cle Tavily si vous voulez activer le fallback web

## Installation backend

Depuis la racine du projet :

```bash
cd backend
python3 -m venv chatbot
source chatbot/bin/activate
pip install -r requirements.txt
```

Sur Windows PowerShell :

```powershell
cd backend
python -m venv chatbot
.\chatbot\Scripts\python.exe -m pip install -r requirements.txt
```

## Configuration

Creer le fichier `.env` :

```bash
cp .env.example .env
```

Sur Windows PowerShell :

```powershell
Copy-Item .env.example .env
```

Variables importantes :

```env
SECRET_KEY=une-cle-longue
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=google/gemma-4-31b-it:free
TAVILY_API_KEY=tvly-dev-...
DATABASE_URL=sqlite:///chatbot.db
CHROMA_PATH=./chroma_db
DATA_PATH=../data/json
HF_HOME=./hf_cache
HF_HUB_DISABLE_SYMLINKS_WARNING=1
PORT=5001
FLASK_DEBUG=false
```

`HF_HOME` permet de stocker le modele Hugging Face dans le dossier backend au lieu du dossier utilisateur.

## Lancer le backend

Depuis `backend/` :

```bash
source chatbot/bin/activate
PYTHONUTF8=1 python app.py
```

Sur Windows PowerShell :

```powershell
$env:PYTHONUTF8="1"
.\chatbot\Scripts\python.exe app.py
```

Le backend demarre sur :

```text
http://localhost:5001
```

Au premier lancement, l'indexation ChromaDB peut prendre plusieurs minutes.

## Reinitialiser l'index RAG

Si les donnees ou les aliases changent, il faut supprimer l'ancien index :

```bash
rm -rf backend/chroma_db
```

Sur Windows PowerShell :

```powershell
Remove-Item -Recurse -Force backend\chroma_db
```

Puis relancer le backend.

## Installation frontend

Dans un second terminal :

```bash
cd frontend
npm install
npm run dev
```

Le frontend demarre sur :

```text
http://localhost:5173
```

## Structure du projet

```text
TransportsChatbot/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   └── core/
│       ├── rag.py
│       ├── llm.py
│       └── search.py
├── data/
│   └── json/
├── frontend/
│   ├── package.json
│   └── src/
│       ├── api/
│       ├── components/
│       ├── context/
│       └── pages/
└── README.md
```

## Points importants

- Le chatbot ne doit pas inventer d'informations.
- Les reponses doivent s'appuyer sur le contexte RAG ou sur une source web fiable.
- Les horaires precis et les informations temps reel ne doivent pas etre inventes.
- Les dossiers `backend/chroma_db/`, `backend/hf_cache/`, `backend/chatbot/` et les fichiers `.env` ne doivent pas etre commits.

## Problemes frequents

**Le backend relance deux fois l'indexation**

Mettre dans `.env` :

```env
FLASK_DEBUG=false
```

**Impossible de supprimer `chroma_db`**

Un processus Python utilise probablement ChromaDB. Arreter le backend puis supprimer le dossier.

**Le chatbot repond avec le web alors que la donnee existe**

Supprimer `backend/chroma_db/`, relancer le backend et laisser l'indexation se terminer.

**Les tableaux Markdown s'affichent mal**

Le frontend utilise `remark-gfm` pour afficher les tableaux. Relancer :

```bash
cd frontend
npm install
npm run dev
```
