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
import re
import unicodedata
from collections import defaultdict

try:
    from langchain_core.documents import Document
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

from config import CHROMA_PATH, DATA_PATH

COLLECTION_NAME = 'transport_data_v3'
RELEVANCE_THRESHOLD = 1.6
MIN_KEYWORD_OVERLAP = 1

_embeddings = None
_vectorstore = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        print("Chargement du modele d'embedding avec LangChain...")
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    return _embeddings


def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=CHROMA_PATH,
            embedding_function=get_embeddings(),
        )
    return _vectorstore


def _make_document(content: str, source: str, doc_type: str, doc_id: str) -> Document:
    return Document(
        page_content=content,
        metadata={
            "source": source,
            "type": doc_type,
            "id": doc_id,
        },
    )


def _build_tarif_aliases(name: str) -> str:
    aliases_by_product = {
        "Forfait Navigo Mois": [
            "forfait Navigo mensuel",
            "abonnement Navigo mensuel",
            "Navigo mensuel",
            "pass Navigo mensuel",
            "forfait mensuel Navigo",
        ],
        "Forfait Navigo Semaine": [
            "forfait Navigo hebdomadaire",
            "abonnement Navigo semaine",
            "Navigo hebdomadaire",
            "pass Navigo semaine",
        ],
        "Forfait Navigo Annuel": [
            "abonnement Navigo annuel",
            "Navigo annuel",
            "pass Navigo annuel",
            "forfait annuel Navigo",
        ],
        "Forfait Navigo Jour": [
            "forfait Navigo journalier",
            "Navigo jour",
            "pass Navigo jour",
            "forfait journalier Navigo",
        ],
    }
    aliases = aliases_by_product.get(name, [])
    if not aliases:
        return ""
    return f"Alias de recherche : {', '.join(aliases)}. "


def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return text


def _keywords(text: str) -> set[str]:
    stopwords = {
        "quel", "quelle", "quels", "quelles", "dans", "avec", "pour", "sont",
        "est", "des", "les", "une", "aux", "sur", "comment", "prix",
    }
    normalized = _normalize_text(text)
    return {
        word for word in re.findall(r"[a-z0-9]+", normalized)
        if len(word) > 3 and word not in stopwords
    }


def _metadata_filter_for_query(query: str) -> dict | None:
    normalized = _normalize_text(query)
    if any(word in normalized for word in ["navigo", "forfait", "ticket", "tarif", "abonnement"]):
        return {"type": "tarif"}
    if any(word in normalized for word in ["pmr", "accessibilite", "accessible", "ascenseur", "equipement"]):
        return {"type": "equip"}
    return None


def _is_relevant_result(query_words: set[str], content: str, score: float) -> bool:
    if score <= RELEVANCE_THRESHOLD:
        return True
    content_words = _keywords(content)
    return len(query_words & content_words) >= MIN_KEYWORD_OVERLAP


def _build_tarif_chunk(item: dict) -> str:
    name = item.get('product_name', '')
    desc = item.get('short_description', '') or ''
    price = item.get('price', '')
    period = item.get('price_period', '') or ''
    args = (item.get('selling_arguments', '') or '').replace(';', ', ')
    profile = item.get('profile_new_fr', '') or ''
    duration = item.get('duration_new_fr', '') or ''
    aliases = _build_tarif_aliases(name)
    return (
        f"Titre de transport IDFM : {name}. "
        f"{aliases}"
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
        print("RAG desactive : dependances LangChain/Chroma manquantes.")
        return

    vectorstore = get_vectorstore()
    existing_count = vectorstore._collection.count()
    if existing_count > 0:
        print(f"RAG deja indexe ({existing_count} documents). Chargement depuis ChromaDB.")
        return

    print("Indexation complete des donnees de transport avec LangChain...")
    documents = []
    document_ids = []
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
                doc_id = f"{prefix}_{i}"
                documents.append(_make_document(builder(item), filename, prefix, doc_id))
                document_ids.append(doc_id)
            print(f"  ✓ {len(data)} {label}")

    path = os.path.join(data_path, 'sncf_equipements-accessibilite-sncf.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for i, item in enumerate(data):
            doc_id = f"equip_{i}"
            content = f"Équipement accessibilité SNCF — {item.get('column_1', '')} : {item.get('column_2', '')}"
            documents.append(_make_document(content, 'sncf_equipements-accessibilite-sncf.json', 'equip', doc_id))
            document_ids.append(doc_id)
        print(f"  ✓ {len(data)} équipements accessibilité")

    path = os.path.join(data_path, 'sncf_proprete-en-gare.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        proprete_chunks = _aggregate_proprete(data)
        for i, text in enumerate(proprete_chunks):
            doc_id = f"proprete_{i}"
            documents.append(_make_document(text, 'sncf_proprete-en-gare.json', 'proprete', doc_id))
            document_ids.append(doc_id)
        print(f"  ✓ {len(proprete_chunks)} gares (agrégées depuis {len(data)} contrôles mensuels)")

    if not documents:
        print("Aucune donnee trouvee dans", data_path)
        return

    print(f"Calcul et stockage des embeddings pour {len(documents)} documents...")
    batch_size = 1000
    for start in range(0, len(documents), batch_size):
        end = start + batch_size
        vectorstore.add_documents(
            documents=documents[start:end],
            ids=document_ids[start:end],
        )
        print(f"  Indexe {min(end, len(documents))}/{len(documents)} documents...")

    print(f"RAG indexe : {len(documents)} documents dans ChromaDB")


def retrieve(query: str, n_results: int = 6) -> list[dict]:
    if not RAG_AVAILABLE:
        return []

    vectorstore = get_vectorstore()

    if vectorstore._collection.count() == 0:
        return []

    metadata_filter = _metadata_filter_for_query(query)
    search_kwargs = {"k": max(n_results, 8)}
    if metadata_filter:
        search_kwargs["filter"] = metadata_filter

    results = vectorstore.similarity_search_with_score(query, **search_kwargs)

    docs = []
    query_words = _keywords(query)
    for doc, score in results:
        if _is_relevant_result(query_words, doc.page_content, score):
            docs.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source"),
                "type": doc.metadata.get("type"),
                "score": score,
            })
        if len(docs) >= n_results:
            break

    return docs
