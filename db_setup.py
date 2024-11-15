import sqlite3

def initialize_database():
    conn = sqlite3.connect('serie_a_seasons_downloadable.db')
    cursor = conn.cursor()

    # Controlla se la tabella esiste già
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Gigiriva'")
    gigiriva_exists = cursor.fetchone()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='relegated_teams'")
    relegated_exists = cursor.fetchone()

    # Inizializza solo se le tabelle non esistono
    if not gigiriva_exists:
        cursor.execute('''CREATE TABLE IF NOT EXISTS Gigiriva (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stagione TEXT,
            squadra_in_casa TEXT,
            squadra_in_trasferta TEXT,
            risultato TEXT,
            squadra_vincitrice TEXT,
            numero_di_trofei_conquistati INTEGER,
            streak INTEGER
        )''')
        print("Tabella Gigiriva creata.")
    
    if not relegated_exists:
        cursor.execute('''CREATE TABLE IF NOT EXISTS relegated_teams (
            stagione TEXT,
            squadra TEXT
        )''')
        print("Tabella relegated_teams creata.")

    conn.commit()
    conn.close()

DATABASE_PATH = 'serie_a_seasons_downloadable.db'


def initialize_team_statistics():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Creazione della tabella di cache per le statistiche se non esiste
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_statistics (
            team_name TEXT PRIMARY KEY,
            trophy_count INTEGER,
            weeks_champion INTEGER,
            longest_streak INTEGER,
            streak_start_match TEXT,
            streak_end_match TEXT,
            win_percentage REAL,
            frequent_opponents TEXT
        )
    ''')
    conn.commit()
    conn.close()
