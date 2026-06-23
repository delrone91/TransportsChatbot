from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import DATABASE_URL

# On crée le moteur de base de données
# check_same_thread=False est nécessaire avec SQLite pour que Flask puisse
# utiliser la même connexion depuis plusieurs threads
engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {},
    # pool_pre_ping teste la connexion avant chaque usage et la rouvre si elle
    # a ete fermee. Necessaire avec Neon qui suspend la base apres inactivite
    # (sinon erreur "SSL connection has been closed unexpectedly").
    pool_pre_ping=True,
    pool_recycle=300,
)

# SessionLocal permet d'ouvrir une session vers la base de données
SessionLocal = sessionmaker(bind=engine)


# Classe de base dont héritent tous nos modèles (User, Message, etc.)
class Base(DeclarativeBase):
    pass


def get_db():
    # Ouvre une nouvelle session à chaque requête
    return SessionLocal()


def init_db():
    # On importe les modèles ici pour que SQLAlchemy les enregistre
    # avant de créer les tables
    import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _run_migrations()


def _run_migrations():
    # create_all ne modifie pas une table deja existante : on ajoute ici les
    # colonnes manquantes (ex. sources_json sur la base Neon deja creee).
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    if 'messages' not in inspector.get_table_names():
        return
    columns = [c['name'] for c in inspector.get_columns('messages')]
    if 'sources_json' not in columns:
        with engine.begin() as conn:
            conn.execute(text('ALTER TABLE messages ADD COLUMN sources_json TEXT'))
