#!/usr/bin/env python
"""
🎵🔍 TRIER Unified Logger
Listens to SomaFM stream and updates BOTH databases:
- music/artists.db & plays.csv (your music taste)
- data/users.db & transactions.csv (fraud patterns)
"""

import sys
import re
import csv
import sqlite3
import os
import json
from datetime import datetime, timedelta
import random  # for demo fraud patterns

class TrierUnifiedLogger:
    def __init__(self):
        # Paths
        self.music_path = '../music/'
        self.data_path = '../data/'
        
        # Initialize all databases
        self.ensure_all_files()
        
        # Track state
        self.last_song = None
        self.last_song_time = None
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def ensure_all_files(self):
        """Create all necessary files if missing"""
        
        # ===== MUSIC LAB FILES =====
        os.makedirs(self.music_path, exist_ok=True)
        
        # plays.csv
        plays_csv = f'{self.music_path}plays.csv'
        if not os.path.exists(plays_csv):
            with open(plays_csv, 'w') as f:
                f.write('timestamp,artist,track,album,source,duration_seconds\n')
        
        # artists.db
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
        
        # discoveries.json
        discoveries = f'{self.music_path}discoveries.json'
        if not os.path.exists(discoveries):
            with open(discoveries, 'w') as f:
                json.dump([], f)
        
        # ===== FRAUD DETECTION FILES =====
        os.makedirs(self.data_path, exist_ok=True)
        
        # transactions.csv (for fraud detector)
        tx_csv = f'{self.data_path}transactions.csv'
        if not os.path.exists(tx_csv):
            with open(tx_csv, 'w') as f:
                f.write('transaction_id,user_id,amount,merchant,location,device_id,timestamp,is_actual_fraud\n')
        
        # users.db
        conn = sqlite3.connect(f'{self.data_path}users.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                email TEXT,
                country TEXT,
                account_age_days INTEGER,
                risk_score REAL,
                is_vip INTEGER
            )
        ''')
        # Add some demo users if none exist
        cur = conn.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            for i in range(1, 101):
                conn.execute('''
                    INSERT INTO users (user_id, email, country, account_age_days, risk_score, is_vip)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (i, f'user{i}@example.com', 
                      random.choice(['US', 'UK', 'CA', 'AU']),
                      random.randint(1, 365),
                      round(random.random(), 2),
                      random.choice([0, 1])))
        conn.commit()
        conn.close()
        
        # historical_frauds.csv
        hist_csv = f'{self.data_path}historical_frauds.csv'
        if not os.path.exists(hist_csv):
            with open(hist_csv, 'w') as f:
                f.write('transaction_id,user_id,amount,merchant,location,device_id,timestamp,fraud_type\n')
    
    def parse_icy_title(self, line):
        """Extract artist and track from 'icy-title: Artist - Song'"""
        match = re.search(r'icy-title:\s*(.+?)\s*-\s*(.+)', line)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return None, None
    
    def update_music_db(self, artist, track):
        """Update music/artists.db and plays.csv"""
        timestamp = datetime.now()
        
        # 1. Append to plays.csv
        with open(f'{self.music_path}plays.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp.isoformat(),
                artist,
                track,
                '',  # album
                'SomaFM Indie Pop',
                180  # default duration
            ])
        
        # 2. Update artist database
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
            """, (timestamp.date().isoformat(), artist))
        else:
            # New artist discovery!
            conn.execute("""
                INSERT INTO artists (name, play_count, first_heard, last_heard)
                VALUES (?, 1, ?, ?)
            """, (artist, timestamp.date().isoformat(), timestamp.date().isoformat()))
            
            # Log discovery
            self.log_discovery(artist, track)
        
        conn.commit()
        conn.close()
    
    def log_discovery(self, artist, track):
        """Record new artist discovery"""
        with open(f'{self.music_path}discoveries.json', 'r') as f:
            discoveries = json.load(f)
        
        discoveries.append({
            'artist': artist,
            'track': track,
            'discovered_at': datetime.now().isoformat(),
            'source': 'SomaFM Indie Pop'
        })
        
        with open(f'{self.music_path}discoveries.json', 'w') as f:
            json.dump(discoveries[-100:], f, indent=2)
    
    def update_fraud_db(self, artist, track):
        """
        Update fraud detection databases based on music patterns
        This is where music meets fraud detection!
        """
        timestamp = datetime.now()
        
        # Create a "transaction" from the music play
        # This simulates how your music taste could relate to fraud patterns
        
        # Generate a transaction ID
        tx_id = f"TX_MUSIC_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # Map artists to merchants (for fun!)
        merchant_map = {
            # Indie pop → Amazon (common)
            'Caroline': 'Amazon',
            'Radical': 'Amazon',
            'Mary': 'Amazon',
            'Blondfire': 'Amazon',
            'Wild Belle': 'Amazon',
            'Hovvdy': 'Amazon',
            # Default
            'default': random.choice(['Amazon', 'Walmart', 'Target', 'Spotify'])
        }
        
        # Find which merchant this artist maps to
        merchant = 'Spotify'  # Default
        for key in merchant_map:
            if key.lower() in artist.lower():
                merchant = merchant_map[key]
                break
        
        # Location based on artist origin (simulated)
        location_map = {
            'Caroline': 'US',      # Caroline Rose - US
            'Radical': 'US',       # Radical Face - US
            'Mary': 'SE',          # Mary Onettes - Sweden
            'Blondfire': 'US',     # Blondfire - US
            'Wild Belle': 'US',    # Wild Belle - US
            'Hovvdy': 'US',        # Hovvdy - US
            'Duane': 'US'          # Duane Hoover - US
        }
        
        location = 'US'
        for key in location_map:
            if key.lower() in artist.lower():
                location = location_map[key]
                break
        
        # Generate a "transaction" from this music play
        transaction = {
            'transaction_id': tx_id,
            'user_id': random.randint(1, 100),  # Random user
            'amount': round(random.uniform(10, 150), 2),  # Small amount like music purchase
            'merchant': merchant,
            'location': location,
            'device_id': f'DEV_MUSIC_{random.randint(100, 999)}',
            'timestamp': timestamp.isoformat(),
            'is_actual_fraud': 0  # Most music transactions are legit
        }
        
        # Append to transactions.csv
        with open(f'{self.data_path}transactions.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([
                transaction['transaction_id'],
                transaction['user_id'],
                transaction['amount'],
                transaction['merchant'],
                transaction['location'],
                transaction['device_id'],
                transaction['timestamp'],
                transaction['is_actual_fraud']
            ])
        
        # Also log to a music-transactions log for fun
        log_file = f'{self.data_path}music_transactions.log'
        with open(log_file, 'a') as f:
            f.write(f"{timestamp.isoformat()}|{artist}|{track}|${transaction['amount']}|{merchant}|{location}\n")
        
        return transaction
    
    def log_song(self, artist, track):
        """Log song to ALL databases"""
        timestamp = datetime.now()
        song_key = f"{artist} - {track}"
        
        # Avoid duplicates (same song within 30 seconds)
        if song_key == self.last_song and self.last_song_time:
            if (timestamp - self.last_song_time).seconds < 30:
                return
        
        # Update music database
        self.update_music_db(artist, track)
        
        # Update fraud database (create a transaction)
        tx = self.update_fraud_db(artist, track)
        
        # Update state
        self.last_song = song_key
        self.last_song_time = timestamp
        
        # Print unified log
        print(f"🎵 [{timestamp.strftime('%H:%M:%S')}] {artist} - {track}")
        print(f"   💳 Transaction: ${tx['amount']} at {tx['merchant']} ({tx['location']})")
        print(f"   📊 Music DB + Fraud DB updated")
    
    def run(self):
        """Read from stdin and log to all databases"""
        print("="*60)
        print("🎵🔍 TRIER UNIFIED LOGGER")
        print(f"Session: {self.session_id}")
        print("="*60)
        print("Listening to SomaFM Indie Pop...")
        print("Updating BOTH music and fraud databases")
        print("-"*60)
        
        for line in sys.stdin:
            artist, track = self.parse_icy_title(line)
            if artist and track:
                self.log_song(artist, track)

if __name__ == "__main__":
    logger = TrierUnifiedLogger()
    try:
        logger.run()
    except KeyboardInterrupt:
        print("\n" + "="*60)
        print("👋 TRIER Unified Logger stopped")
        print("Check your databases:")
        print("  🎵 music/artists.db")
        print("  🎵 music/plays.csv")
        print("  🔍 data/transactions.csv")
        print("  🔍 data/users.db")
        print("="*60)
