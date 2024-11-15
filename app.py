import os
import sqlite3
from flask import Flask, render_template, request, jsonify, g
from db_setup import initialize_database
from aggiorna_db import reset_gigiriva
from salvagigi import calculate_all_seasons

app = Flask(__name__)
DATABASE_PATH = 'serie_a_seasons_downloadable.db'

def get_db_connection():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ottieni l'ultimo detentore attuale, basato sulla stagione e sulla giornata più recente
    cursor.execute("""
        SELECT squadra_vincitrice, streak
        FROM Gigiriva
        ORDER BY stagione DESC, giornata DESC
        LIMIT 1
    """)
    result = cursor.fetchone()
    attuale_detentore = result['squadra_vincitrice'] if result else "N/A"
    streak = result['streak'] if result else 0

    # Calcola il numero di titoli vinti dal detentore attuale
    if attuale_detentore != "N/A":
        cursor.execute("SELECT COUNT(*) FROM Gigiriva WHERE squadra_vincitrice = ?", (attuale_detentore,))
        titoli_vinti = cursor.fetchone()[0]
    else:
        titoli_vinti = 0

    conn.close()

    return render_template('index.html', attuale_detentore=attuale_detentore, titoli_vinti=titoli_vinti, streak=streak)

@app.route('/api/gigiriva/<season>/<int:page>')
def api_gigiriva_season(season, page):
    """Endpoint API che restituisce i dati della stagione specifica in formato JSON per il lazy loading."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    entries_per_page = 50
    offset = page * entries_per_page

    cursor.execute("SELECT * FROM Gigiriva WHERE stagione = ? ORDER BY giornata LIMIT ? OFFSET ?", 
                   (season, entries_per_page, offset))
    gigiriva_data = cursor.fetchall()
    conn.close()
    
    data = [dict(row) for row in gigiriva_data]
    return jsonify(data)

@app.route('/gigiriva')
def gigiriva():
    conn = sqlite3.connect('serie_a_seasons_downloadable.db')
    cursor = conn.cursor()
    cursor.execute("SELECT stagione, data, giornata, squadra_in_casa, squadra_in_trasferta, risultato, squadra_vincitrice, numero_di_trofei_conquistati, streak FROM matches")
    gigiriva_data = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return render_template('gigiriva.html', gigiriva_data=gigiriva_data)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Ottieni la porta dalle variabili d'ambiente, default 5000
    app.run(host='0.0.0.0', port=port, debug=True)
