import sqlite3
import os

# Percorso al tuo file SQLite esistente
database_path = "serie_a_seasons_downloadable.db"

if os.path.exists(database_path):
    try:
        # Connessione al database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Lista completa delle stagioni per le quali calcolare il numero di giornate
        seasons = [
            "1929_1930", "1930_1931", "1931_1932", "1932_1933", "1933_1934", "1934_1935",
            "1935_1936", "1936_1937", "1937_1938", "1938_1939", "1939_1940", "1940_1941",
            "1941_1942", "1942_1943", "1946_1947", "1947_1948", "1948_1949", "1949_1950",
            "1950_1951", "1951_1952", "1952_1953", "1953_1954", "1954_1955", "1955_1956",
            "1956_1957", "1957_1958", "1958_1959", "1959_1960", "1960_1961", "1961_1962",
            "1962_1963", "1963_1964", "1964_1965", "1965_1966", "1966_1967", "1967_1968",
            "1968_1969", "1969_1970", "1970_1971", "1971_1972", "1972_1973", "1973_1974",
            "1974_1975", "1975_1976", "1976_1977", "1977_1978", "1978_1979", "1979_1980",
            "1980_1981", "1981_1982", "1982_1983", "1983_1984", "1984_1985", "1985_1986",
            "1986_1987", "1987_1988", "1988_1989", "1989_1990", "1990_1991", "1991_1992",
            "1992_1993", "1993_1994", "1994_1995", "1995_1996", "1996_1997", "1997_1998",
            "1998_1999", "1999_2000", "2000_2001", "2001_2002", "2002_2003", "2003_2004",
            "2004_2005", "2005_2006", "2006_2007", "2007_2008", "2008_2009", "2009_2010",
            "2010_2011", "2011_2012", "2012_2013", "2013_2014", "2014_2015", "2015_2016",
            "2016_2017", "2017_2018", "2018_2019", "2019_2020", "2020_2021", "2021_2022",
            "2022_2023", "2023_2024"
        ]

        # Calcola il numero di giornate per ciascuna stagione e aggiorna la tabella
        for season in seasons:
            table_name = f"serie_a_{season}"

            # Rimuovi tutti i valori dalla colonna "matchdays" se esiste
            try:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN matchdays INTEGER")
            except sqlite3.OperationalError:
                # La colonna probabilmente già esiste, quindi svuotiamo i valori
                cursor.execute(f"UPDATE {table_name} SET matchdays = NULL")

            # Conta il numero totale di righe nella tabella
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = cursor.fetchone()[0]

            # Calcola il numero di giornate
            if season == "1947_1948":
                matchdays = 42  # Forza 42 giornate per la stagione 1947-1948
            else:
                cursor.execute(f"SELECT COUNT(DISTINCT home_team) FROM {table_name}")
                num_teams = cursor.fetchone()[0]
                if num_teams > 1:
                    matchdays = (num_teams - 1) * 2  # Numero totale di giornate
                else:
                    matchdays = 0

            # Verifica se il numero di partite per giornata è costante
            matches_per_matchday = total_rows / matchdays if matchdays > 0 else 0
            if total_rows % matchdays != 0:
                print(f"Attenzione: il numero di partite per giornata nella stagione {season} non è costante.")

            # Assegna il numero di giornata a ciascuna partita, controllando che una squadra non giochi due volte nella stessa giornata
            current_matchday = 1
            team_matchday_check = {}
            for i in range(total_rows):
                cursor.execute(f"SELECT home_team, away_team FROM {table_name} WHERE rowid = ?", (i + 1,))
                home_team, away_team = cursor.fetchone()

                # Controlla se una delle squadre ha già giocato in questa giornata
                if home_team in team_matchday_check and team_matchday_check[home_team] == current_matchday:
                    current_matchday += 1
                if away_team in team_matchday_check and team_matchday_check[away_team] == current_matchday:
                    current_matchday += 1

                # Aggiorna il controllo per le squadre
                team_matchday_check[home_team] = current_matchday
                team_matchday_check[away_team] = current_matchday

                # Assegna il numero di giornata
                cursor.execute(f"UPDATE {table_name} SET matchdays = ? WHERE rowid = ?", (current_matchday, i + 1))
                
                # Incrementa la giornata se necessario
                if (i + 1) % matches_per_matchday == 0 and current_matchday < matchdays:
                    current_matchday += 1

        # Salva le modifiche e chiudi la connessione
        conn.commit()
        print("Aggiornamento del numero di giornate completato con successo per tutte le stagioni!")
    except sqlite3.Error as e:
        print(f"Errore durante la connessione al database: {e}")
    finally:
        conn.close()
else:
    print("Database non trovato.")
