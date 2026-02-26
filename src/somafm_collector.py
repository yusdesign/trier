#!/usr/bin/env python
"""
SomaFM Indie Pop Behavior Collector
Captures every song you actually listen to in real-time
"""

import requests
import csv
import time
import os
from datetime import datetime
import json
import subprocess
import threading

class SomaFMBehaviorCollector:
    def __init__(self):
        self.station = "indiepop"
        # SomaFM provides JSON feeds of current songs
        self.metadata_url = f"https://api.somafm.com/songhistory.json?channel={self.station}"
        self.plays_file = '../music/somafm_plays.csv'
        self.current_song = None
        self.listening_session = []
        
        # Create file with headers if needed
        if not os.path.exists(self.plays_file):
            with open(self.plays_file, 'w') as f:
                f.write('timestamp,song_title,artist,album,station,listened_duration\n')
    
    def fetch_current_song(self):
        """Get what's currently playing on SomaFM Indie Pop"""
        try:
            response = requests.get(self.metadata_url)
            data = response.json()
            
            # Get the most recent song
            if data and 'songs' in data and len(data['songs']) > 0:
                latest = data['songs'][0]
                return {
                    'artist': latest.get('artist', 'Unknown'),
                    'title': latest.get('title', 'Unknown'),
                    'album': latest.get('album', 'Unknown'),
                    'timestamp': latest.get('played_at', datetime.now().isoformat())
                }
        except Exception as e:
            print(f"🔌 SomaFM connection hiccup: {e}")
        return None
    
    def listen_live(self, duration_minutes=60):
        """Listen and collect for a specified duration"""
        print(f"🎧 Tuning into SomaFM Indie Pop for {duration_minutes} minutes...")
        print("📻 Every song you hear will be logged")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        songs_heard = set()
        
        while datetime.now() < end_time:
            current = self.fetch_current_song()
            
            if current:
                song_key = f"{current['artist']} - {current['title']}"
                
                # New song started
                if song_key != self.current_song:
                    if self.current_song:
                        # Log the previous song
                        self.log_song(self.current_song, self.current_song_start)
                    
                    # Start tracking new song
                    self.current_song = song_key
                    self.current_song_start = datetime.now()
                    self.current_song_details = current
                    
                    print(f"🎵 Now playing: {song_key}")
                    
                    # First time hearing this song?
                    if song_key not in songs_heard:
                        songs_heard.add(song_key)
                        print(f"✨ New discovery!")
            
            time.sleep(10)  # Check every 10 seconds
        
        # Log the final song
        if self.current_song:
            self.log_song(self.current_song_details, self.current_song_start)
        
        print(f"\n✅ Listened to {len(songs_heard)} unique songs")
        return songs_heard
    
    def log_song(self, song_details, start_time):
        """Log a song with listening duration"""
        end_time = datetime.now()
        duration = (end_time - start_time).seconds
        
        with open(self.plays_file, 'a') as f:
            writer = csv.writer(f)
            writer.writerow([
                start_time.isoformat(),
                song_details['title'],
                song_details['artist'],
                song_details['album'],
                'SomaFM Indie Pop',
                duration
            ])
        
        print(f"  💾 Logged: {song_details['artist']} - {song_details['title']} ({duration}s)")
    
    def get_your_taste_profile(self):
        """Analyze your SomaFM listening patterns"""
        import pandas as pd
        from collections import Counter
        
        df = pd.read_csv(self.plays_file)
        
        # What you love (most listened)
        df['song_full'] = df['artist'] + ' - ' + df['song_title']
        top_played = df.groupby('song_full')['listened_duration'].sum().sort_values(ascending=False).head(10)
        
        # Artists you love
        top_artists = df.groupby('artist')['listened_duration'].sum().sort_values(ascending=False).head(10)
        
        # When you listen most
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        listening_time = df['hour'].value_counts().sort_index()
        
        # Your discoveries (songs you've heard multiple times)
        repeated = df['song_full'].value_counts()
        favorites = repeated[repeated > 1]
        
        return {
            'total_listening_minutes': df['listened_duration'].sum() / 60,
            'unique_songs': df['song_full'].nunique(),
            'unique_artists': df['artist'].nunique(),
            'top_songs': top_played.to_dict(),
            'top_artists': top_artists.to_dict(),
            'favorite_hour': listening_time.idxmax(),
            'favorites_you_replay': len(favorites)
        }

# Example usage
if __name__ == "__main__":
    collector = SomaFMBehaviorCollector()
    
    # Listen for 30 minutes and log everything
    collector.listen_live(duration_minutes=30)
    
    # See your taste profile
    profile = collector.get_your_taste_profile()
    print(f"\n🎯 Your Indie Pop Profile:")
    print(f"   You've listened to {profile['unique_songs']} unique songs")
    print(f"   Total: {profile['total_listening_minutes']:.0f} minutes")
    print(f"   You listen most around {profile['favorite_hour']}:00")
