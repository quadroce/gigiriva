import pandas as pd
import sqlite3

DATABASE_PATH = 'serie_a_seasons_downloadable.db'

def get_db_connection():
    """Funzione per connettersi al database."""
    return sqlite3.connect(DATABASE_PATH)

def process_season(data, starting_holder, season_year, expected_matchdays, titles, conn, current_streak):
    """
    Processes a single season to track the trophy holder for each matchday,
    excluding suspended matchdays and checking matchday count for accuracy.
    """
    current_holder = starting_holder
    trophy_history = []
    processed_matchdays = 0

    cursor = conn.cursor()

    for index, row in data.iterrows():
        matchday = row['matchdays']
        home_team = row['home_team']
        away_team = row['away_team']
        score = row['score']
        
        result = 'not_involved'

        # Check if the match was suspended
        if score.lower() == 'sospeso':
            continue

        # Parse the score and update holder as per rules
        try:
            home_goals, away_goals = map(int, score.split('-'))
        except ValueError:
            continue

        # Determine the new holder based on match result
        if home_team == current_holder or away_team == current_holder:
            if (home_team == current_holder and home_goals >= away_goals) or (away_team == current_holder and away_goals >= home_goals):
                result = 'retained'
                current_streak += 1
            else:
                current_holder = home_team if home_goals > away_goals else away_team
                result = 'transferred'
                current_streak = 1  # Streak for new holder starts at 1

                if current_holder not in titles:
                    titles[current_holder] = 0
                titles[current_holder] += 1

                print(f"Giornata {matchday}: Il trofeo passa a {current_holder}, Trofei conquistati: {titles[current_holder]}")

            cursor.execute(''' 
                INSERT INTO Gigiriva (stagione, data, giornata, squadra_in_casa, squadra_in_trasferta, risultato, squadra_vincitrice, numero_di_trofei_conquistati, streak)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (season_year, row['date'], matchday, home_team, away_team, score, current_holder, titles.get(current_holder, 0), current_streak))

        trophy_history.append({'matchday': matchday, 'holder': current_holder, 'result': result})
        processed_matchdays += 1

    conn.commit()
    return trophy_history, current_streak  # Return the updated current_streak

def save_winner_table(conn, season, trophy_history):
    """
    Salva i dati della storia del detentore per una stagione specifica nella tabella winner_{season}.
    """
    table_name = f"winner_{season}"
    cursor = conn.cursor()

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            giornata INTEGER,
            holder TEXT
        )
    """)

    cursor.executemany(f"INSERT INTO {table_name} (giornata, holder) VALUES (?, ?)", 
                       [(entry['matchday'], entry['holder']) for entry in trophy_history])
    conn.commit()


def calculate_all_seasons():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'serie_a_%'")
    all_seasons = [row[0] for row in cursor.fetchall()]
    all_seasons.sort()

    previous_holder = "Bologna"
    current_streak = 0  # Initialize current_streak here to persist across seasons
    titles = {}

    seasons_processed = set()

    for season in all_seasons:
        if season in seasons_processed:
            continue

        seasons_processed.add(season)
        season_data = pd.read_sql_query(f"SELECT * FROM {season}", conn)

        trophy_history, current_streak = process_season(
            season_data, previous_holder, season, expected_matchdays=34, titles=titles, conn=conn, current_streak=current_streak
        )
        save_winner_table(conn, season, trophy_history)

        if trophy_history:
            final_holder = trophy_history[-1]['holder']
            relegated_teams = pd.read_sql_query(f"SELECT team FROM relegated_teams WHERE season = '{season}'", conn)
            if final_holder in relegated_teams['team'].values:
                previous_holder = next(
                    (entry['holder'] for entry in reversed(trophy_history) if entry['holder'] not in relegated_teams['team'].values),
                    "Bologna"
                )
                current_streak = 0  # Reset streak if the holder is relegated
            else:
                previous_holder = final_holder

    conn.close()
