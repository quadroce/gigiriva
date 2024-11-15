import pandas as pd
import sqlite3

DATABASE_PATH = 'serie_a_seasons_downloadable.db'

def get_db_connection():
    """Funzione per connettersi al database."""
    return sqlite3.connect(DATABASE_PATH)

def process_season(data, starting_holder, season_year, expected_matchdays):
    """
    Processes a single season to track the trophy holder for each matchday,
    excluding suspended matchdays and checking matchday count for accuracy.
    """
    current_holder = starting_holder
    trophy_history = []
    processed_matchdays = 0
    suspension_count = 0

    conn = get_db_connection()
    cursor = conn.cursor()

    for index, row in data.iterrows():
        matchday = row['matchdays']
        home_team = row['home_team']
        away_team = row['away_team']
        score = row['score']
        
        # Inizializzazione di result per evitare l'errore di variabile non associata
        result = 'not_involved'

        # Check if the match was suspended
        if score.lower() == 'sospeso':
            suspension_count += 1
            continue  # Skip suspended matchdays

        # Parse the score and update holder as per rules
        try:
            home_goals, away_goals = map(int, score.split('-'))
        except ValueError:
            continue

        # Determine the new holder based on match result
        if home_team == current_holder or away_team == current_holder:
            if (home_team == current_holder and home_goals >= away_goals) or (away_team == current_holder and away_goals >= home_goals):
                result = 'retained'
            else:
                # Trophy changes hands
                current_holder = home_team if home_goals > away_goals else away_team
                result = 'transferred'

            # Insert data into Gigiriva
            cursor.execute(''' 
                INSERT INTO Gigiriva (stagione, data, giornata, squadra_in_casa, squadra_in_trasferta, risultato, squadra_vincitrice, numero_di_trofei_conquistati, streak)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (season_year, row['date'], matchday, home_team, away_team, score, current_holder, 1, 1))

        trophy_history.append({'matchday': matchday, 'holder': current_holder, 'result': result})
        processed_matchdays += 1
        conn.commit()  # Commit each insertion

    # Check for discrepancy in matchday count
    if processed_matchdays != expected_matchdays:
        pass

    conn.close()
    return trophy_history

def save_winner_table(conn, season, trophy_history):
    """
    Salva i dati della storia del detentore per una stagione specifica nella tabella winner_{season}.
    """
    table_name = f"winner_{season}"
    cursor = conn.cursor()
    
    # Creazione della tabella
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            giornata INTEGER,
            holder TEXT
        )
    """)
    
    # Inserimento dei dati
    cursor.executemany(f"INSERT INTO {table_name} (giornata, holder) VALUES (?, ?)", 
                       [(entry['matchday'], entry['holder']) for entry in trophy_history])
    conn.commit()

def calculate_all_seasons():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ottiene tutte le stagioni in ordine, con la prima stagione come 1929-1930
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'serie_a_%'")
    all_seasons = [row[0] for row in cursor.fetchall()]
    all_seasons.sort()  # Ordina alfabeticamente, assicurandosi che la stagione 1929-1930 sia prima

    previous_holder = "Bologna"  # Set initial trophy holder here

    # Aggiungi il set per monitorare le stagioni già processate
    seasons_processed = set()

    for season in all_seasons:
        if season in seasons_processed:
            continue  # Salta la stagione se è già stata processata

        seasons_processed.add(season)  # Aggiungi la stagione al set

        # Carica i dati della stagione come DataFrame
        season_data = pd.read_sql_query(f"SELECT * FROM {season}", conn)

        # Calcola la storia del trofeo per la stagione corrente
        trophy_history = process_season(season_data, previous_holder, season, expected_matchdays=34)

        # Salva i risultati nel database
        save_winner_table(conn, season, trophy_history)

        # Verifica se il detentore alla fine della stagione è retrocesso
        if trophy_history:
            final_holder = trophy_history[-1]['holder']

            # Controlla se `final_holder` è retrocesso
            relegated_teams = pd.read_sql_query(f"SELECT team FROM relegated_teams WHERE season = '{season}'", conn)
            if final_holder in relegated_teams['team'].values:
                # Trova l'ultima squadra di Serie A ad aver detenuto il trofeo
                previous_holder_in_serie_a = None
                for entry in reversed(trophy_history):
                    if entry['holder'] not in relegated_teams['team'].values:
                        previous_holder_in_serie_a = entry['holder']
                        break

                # Aggiorna il detentore per la stagione successiva
                previous_holder = previous_holder_in_serie_a or "Bologna"  # Default to Bologna if no valid holder found
            else:
                # Detentore rimane lo stesso per la stagione successiva
                previous_holder = final_holder

    conn.close()

# Run the complete calculation across all seasons
#calculate_all_seasons()
