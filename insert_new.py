import csv
import sqlite3
import os

# CSV file to read
csv_file = 'main_games.csv'

# Connect to SQLite database
conn = sqlite3.connect('games.db')
cursor = conn.cursor()

# # Ensure table exists
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS games (
#     GameId TEXT PRIMARY KEY,
#     ArcadeGame INTEGER DEFAULT 0,
#     Eboot TEXT DEFAULT '',
#     Favorite INTEGER DEFAULT 0,
#     GameTitle TEXT DEFAULT 'Unknown',
#     Genre TEXT DEFAULT 'Unknown',
#     Icon0 TEXT DEFAULT '',
#     Loader TEXT DEFAULT '',
#     Param TEXT DEFAULT '',
#     Pic1 TEXT DEFAULT '',
#     Played INTEGER DEFAULT 0,
#     PSN INTEGER DEFAULT 0,
#     Format TEXT DEFAULT 'PlayStation 3',
#     Publisher TEXT DEFAULT 'Unknown',
#     Region TEXT DEFAULT 'Unknown',
#     ReleaseDate TEXT DEFAULT 'Unknown',
#     Snd0 TEXT DEFAULT '',
#     IconBlob BLOB,
#     Have INTEGER DEFAULT 0
# )
# """)

# Read CSV and insert
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0

    for row in reader:
        # Clean and default missing fields
        record = {
            'GameId': row.get('GameId', '').strip(),
            'ArcadeGame': int(row.get('ArcadeGame', 0)),
            'Eboot': row.get('Eboot', '').strip(),
            'Favorite': int(row.get('Favorite', 0)),
            'GameTitle': row.get('GameTitle', 'Unknown').strip(),
            'Genre': row.get('Genre', 'Unknown').strip(),
            'Icon0': row.get('Icon0', '').strip(),
            'Loader': row.get('Loader', '').strip(),
            'Param': row.get('Param', '').strip(),
            'Pic1': row.get('Pic1', '').strip(),
            'Played': int(row.get('Played', 0)),
            'PSN': int(row.get('PSN', 0)),
            'Format': row.get('Format', 'PlayStation 3').strip(),
            'Publisher': row.get('Publisher', 'Unknown').strip(),
            'Region': row.get('Region', 'Unknown').strip(),
            'ReleaseDate': row.get('ReleaseDate', 'Unknown').strip(),
            'Snd0': row.get('Snd0', '').strip(),
            'IconBlob': None,
            'Have': int(row.get('Have', 0))
        }

        # # Load IconBlob from Icon0 path if available
        # icon_path = record['Icon0']
        # if icon_path and os.path.exists(icon_path):
        #     with open(icon_path, 'rb') as img_file:
        #         record['IconBlob'] = img_file.read()

        # Insert or update the row
        cursor.execute("""
            INSERT OR REPLACE INTO games (
                GameId, ArcadeGame, Eboot, Favorite, GameTitle, Genre,
                Icon0, Loader, Param, Pic1, Played, PSN, Format,
                Publisher, Region, ReleaseDate, Snd0, IconBlob, Have
            ) VALUES (
                :GameId, :ArcadeGame, :Eboot, :Favorite, :GameTitle, :Genre,
                :Icon0, :Loader, :Param, :Pic1, :Played, :PSN, :Format,
                :Publisher, :Region, :ReleaseDate, :Snd0, :IconBlob, :Have
            )
        """, record)
        count += 1

conn.commit()
conn.close()
print(f"Successfully imported {count} entries from {csv_file}.")
