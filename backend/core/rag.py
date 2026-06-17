"""
RAG (Retrieval-Augmented Generation) pipeline.

Données indexées :
- Tarifs IDFM (titres de transport)
- Équipements accessibilité SNCF
- Horaires des gares SNCF
- Fréquentation des gares SNCF (2015–2024)
- Propreté en gare (agrégée par gare depuis 78 523 contrôles mensuels)
"""
import os
import json
from collections import defaultdict

try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

from config import CHROMA_PATH, DATA_PATH

_model = None
_collection = None

COLLECTION_NAME = 'transport_data_v3'
RELEVANCE_THRESHOLD = 0.7


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
        _collection = client.get_or_create_collection(
            COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def _build_tarif_chunk(item: dict) -> str:
    name = item.get('product_name', '')
    desc = item.get('short_description', '') or ''
    price = item.get('price', '')
    period = item.get('price_period', '') or ''
    args = (item.get('selling_arguments', '') or '').replace(';', ', ')
    profile = item.get('profile_new_fr', '') or ''
    duration = item.get('duration_new_fr', '') or ''
    return (
        f"Titre de transport IDFM : {name}. "
        f"Description : {desc}. "
        f"Prix : {price} {period}. "
        f"Profil : {profile}. "
        f"Durée : {duration}. "
        f"Avantages : {args}"
    )


def _build_horaire_chunk(item: dict) -> str:
    nom = item.get('nom_normal', '')
    jour = item.get('jour', '') or ''
    horaire = item.get('horaire_normal', '') or ''
    horaire_ferie = item.get('horaire_ferie', '') or ''
    text = f"Horaires gare SNCF {nom}"
    if jour:
        text += f" — type de jour : {jour}"
    if horaire:
        text += f" — horaire normal : {horaire}"
    if horaire_ferie:
        text += f" — horaire jour férié : {horaire_ferie}"
    return text


def _build_frequentation_chunk(item: dict) -> str:
    nom = item.get('nom_gare', '')
    cp = item.get('code_postal', '') or ''
    region = item.get('direction_regionale_gares', '') or ''
    segment = item.get('segmentation_marketing', '') or ''
    v2024 = item.get('total_voyageurs_2024', '') or ''
    v2023 = item.get('total_voyageurs_2023', '') or ''
    v2022 = item.get('total_voyageurs_2022', '') or ''
    return (
        f"Fréquentation gare SNCF {nom} (code postal {cp}, {region}, {segment}). "
        f"Nombre de voyageurs 2024 : {v2024}. "
        f"Nombre de voyageurs 2023 : {v2023}. "
        f"Nombre de voyageurs 2022 : {v2022}."
    )


def _aggregate_proprete(data: list) -> list[str]:
    stations: dict = defaultdict(lambda: {
        'nom': '', 'observations': 0, 'conformites_ok': 0, 'mois_count': 0
    })
    for item in data:
        uic = item.get('uic', '')
        nom = item.get('nom_gare', '')
        obs = item.get('nombre_d_observations') or 0
        non_conf = item.get('nombre_de_non_conformites') or 0
        stations[uic]['nom'] = nom
        stations[uic]['observations'] += obs
        stations[uic]['conformites_ok'] += (obs - non_conf)
        stations[uic]['mois_count'] += 1

    chunks = []
    for uic, s in stations.items():
        if not s['nom']:
            continue
        if s['observations'] > 0:
            taux = round(s['conformites_ok'] / s['observations'] * 100, 1)
            chunks.append(
                f"Propreté gare SNCF {s['nom']} (UIC {uic}) — "
                f"taux de conformité propreté : {taux}% "
                f"(calculé sur {s['mois_count']} mois de contrôles, "
                f"{s['observations']} observations)"
            )
        else:
            chunks.append(f"Propreté gare SNCF {s['nom']} (UIC {uic}) — données non disponibles")
    return chunks


def load_and_index_data():
    if not RAG_AVAILABLE:
        print("⚠️  RAG désactivé : dépendances manquantes (sentence-transformers, chromadb).")
        return

    collection = get_collection()
    if collection.count() > 0:
        print(f"RAG déjà indexé ({collection.count()} chunks). Chargement depuis ChromaDB.")
        return

    print("Indexation complète des données de transport...")
    model = get_model()
    chunks = []
    ids = []
    data_path = os.path.abspath(DATA_PATH)

    datasets = [
        ('idfm_titres-et-tarifs.json', _build_tarif_chunk, 'tarif', 'titres de transport IDFM'),
        ('sncf_horaires-des-gares1.json', _build_horaire_chunk, 'horaire', 'horaires de gares SNCF'),
        ('sncf_frequentation-gares.json', _build_frequentation_chunk, 'freq', 'gares (fréquentation)'),
    ]

    for filename, builder, prefix, label in datasets:
        path = os.path.join(data_path, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for i, item in enumerate(data):
                chunks.append(builder(item))
                ids.append(f"{prefix}_{i}")
            print(f"  ✓ {len(data)} {label}")

    path = os.path.join(data_path, 'sncf_equipements-accessibilite-sncf.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for i, item in enumerate(data):
            chunks.append(f"Équipement accessibilité SNCF — {item.get('column_1', '')} : {item.get('column_2', '')}")
            ids.append(f"equip_{i}")
        print(f"  ✓ {len(data)} équipements accessibilité")

    path = os.path.join(data_path, 'sncf_proprete-en-gare.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        proprete_chunks = _aggregate_proprete(data)
        for i, text in enumerate(proprete_chunks):
            chunks.append(text)
            ids.append(f"proprete_{i}")
        print(f"  ✓ {len(proprete_chunks)} gares (agrégées depuis {len(data)} contrôles mensuels)")

    if not chunks:
        print("Aucune donnée trouvée dans", data_path)
        return

    print(f"Calcul des embeddings pour {len(chunks)} chunks...")
    embeddings = model.encode(chunks, show_progress_bar=True, batch_size=64).tolist()

    batch_size = 5000
    for start in range(0, len(chunks), batch_size):
        end = start + batch_size
        collection.add(
            documents=chunks[start:end],
            embeddings=embeddings[start:end],
            ids=ids[start:end],
        )
        print(f"  Indexé {min(end, len(chunks))}/{len(chunks)} chunks...")
    print(f"✓ RAG indexé : {len(chunks)} chunks dans ChromaDB")


def retrieve(query: str, n_results: int = 6) -> list[str]:
    if not RAG_AVAILABLE:
        return []
    model = get_model()
    collection = get_collection()
    if collection.count() == 0:
        return []
    query_embedding = model.encode([query])[0].tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
        include=['documents', 'distances']
    )
    docs = results['documents'][0] if results['documents'] else []
    distances = results['distances'][0] if results['distances'] else []
    return [doc for doc, dist in zip(docs, distances) if dist < RELEVANCE_THRESHOLD]
