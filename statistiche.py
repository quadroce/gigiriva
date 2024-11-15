import sqlite3
import json
from flask import Blueprint, jsonify, request

DATABASE_PATH = 'serie_a_seasons_downloadable.db'

# Crea un blueprint per le statistiche
statistiche_bp = Blueprint('statistiche', __name__)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def update_team_statistics():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Ottieni tutte le squadre che hanno vinto almeno un trofeo
    cursor.execute("SELECT DISTINCT squadra_vincitrice FROM Gigiriva")
    teams = [row['squadra_vincitrice'] for row in cursor.fetchall()]

    for team_name in teams:
        # Calcola le statistiche
        cursor.execute("SELECT COUNT(*) FROM Gigiriva WHERE squadra_vincitrice = ?", (team_name,))
        trophy_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT giornata) FROM Gigiriva WHERE squadra_vincitrice = ?", (team_name,))
        weeks_champion = cursor.fetchone()[0]

        cursor.execute("SELECT MAX(streak) FROM Gigiriva WHERE squadra_vincitrice = ?", (team_name,))
        longest_streak = cursor.fetchone()[0]

        cursor.execute("""
            SELECT giornata FROM Gigiriva 
            WHERE squadra_vincitrice = ? AND streak = ?
            ORDER BY data
        """, (team_name, longest_streak))
        streak_matches = cursor.fetchall()
        streak_start_match = streak_matches[0]['giornata'] if streak_matches else "N/A"
        streak_end_match = streak_matches[-1]['giornata'] if streak_matches else "N/A"

        cursor.execute("""
            SELECT COUNT(*) FROM Gigiriva 
            WHERE (squadra_in_casa = ? OR squadra_in_trasferta = ?) 
            AND (risultato LIKE '%-0' OR risultato LIKE '0-%')
        """, (team_name, team_name))
        total_matches = cursor.fetchone()[0]
        win_percentage = round((trophy_count / total_matches) * 100, 2) if total_matches else 0

        cursor.execute("""
            SELECT squadra_in_casa AS opponent FROM Gigiriva WHERE squadra_trasferta = ?
            UNION ALL
            SELECT squadra_trasferta AS opponent FROM Gigiriva WHERE squadra_in_casa = ?
        """, (team_name, team_name))
        opponents = [row['opponent'] for row in cursor.fetchall()]
        frequent_opponents = json.dumps(list(set(opponents[:5])))  # Solo i primi 5

        # Inserisci o aggiorna i dati della squadra
        cursor.execute('''
            INSERT INTO team_statistics (team_name, trophy_count, weeks_champion, longest_streak,
                                         streak_start_match, streak_end_match, win_percentage, frequent_opponents)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(team_name) DO UPDATE SET
                trophy_count=excluded.trophy_count,
                weeks_champion=excluded.weeks_champion,
                longest_streak=excluded.longest_streak,
                streak_start_match=excluded.streak_start_match,
                streak_end_match=excluded.streak_end_match,
                win_percentage=excluded.win_percentage,
                frequent_opponents=excluded.frequent_opponents
        ''', (team_name, trophy_count, weeks_champion, longest_streak, streak_start_match, streak_end_match,
              win_percentage, frequent_opponents))

    conn.commit()
    conn.close()

@statistiche_bp.route('/api/teams')
def get_teams():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT squadra_vincitrice FROM Gigiriva ORDER BY squadra_vincitrice")
    teams = [{'name': row['squadra_vincitrice']} for row in cursor.fetchall()]
    conn.close()
    return jsonify(teams)

@statistiche_bp.route('/api/team_stats')
def team_stats():
    team_name = request.args.get('team')
    conn = get_db_connection()
    cursor = conn.cursor()

    # Recupera le statistiche pre-calcolate dalla tabella `team_statistics`
    cursor.execute("SELECT * FROM team_statistics WHERE team_name = ?", (team_name,))
    stats = cursor.fetchone()

    if stats:
        stats = dict(stats)
        stats['frequent_opponents'] = json.loads(stats['frequent_opponents'])  # Converte JSON in lista

    conn.close()
    return jsonify(stats) if stats else jsonify({"error": "Squadra non trovata"}), 404
