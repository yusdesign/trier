#!/usr/bin/env python
"""
TRIER Music Lab - Analyze your listening patterns
COMPLETE VERSION - No warnings, all features!
"""

import pandas as pd
import sqlite3
import json
from datetime import datetime, timedelta
import os

class MusicAnalyzer:
    def __init__(self):
        self.music_path = '../music/'
        self.plays = None
        self.artists = None
        self.discoveries = []
        
    def load_data(self):
        """Load all music data with explicit datetime handling"""
        try:
            # Read CSV first as strings
            csv_path = f'{self.music_path}plays.csv'
            if not os.path.exists(csv_path):
                print("⚠️ plays.csv not found, creating empty file")
                with open(csv_path, 'w') as f:
                    f.write('timestamp,artist,track,album,source,duration_seconds\n')
                self.plays = pd.DataFrame(columns=['timestamp', 'artist', 'track', 'album', 'source', 'duration_seconds'])
            else:
                self.plays = pd.read_csv(csv_path)
                
                # EXACT FORMAT for your timestamps (no more warnings!)
                if 'timestamp' in self.plays.columns and len(self.plays) > 0:
                    self.plays['timestamp'] = pd.to_datetime(
                        self.plays['timestamp'],
                        format='%Y-%m-%dT%H:%M:%S.%f',  # Your exact format: 2026-02-26T06:22:11.881696
                        errors='coerce'
                    )
                    
                    # Remove rows with invalid timestamps
                    initial_count = len(self.plays)
                    self.plays = self.plays.dropna(subset=['timestamp'])
                    if len(self.plays) < initial_count:
                        print(f"⚠️ Dropped {initial_count - len(self.plays)} rows with invalid timestamps")
            
        except Exception as e:
            print(f"❌ Error loading plays.csv: {e}")
            self.plays = pd.DataFrame(columns=['timestamp', 'artist', 'track', 'album', 'source', 'duration_seconds'])
        
        # Load artists database
        try:
            db_path = f'{self.music_path}artists.db'
            conn = sqlite3.connect(db_path)
            self.artists = pd.read_sql_query("SELECT * FROM artists", conn)
            conn.close()
        except Exception as e:
            print(f"❌ Error loading artists: {e}")
            self.artists = pd.DataFrame(columns=['artist_id', 'name', 'play_count', 'first_heard', 'last_heard'])
        
        # Load discoveries
        try:
            disc_path = f'{self.music_path}discoveries.json'
            if os.path.exists(disc_path):
                with open(disc_path, 'r') as f:
                    self.discoveries = json.load(f)
            else:
                self.discoveries = []
        except Exception as e:
            print(f"❌ Error loading discoveries: {e}")
            self.discoveries = []
        
        print(f"✅ Loaded {len(self.plays)} plays, {len(self.artists)} artists")
        if len(self.plays) > 0:
            print(f"📅 Timestamp dtype: {self.plays['timestamp'].dtype}")
            print(f"📅 First timestamp: {self.plays['timestamp'].iloc[0]}")
    
    def analyze_taste(self):
        """Generate music taste insights"""
        
        if len(self.plays) == 0:
            return {
                'total_plays': 0,
                'unique_artists': 0,
                'unique_tracks': 0,
                'top_artists': {},
                'daily_average': 0,
                'recent_favorites': {},
                'new_discoveries': 0,
                'favorite_day': None,
                'most_active_hour': 12
            }
        
        # Top artists
        top_artists = self.plays['artist'].value_counts().head(10)
        
        # Listening over time
        self.plays['date'] = self.plays['timestamp'].dt.date
        daily_plays = self.plays.groupby('date').size()
        
        # Recent favorites (last 7 days)
        recent = self.plays[self.plays['timestamp'] > datetime.now() - timedelta(days=7)]
        recent_faves = recent['artist'].value_counts().head(5) if len(recent) > 0 else pd.Series()
        
        # New discoveries this week
        new_this_week = [d for d in self.discoveries 
                        if datetime.fromisoformat(d['discovered_at']) > 
                           datetime.now() - timedelta(days=7)]
        
        # Most active hour
        if len(self.plays) > 0:
            most_active_hour = self.plays['timestamp'].dt.hour.mode()[0]
        else:
            most_active_hour = 12
        
        return {
            'total_plays': len(self.plays),
            'unique_artists': self.plays['artist'].nunique(),
            'unique_tracks': len(self.plays),
            'top_artists': top_artists.to_dict(),
            'daily_average': daily_plays.mean() if len(daily_plays) > 0 else 0,
            'recent_favorites': recent_faves.to_dict(),
            'new_discoveries': len(new_this_week),
            'favorite_day': str(daily_plays.idxmax()) if len(daily_plays) > 0 else None,
            'most_active_hour': most_active_hour
        }
    
    def get_artist_depth(self, artist):
        """How deep is your love for an artist?"""
        artist_plays = self.plays[self.plays['artist'] == artist]
        
        if len(artist_plays) == 0:
            return {
                'artist': artist,
                'total_plays': 0,
                'unique_tracks': 0,
                'first_heard': None,
                'last_heard': None,
                'favorite_track': None
            }
        
        return {
            'artist': artist,
            'total_plays': len(artist_plays),
            'unique_tracks': artist_plays['track'].nunique(),
            'first_heard': artist_plays['timestamp'].min(),
            'last_heard': artist_plays['timestamp'].max(),
            'favorite_track': artist_plays['track'].mode()[0] if len(artist_plays) > 0 else None
        }
    
    def get_listening_timeline(self):
        """Get hourly listening distribution"""
        if len(self.plays) == 0:
            return {}
        
        return self.plays['timestamp'].dt.hour.value_counts().sort_index().to_dict()
    
    def get_daily_timeline(self):
        """Get daily listening distribution"""
        if len(self.plays) == 0:
            return {}
        
        return self.plays.groupby(self.plays['timestamp'].dt.date).size().to_dict()

if __name__ == "__main__":
    # Quick test
    analyzer = MusicAnalyzer()
    analyzer.load_data()
    taste = analyzer.analyze_taste()
    
    print("\n🎵 Quick Music Profile:")
    print(f"   Total plays: {taste['total_plays']}")
    print(f"   Unique artists: {taste['unique_artists']}")
    print(f"   Top artist: {list(taste['top_artists'].keys())[0] if taste['top_artists'] else 'None'}")
    print(f"   New discoveries this week: {taste['new_discoveries']}")
