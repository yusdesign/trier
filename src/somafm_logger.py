#!/usr/bin/env python
"""
Simple SomaFM Logger - Reads mpv output and logs songs
Run this alongside your mpv stream
"""

import subprocess
import re
import csv
import os
from datetime import datetime

class SomaFMLogger:
    def __init__(self):
        self.music_path = '../music/'
        self.ensure_csv()
        
    def ensure_csv(self):
        """Make sure plays.csv has correct headers"""
        if not os.path.exists(f'{self.music_path}plays.csv'):
            with open(f'{self.music_path}plays.csv', 'w') as f:
                f.write('timestamp,artist,track,album,source,duration_seconds\n')
    
    def parse_icy_title(self, line):
        """Extract artist and track from 'icy-title: Artist - Song'"""
        match = re.search(r'icy-title:\s*(.+?)\s*-\s*(.+)', line)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return None, None
    
    def log_song(self, artist, track):
        """Append song to plays.csv"""
        with open(f'{self.music_path}plays.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                artist,
                track,
                '',  # album
                'SomaFM Indie Pop',
                180  # default duration
            ])
        print(f"✅ Logged: {artist} - {track}")
    
    def follow_stream(self):
        """Read mpv output and log songs"""
        print("🎧 Listening for SomaFM songs...")
        print("(Make sure mpv is running in another session)")
        
        # This reads from terminal - in real use, you'd pipe mpv output
        # For now, we'll simulate by reading your visible output
        import sys
        print("\n📝 Paste the icy-title lines here (Ctrl+D to finish):")
        for line in sys.stdin:
            artist, track = self.parse_icy_title(line)
            if artist and track:
                self.log_song(artist, track)
                # Also add to music_lab_collector for artist tracking
                self.add_to_artist_db(artist, track)
    
    def add_to_artist_db(self, artist, track):
        """Also update the artist database"""
        from music_lab_collector import MusicLabCollector
        collector = MusicLabCollector()
        collector.log_play(artist, track, source='SomaFM Indie Pop')

if __name__ == "__main__":
    logger = SomaFMLogger()
    logger.follow_stream()
