import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('jack.db')
cursor = conn.cursor()

# Create a table for players
cursor.execute('''
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    total_games_played INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0
)
''')


# Create a table for game sessions
cursor.execute('''
CREATE TABLE IF NOT EXISTS game_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    player_id INTEGER,
    dealer_hand_value INTEGER,
    player_hand_value INTEGER,
    outcome TEXT,
    FOREIGN KEY (player_id) REFERENCES players (player_id)
)
''')

cursor.execute("PRAGMA table_info(players)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]
if "money_bag" not in column_names:
    cursor.execute("""
    ALTER TABLE players
    ADD COLUMN money_bag INTEGER DEFAULT 100
""")

# Commit the changes and close the connection
conn.commit()
conn.close()