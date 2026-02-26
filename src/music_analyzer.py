#!/usr/bin/env python
"""
TRIER Music Lab - Analyze your listening patterns
"""

import pandas as pd
import sqlite3
import json
from datetime import datetime, timedelta
import os

class MusicAnalyzer:
    def __init__(self):
        self.music_path = '../music/'
        
    def load_data(self):
        """Load all music data with explicit datetime handling (pandas 3.0.1 compatible)"""
        try:
            # Read CSV first as strings
            self.plays = pd.read_csv(f'{self.music_path}plays.csv')
        
            # Modern pandas approach - use format mixing or explicit format
            try:
                # Try explicit format first (fastest)
                self.plays['timestamp'] = pd.to_datetime(
                    self.plays['timestamp'], 
                    format='%Y-%m-%dT%H:%M:%S.%f'  # Your ISO format with microseconds
                )
                print("✅ Parsed timestamps with ISO format")
            except (ValueError, TypeError):
                try:
                    # Fallback to mixed format (pandas 2.0+ way)
                    self.plays['timestamp'] = pd.to_datetime(
                        self.plays['timestamp'],
                        format='mixed'  # This replaces infer_datetime_format
                    )
                    print("✅ Parsed timestamps with mixed format")
                except (ValueError, TypeError):
                    # Ultimate fallback
                    self.plays['timestamp'] = pd.to_datetime(
                        self.plays['timestamp'],
                        errors='coerce'
                    )
                    print("⚠️ Used pandas coercion for timestamps")
        
            # Remove rows with invalid timestamps
            initial_count = len(self.plays)
            self.plays = self.plays.dropna(subset=['timestamp'])
            if len(self.plays) < initial_count:
                print(f"⚠️ Dropped {initial_count - len(self.plays)} rows with invalid timestamps")
        
        except Exception as e:
            print(f"❌ Error loading plays.csv: {e}")
            # Create empty DataFrame with correct columns
            self.plays = pd.DataFrame(columns=['timestamp', 'artist', 'track', 'album', 'source', 'duration_seconds'])
    
        # Connect to artist database
        try:
            conn = sqlite3.connect(f'{self.music_path}artists.db')
            self.artists = pd.read_sql_query("SELECT * FROM artists", conn)
            conn.close()
        except Exception as e:
            print(f"❌ Error loading artists: {e}")
            self.artists = pd.DataFrame(columns=['artist_id', 'name', 'play_count', 'first_heard', 'last_heard'])
    
        # Load discoveries
        try:
            with open(f'{self.music_path}discoveries.json', 'r') as f:
                self.discoveries = json.load(f)
        except:
            self.discoveries = []
    
        print(f"✅ Loaded {len(self.plays)} plays, {len(self.artists)} artists")
    
        # Verify timestamp column
        if len(self.plays) > 0:
            print(f"📅 Timestamp dtype: {self.plays['timestamp'].dtype}")
            if len(self.plays) > 0:
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
    
        return {
            'total_plays': len(self.plays),
            'unique_artists': self.plays['artist'].nunique(),
            'unique_tracks': len(self.plays),
            'top_artists': top_artists.to_dict(),
            'daily_average': daily_plays.mean() if len(daily_plays) > 0 else 0,
            'recent_favorites': recent_faves.to_dict(),
            'new_discoveries': len(new_this_week),
            'favorite_day': str(daily_plays.idxmax()) if len(daily_plays) > 0 else None,
            'most_active_hour': self.plays['timestamp'].dt.hour.mode()[0] if len(self.plays) > 0 else 12
        }
   
    def get_artist_depth(self, artist):
        """How deep is your love for an artist?"""
        artist_plays = self.plays[self.plays['artist'] == artist]
        
        return {
            'artist': artist,
            'total_plays': len(artist_plays),
            'unique_tracks': artist_plays['track'].nunique(),
            'first_heard': artist_plays['timestamp'].min(),
            'last_heard': artist_plays['timestamp'].max(),
            'favorite_track': artist_plays['track'].mode()[0] if len(artist_plays) > 0 else None
        }
