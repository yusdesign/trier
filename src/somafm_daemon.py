#!/usr/bin/env python
import time
import schedule
from somafm_collector import SomaFMBehaviorCollector

class SomaFMDaemon:
    def __init__(self):
        self.collector = SomaFMBehaviorCollector()
        self.current_song = None
        
    def check_and_log(self):
        """Check SomaFM every minute, log if song changed"""
        current = self.collector.fetch_current_song()
        
        if current:
            song_id = f"{current['artist']} - {current['title']}"
            
            if song_id != self.current_song:
                print(f"📻 {song_id}")
                
                # Log to your CSV
                with open('../music/live_stream.csv', 'a') as f:
                    f.write(f"{datetime.now().isoformat()},{song_id}\n")
                
                self.current_song = song_id
    
    def run_forever(self):
        """Run continuously, checking every 30 seconds"""
        print("🎧 SomaFM Behavior Daemon Started")
        print("Logging every song you hear...")
        
        schedule.every(30).seconds.do(self.check_and_log)
        
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    daemon = SomaFMDaemon()
    daemon.run_forever()
