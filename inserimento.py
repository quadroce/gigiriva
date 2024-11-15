# inserimento.py
import sqlite3
import csv
import os
from flask import Blueprint, request, render_template, flash, redirect, url_for

# Configura il Blueprint per gestire le route di inserimento
inserimento_blueprint = Blueprint('inserimento', __name__)

DATABASE_PATH = "serie_a_seasons_downloadable.db"
UPLOAD_FOLDER = "uploads"

def get_db_connection():
    return sqlite3.connect(DATABASE_PATH)

def create_season_table(season):
    """Crea una tabella per una nuova stagione se non esiste già."""
    conn = get_db_connection()
    cursor = conn.cursor()
    table_name = f"serie_a_{season}"
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            matchdays INTEGER,
            home_team TEXT,
            away_team TEXT,
            score TEXT
        )
    """)
    conn.commit()
    conn.close()

@inserimento_blueprint.route('/inserimento_giornate')
def inserimento_giornate():
    """Renderizza la pagina per caricare il file CSV."""
    return render_template('inserimento_giornate.html')

@inserimento_blueprint.route('/upload_csv', methods=['POST'])
def upload_csv():
    """Gestisce il caricamento del file CSV e inserisce i dati nel database."""
    file = request.files['csv_file']
    season = request.form.get('season')  # Ottiene la stagione dal form

    # Verifica che sia stato caricato un file CSV e che sia stata specificata la stagione
    if file and file.filename.endswith('.csv') and season:
        # Crea la tabella per la stagione se non esiste
        create_season_table(season)
        
        # Salva il file caricato nella cartella uploads
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Processa il CSV e inserisci i dati
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Inserisce i dati per ogni partita nel database
            for row in reader:
                cursor.execute(f"""
                    INSERT INTO serie_a_{season} (date, matchdays, home_team, away_team, score)
                    VALUES (?, ?, ?, ?, ?)
                """, (row['date'], row['matchday'], row['home_team'], row['away_team'], row['score']))
            
            conn.commit()
            conn.close()
        
        flash(f"Giornata per la stagione {season} caricata con successo!", 'success')
    else:
        flash('Errore: carica un file CSV valido e specifica una stagione.', 'danger')
    
    return redirect(url_for('inserimento.inserimento_giornate'))
