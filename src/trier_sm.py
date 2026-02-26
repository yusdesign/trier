#!/usr/bin/env python
"""
🎵🔍 TRIER SESSION MANAGER - With Live Stream Priority!
"""

import subprocess
import time
import os
import signal
import sys
import threading
import json
import pandas as pd
from datetime import datetime

class TrierSessionManager:
    def __init__(self):
        self.stream_logger = None
        self.last_dashboard = time.time()
        self.last_git_push = time.time()
        
        self.dashboard_interval = 30 * 60  # 30 minutes
        self.git_push_interval = 2 * 60 * 60  # 2 hours
        
        self.running = True
        self.stream_started = False
        
    def log(self, msg):
        """Print with timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📍 {msg}")
    
    def start_stream_logger(self):
        """Start the unified logger with mpv stream and SHOW LIVE OUTPUT"""
        self.log("🎧 Starting SomaFM stream + logger...")
        
        self.stream_logger = subprocess.Popen(
            'mpv --volume=50 https://ice1.somafm.com/indiepop-32-aac 2>&1 | python -u trier_unified_logger.py',
            shell=True,
            executable='/data/data/com.termux/files/usr/bin/bash',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0,
            universal_newlines=True
        )
        
        self.log("✅ Stream + Logger active - LIVE OUTPUT:")
        self.log("-" * 60)
        
        def print_output():
            for line in self.stream_logger.stdout:
                print(line, end='')
                sys.stdout.flush()
        
        self.stream_thread = threading.Thread(target=print_output, daemon=True)
        self.stream_thread.start()
        self.stream_started = True
        
        # Give stream a moment to start producing output
        time.sleep(5)
    
    def generate_dashboards(self):
        """Update both dashboards WITHOUT blocking stream"""
        self.log("📊 Generating dashboards (stream continues in background)...")
        self.log("-" * 40)
        
        # STEP 1: Run fraud detector
        self.log("🔍 Step 1: Running fraud detector...")
        try:
            fraud_result = subprocess.run(
                ["python", "trier_fraud_detector.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if fraud_result.returncode == 0:
                self.log("✅ Fraud detector completed")
                # Show just the key results
                for line in fraud_result.stdout.split('\n'):
                    if 'True Positives:' in line or 'Precision:' in line:
                        print(f"     {line.strip()}")
            else:
                self.log(f"⚠️ Fraud detector error")
                
        except Exception as e:
            self.log(f"⚠️ Fraud detector exception: {e}")
        
        # STEP 2: Generate fraud dashboard
        self.log("📈 Step 2: Generating fraud dashboard...")
        try:
            subprocess.run(["python", "trier_dashboard.py"], 
                         capture_output=True, text=True)
            self.log("✅ Fraud dashboard updated")
        except Exception as e:
            self.log(f"⚠️ Fraud dashboard error: {e}")
        
        # STEP 3: Generate music dashboard
        self.log("🎵 Step 3: Generating music dashboard...")
        try:
            music_result = subprocess.run(
                ["python", "music_dashboard.py"],
                capture_output=True,
                text=True
            )
            if music_result.returncode == 0:
                self.log("✅ Music dashboard updated")
                # Show play count
                for line in music_result.stdout.split('\n'):
                    if "✅ Loaded" in line and "plays" in line:
                        print(f"     {line.strip()}")
            else:
                self.log(f"⚠️ Music dashboard error")
        except Exception as e:
            self.log(f"⚠️ Music dashboard exception: {e}")
        
        # STEP 4: Show summary
        self.log("\n📊 Step 4: Quick Stats")
        self.log(f"     Fraud: {self.get_fraud_stats()}")
        self.log(f"     Music: {self.get_music_stats()}")
        self.log("-" * 40)
        
        self.last_dashboard = time.time()
    
    def get_fraud_stats(self):
        """Get quick fraud stats"""
        try:
            with open('../data/trier_results.json', 'r') as f:
                data = json.load(f)
                metrics = data.get('metrics', {})
                return f"P:{metrics.get('precision', 0)*100:.0f}% R:{metrics.get('recall', 0)*100:.0f}%"
        except:
            return "No data"
    
    def get_music_stats(self):
        """Get quick music stats"""
        try:
            df = pd.read_csv('../music/plays.csv')
            return f"{len(df)} plays, {df['artist'].nunique()} artists"
        except:
            return "No data"
    
    def push_to_git(self):
        """Push all changes to GitHub"""
        self.log("🚀 Pushing to GitHub...")
        
        os.chdir("..")
        
        subprocess.run(["git", "add", "data/", "music/", "docs/"], 
                      capture_output=True)
        
        commit_msg = f"🤖 TRIER Live Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        result = subprocess.run(["git", "commit", "-m", commit_msg],
                               capture_output=True, text=True)
        
        if "nothing to commit" not in result.stderr:
            push_result = subprocess.run(["git", "push"], 
                                        capture_output=True, text=True)
            if push_result.returncode == 0:
                self.log("✅ Pushed to GitHub! Website updates in 1-2 min")
            else:
                self.log(f"⚠️ Push failed")
        else:
            self.log("📊 No changes to push")
        
        os.chdir("src")
        self.last_git_push = time.time()
    
    def run(self):
        """Main loop"""
        self.log("="*60)
        self.log("🎵🔍 TRIER SESSION MANAGER")
        self.log(f"Dashboard updates: every {self.dashboard_interval//60} minutes")
        self.log(f"Git pushes: every {self.git_push_interval//3600} hours")
        self.log("="*60)
        
        # Start stream FIRST - it will show live output
        self.start_stream_logger()
        
        # Wait a bit for stream to stabilize
        time.sleep(3)
        
        # NOW do initial dashboards (stream continues in background)
        self.generate_dashboards()
        
        def signal_handler(sig, frame):
            self.log("\n👋 Shutting down TRIER Session...")
            if self.stream_logger:
                self.stream_logger.terminate()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Main loop - stream output continues via thread
        while self.running:
            for _ in range(60):  # Check every second but sleep in small chunks
                if not self.running:
                    break
                time.sleep(1)
            
            # Check if it's time for dashboards (stream continues printing)
            if time.time() - self.last_dashboard > self.dashboard_interval:
                self.generate_dashboards()
            
            # Check if it's time for git push
            if time.time() - self.last_git_push > self.git_push_interval:
                self.push_to_git()

if __name__ == "__main__":
    manager = TrierSessionManager()
    manager.run()
