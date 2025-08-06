import sqlite3

db_file = 'games.db'
image_file = 'ICON0.PNG'

# Get GameId from user
game_id = input("Enter the GameId: ").strip()

# Read image binary data
with open(image_file, 'rb') as f:
    img_blob = f.read()

# Connect to the SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Check if the GameId exists
cursor.execute("SELECT COUNT(*) FROM games WHERE GameId = ?", (game_id,))
exists = cursor.fetchone()[0]

if exists == 0:
    print(f"No row found with GameId = {game_id}")
else:
    # Update IconBlob column for the given GameId
    cursor.execute("""
        UPDATE games SET IconBlob = ? WHERE GameId = ?
    """, (img_blob, game_id))
    conn.commit()
    print(f"Updated IconBlob for GameId = {game_id}")

conn.close()
