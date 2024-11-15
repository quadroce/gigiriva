import time
import sqlite3
from salvagigi import calculate_all_seasons
 

def initialize_application():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    DATABASE_PATH = 'serie_a_seasons_downloadable.db'

    # Aumenta i tentativi e il tempo di attesa
    retries = 10
    delay = 2  # Secondi di attesa tra i tentativi

    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('initialized', 'False')")
    cursor.execute("SELECT value FROM settings WHERE key='initialized'")
    initialized = cursor.fetchone()

    if initialized and initialized[0] == 'False':
        for attempt in range(retries):
            try:
                reset_gigiriva()
                calculate_all_seasons()
                cursor.execute("UPDATE settings SET value = 'True' WHERE key = 'initialized'")
                conn.commit()
                print("Inizializzazione completata.")
                break
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    print(f"Tentativo {attempt+1} di {retries}: database bloccato, ritento tra {delay} secondi...")
                    time.sleep(delay)
                else:
                    raise
        else:
            print("Inizializzazione fallita dopo diversi tentativi.")
    conn.close()
