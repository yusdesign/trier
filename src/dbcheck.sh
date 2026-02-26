# Quick Python one-liner
python -c "
import sqlite3
conn = sqlite3.connect('../music/artists.db')
for row in conn.execute('SELECT name, play_count FROM artists ORDER BY play_count DESC LIMIT 5'):
    print(f'🎵 {row[0]}: {row[1]} plays')
conn.close()
"
