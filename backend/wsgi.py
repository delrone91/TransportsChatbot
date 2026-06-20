"""Point d'entrée de production pour gunicorn.

En production on lance « gunicorn wsgi:app ». Gunicorn importe ce module
(et non le bloc __main__ de app.py), donc c'est ici qu'on déclenche la
création de la base de données et la construction de l'index RAG, avant
d'exposer l'application Flask.
"""
from app import app, initialize

initialize()
