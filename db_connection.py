import sqlite3
from flask import g
import logging

DATABASE_PATH = 'serie_a_seasons_downloadable.db'

# Configura il logging per registrare le query SQL
logging.basicConfig(
    filename='sql_queries.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger()

def log_query(query, params):
    """Logga la query SQL eseguita con i parametri."""
    if params:
        logger.info(f"Esecuzione Query: {query} | Parametri: {params}")
    else:
        logger.info(f"Esecuzione Query: {query}")

def get_db_connection():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE_PATH, timeout=20)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA synchronous = OFF")
        g.db.execute("PRAGMA journal_mode = MEMORY")
    return g.db
