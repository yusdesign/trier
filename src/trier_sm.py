#!/usr/bin/env python
"""
🎵🔍 TRIER Session Manager
Runs everything needed for a LIVE website:
- Stream logger (music + fraud transactions)
- Dashboard generator (every 30 min)
- Git pusher (every 2 hours)
- All in one session!
"""

import subprocess
import time
import os
import signal
import sys
from datetime import datetime

class TrierSessionManager:
    def __init__(self):
        self.stream_logger = None
        self.last_dashboard = time.time()
        self.last_git_push = time.time()
        
        # Timing configuration
        self.dashboard_interval = 30 * 60  # 30 minutes
        self.git_push_interval = 2 * 60 * 60  # 2 hours (you asked for this!)
        
        self.running = True
        
    def log(self, msg):
        """Print with timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📍 {msg}")
    
    def start_stream_logger(self):
        """Start the unified logger with mpv stream"""
        self.log("🎧 Starting SomaFM stream + logger...")
    
        # Run the exact command that works!
        self.stream_logger = subprocess.Popen(
            'mpv https://ice1.somafm.com/indiepop-32-aac 2>&1 | python trier_unified_logger.py',
            shell=True,
            executable='/data/data/com.termux/files/usr/bin/bash',  # Termux bash
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        self.log("✅ Stream + Logger active - YOU SHOULD HEAR MUSIC NOW!")
   
    def generate_dashboards(self):
        """Update both dashboards"""
        self.log("📊 Generating dashboards...")
        
        # Fraud dashboard
        result = subprocess.run(["python", "trier_dashboard.py"], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            self.log("✅ Fraud dashboard updated")
        else:
            self.log(f"⚠️ Fraud dashboard error: {result.stderr[:100]}")
        
        # Music dashboard
        result = subprocess.run(["python", "music_dashboard.py"], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            self.log("✅ Music dashboard updated")
        else:
            self.log(f"⚠️ Music dashboard error: {result.stderr[:100]}")
        
        self.last_dashboard = time.time()
    
    def push_to_git(self):
        """Push all changes to GitHub"""
        self.log("🚀 Pushing to GitHub...")
        
        # Go to root directory
        os.chdir("..")
        
        # Add everything
        subprocess.run(["git", "add", "data/", "music/", "docs/"], 
                      capture_output=True)
        
        # Commit
        commit_msg = f"🤖 TRIER Live Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        result = subprocess.run(["git", "commit", "-m", commit_msg],
                               capture_output=True, text=True)
        
        if "nothing to commit" not in result.stderr:
            # Push
            push_result = subprocess.run(["git", "push"], 
                                        capture_output=True, text=True)
            if push_result.returncode == 0:
                self.log("✅ Pushed to GitHub! Website will update in 1-2 min")
            else:
                self.log(f"⚠️ Push failed: {push_result.stderr[:100]}")
        else:
            self.log("📊 No changes to push")
        
        # Go back to src
        os.chdir("src")
        self.last_git_push = time.time()
    
    def check_stream_logger(self):
        """Make sure logger is still running"""
        if self.stream_logger and self.stream_logger.poll() is not None:
            self.log("⚠️ Stream logger died, restarting...")
            self.start_stream_logger()
    
    def run(self):
        """Main loop"""
        self.log("="*60)
        self.log("🎵🔍 TRIER SESSION MANAGER")
        self.log(f"Dashboard updates: every {self.dashboard_interval//60} minutes")
        self.log(f"Git pushes: every {self.git_push_interval//3600} hours")
        self.log("="*60)
        
        # Start everything
        self.start_stream_logger()
        self.generate_dashboards()  # Initial dashboards
        
        # Handle Ctrl+C gracefully
        def signal_handler(sig, frame):
            self.log("\n👋 Shutting down TRIER Session...")
            if self.stream_logger:
                self.stream_logger.terminate()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Main loop
        while self.running:
            time.sleep(10)  # Check every 10 seconds
            
            # Check logger health
            self.check_stream_logger()
            
            # Time for new dashboards?
            if time.time() - self.last_dashboard > self.dashboard_interval:
                self.generate_dashboards()
            
            # Time for git push?
            if time.time() - self.last_git_push > self.git_push_interval:
                self.push_to_git()

if __name__ == "__main__":
    manager = TrierSessionManager()
    manager.run()
