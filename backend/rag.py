"""
RAG (Retrieval-Augmented Generation) pipeline.

Requires: sentence-transformers, chromadb
Install:  pip install sentence-transformers chromadb

If these packages are absent the module runs in NO-OP mode:
retrieve() returns [] and load_and_index_data() prints a warning.
"""
import os
import json

try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

from config import CHROMA_PATH, DATA_PATH

_model = None
_collection = None


def get_model():
    global _model
    if _model is None:
        print("Chargement du modèle d'embedding (paraphrase-multilingual-MiniLM-L12-v2)...")
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return _model


def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_or_create_collection('transport_data')
    return _collection


def _record_to_text(prefix: str, item: dict, max_fields: int = 10) -> str:
    fields = [f"{k}: {v}" for k, v in item.items() if v is not None and v != '' and k != 'id']
    return prefix + ". ".join(fields[:max_fields])


def load_and_index_data():
    if not RAG_AVAILABLE:
        print("⚠️  RAG désactivé : dépendances manquantes (sentence-transformers, chromadb).")
        return

    collection = get_collection()
    if collection.count() > 0:
        print(f"RAG déjà indexé ({collection.count()} chunks). Chargement depuis ChromaDB.")
        return

    print("Indexation des données de transport (première utilisation — quelques minutes)...")
    model = get_model()
    chunks = []
    ids = []

    data_path = os.path.abspath(DATA_PATH)

    # Tarifs IDFM
    path = os.path.join(data_path, 'idfm_titres-et-tarifs.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for i, item in enumerate(data):
            name = item.get('product_name', '')
            desc = item.get('short_description', '')
            price = item.get('price', '')
            period = item.get('price_period', '') or ''
            args = (item.get('selling_arguments', '') or '').replace(';', ', ')
            text = f"Titre de transport IDFM: {name}. {desc}. Prix: {price} {period}. Avantages: {args}"
            chunks.append(text)
            ids.append(f"tarif_{i}")
        print(f"  ✓ {len(data)} titres de transport IDFM")

    # Équipements accessibilité SNCF
    path = os.path.join(data_path, 'sncf_equipements-accessibilite-sncf.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for i, item in enumerate(data):
            text = f"Équipement accessibilité SNCF - {item.get('column_1','')}: {item.get('column_2','')}"
            chunks.append(text)
            ids.append(f"equip_{i}")
        print(f"  ✓ {len(data)} équipements accessibilité")

    # Accessibilité gares
    path = os.path.join(data_path, 'sncf_accessibilite_gares.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for i, item in enumerate(data):
            text = f"Accessibilité SNCF: {item.get('donnees', '')}. Format: {item.get('format', '')}"
            chunks.append(text)
            ids.append(f"acc_{i}")

    # Horaires gares (limité à 600 enregistrements)
    path = os.path.join(data_path, 'sncf_horaires-des-gares1.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        subset = data[:600]
        for i, item in enumerate(subset):
            chunks.append(_record_to_text("Horaires gare SNCF - ", item))
            ids.append(f"horaire_{i}")
        print(f"  ✓ {len(subset)} enregistrements horaires (/{len(data)} total)")

    # Fréquentation gares (limité à 600 enregistrements)
    path = os.path.join(data_path, 'sncf_frequentation-gares.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        subset = data[:600]
        for i, item in enumerate(subset):
            chunks.append(_record_to_text("Fréquentation gare SNCF - ", item))
            ids.append(f"freq_{i}")
        print(f"  ✓ {len(subset)} enregistrements fréquentation (/{len(data)} total)")

    # Propreté en gare (limité à 400 enregistrements)
    path = os.path.join(data_path, 'sncf_proprete-en-gare.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        subset = data[:400]
        for i, item in enumerate(subset):
            chunks.append(_record_to_text("Propreté gare SNCF - ", item))
            ids.append(f"proprete_{i}")
        print(f"  ✓ {len(subset)} enregistrements propreté (/{len(data)} total)")

    if not chunks:
        print("Aucune donnée trouvée dans", data_path)
        return

    print(f"Calcul des embeddings pour {len(chunks)} chunks...")
    embeddings = model.encode(chunks, show_progress_bar=True, batch_size=64).tolist()
    collection.add(documents=chunks, embeddings=embeddings, ids=ids)
    print(f"✓ RAG indexé : {len(chunks)} chunks dans ChromaDB")


def retrieve(query: str, n_results: int = 5) -> list:
    if not RAG_AVAILABLE:
        return []
    model = get_model()
    collection = get_collection()
    if collection.count() == 0:
        return []
    query_embedding = model.encode([query])[0].tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count())
    )
    return results['documents'][0] if results['documents'] else []
