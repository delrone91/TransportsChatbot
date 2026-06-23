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
