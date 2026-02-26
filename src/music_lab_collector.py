#!/usr/bin/env python
"""
TRIER Music Lab - Collect your listening behavior
"""

import csv
import os
import json
from datetime import datetime
import random  # For demo - replace with real API calls

class MusicLabCollector:
    def __init__(self):
        self.music_path = '../music/'
        self.ensure_files()
        
    def ensure_files(self):
        """Create music files if they don't exist"""
        os.makedirs(self.music_path, exist_ok=True)
        
        # Plays CSV
        if not os.path.exists(f'{self.music_path}plays.csv'):
            with open(f'{self.music_path}plays.csv', 'w') as f:
                f.write('timestamp,artist,track,album,source,duration_seconds\n')
        
        # Artists DB (SQLite for music taste)
        import sqlite3
        conn = sqlite3.connect(f'{self.music_path}artists.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS artists (
                artist_id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                country TEXT,
                genre TEXT,
                play_count INTEGER DEFAULT 0,
                first_heard DATE,
                last_heard DATE
            )
        ''')
        conn.commit()
        conn.close()
        
        # Discoveries JSON
        if not os.path.exists(f'{self.music_path}discoveries.json'):
            with open(f'{self.music_path}discoveries.json', 'w') as f:
                json.dump([], f)
    
    def log_play(self, artist, track, album="", source="manual"):
        """Log a song you listened to"""
        
        # Append to plays.csv
        with open(f'{self.music_path}plays.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                artist,
                track,
                album,
                source,
                180  # Default 3 min - you can update with actual
            ])
        
        # Update artist database
        import sqlite3
        conn = sqlite3.connect(f'{self.music_path}artists.db')
        
        # Check if artist exists
        cur = conn.execute("SELECT artist_id, play_count FROM artists WHERE name = ?", (artist,))
        row = cur.fetchone()
        
        if row:
            # Update existing
            conn.execute("""
                UPDATE artists 
                SET play_count = play_count + 1,
                    last_heard = ?
                WHERE name = ?
            """, (datetime.now().date().isoformat(), artist))
        else:
            # New artist discovery!
            conn.execute("""
                INSERT INTO artists (name, play_count, first_heard, last_heard)
                VALUES (?, 1, ?, ?)
            """, (artist, datetime.now().date().isoformat(), 
                  datetime.now().date().isoformat()))
            
            # Log discovery
            self.log_discovery(artist, track, source)
        
        conn.commit()
        conn.close()
        
        print(f"🎵 Logged: {artist} - {track}")
    
    def log_discovery(self, artist, track, source="manual"):  # Add source parameter!
        """Record a new artist discovery"""
        with open(f'{self.music_path}discoveries.json', 'r') as f:
            discoveries = json.load(f)
    
        discoveries.append({
            'artist': artist,
            'track': track,
            'discovered_at': datetime.now().isoformat(),
            'source': 'SomaFM' if 'SomaFM' in str(source) else 'manual'
        })
    
        with open(f'{self.music_path}discoveries.json', 'w') as f:
            json.dump(discoveries[-100:], f, indent=2)  # Keep last 100
   
    def collect_somafm_demo(self):
        """Demo: Simulate SomaFM Indie Pop listening"""
        # In real version, this would call SomaFM API
        indie_songs = [
            ("Beach Fossils", "Sleep Apnea"),
            ("Wild Nothing", "Chinatown"),
            ("Craft Spells", "After the Moment"),
            ("DIIV", "Doused"),
            ("Alvvays", "Archie, Marry Me"),
            ("The Pains of Being Pure at Heart", "Young Adult Friction"),
            ("Real Estate", "Darling"),
            ("Mac DeMarco", "Chamber of Reflection"),
            ("Tame Impala", "The Less I Know The Better"),
            ("Unknown Mortal Orchestra", "Hunnybee")
        ]
        
        import random
        # Simulate 5 recent listens
        for _ in range(5):
            artist, track = random.choice(indie_songs)
            self.log_play(artist, track, source="SomaFM Indie Pop")

