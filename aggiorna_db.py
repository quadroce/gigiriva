import sqlite3
import time
from db_connection import get_db_connection  # Importa da db_connection.py

DATABASE_PATH = 'serie_a_seasons_downloadable.db'

def reset_gigiriva():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    retries = 5  # Numero di tentativi per gestire il blocco
    for attempt in range(retries):
        try:
            # Svuota la tabella Gigiriva e resetta la sequenza ID
            cursor.execute("DELETE FROM Gigiriva")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='Gigiriva'")
            conn.commit()
            print("Tabella Gigiriva svuotata con successo.")
            break  # Esce dal ciclo se il comando ha successo
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print(f"Tentativo {attempt+1} di {retries}: database bloccato, ritento tra 1 secondo...")
                time.sleep(1)
            else:
                raise  # Rilancia l'errore se non è un problema di blocco
    conn.close()  # Chiude la connessione solo una volta terminati i tentativi
