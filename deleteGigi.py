import sqlite3

DATABASE_PATH = 'serie_a_seasons_downloadable.db'  # Assicurati che il percorso sia corretto

def clear_gigiriva_table():
    try:
        # Connessione al database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Cancella tutti i dati dalla tabella Gigiriva
        cursor.execute("DELETE FROM Gigiriva")
        
        # Reimposta l'ID incrementale se necessario
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='Gigiriva'")
        
        # Conferma le modifiche
        conn.commit()
        print("Tabella Gigiriva svuotata con successo.")
        
    except sqlite3.Error as e:
        print(f"Errore durante la pulizia della tabella Gigiriva: {e}")
        
    finally:
        # Chiudi la connessione al database
        if conn:
            conn.close()

# Esegui la funzione
clear_gigiriva_table()
