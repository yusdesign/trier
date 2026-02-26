#!/usr/bin/env python
"""
🎵🔍 TRIER Live Logger
- Runs forever, auto-reconnects on interruptions
- Logs to both music and fraud databases
- Pushes to git periodically
- Survives phone calls, network drops, everything!
"""

import subprocess
import sys
import time
import os
from datetime import datetime
import signal

class TrierLiveLogger:
    def __init__(self):
        self.stream_url = "https://ice1.somafm.com/indiepop-32-aac"
        self.logger_script = "trier_unified_logger.py"
        self.git_push_interval = 300  # Push every 5 minutes
        self.last_push = time.time()
        self.running = True
        
    def log(self, msg):
        """Print with timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def push_to_git(self):
        """Push changes to GitHub"""
        try:
            # Add all changed files
            subprocess.run(["git", "-C", "..", "add", "data/", "music/", "docs/"], 
                         capture_output=True)
            
            # Commit
            result = subprocess.run(
                ["git", "-C", "..", "commit", "-m", f"🤖 Auto-update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
                capture_output=True
            )
            
            if "nothing to commit" not in result.stderr.decode():
                # Push
                subprocess.run(["git", "-C", "..", "push"], capture_output=True)
                self.log("🚀 Pushed to GitHub")
            else:
                self.log("📊 No changes to push")
                
        except Exception as e:
            self.log(f"⚠️ Git push failed: {e}")
    
    def run_stream(self):
        """Run the stream with auto-reconnect"""
        while self.running:
            try:
                self.log("🎧 Starting SomaFM stream...")
                
                # Start mpv and pipe to logger
                mpv_process = subprocess.Popen(
                    ["mpv", self.stream_url],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                # Start logger process (reads from mpv's stdout)
                logger_process = subprocess.Popen(
                    ["python", self.logger_script],
                    stdin=mpv_process.stdout,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                # Monitor both processes
                while self.running:
                    # Check if processes are still running
                    if mpv_process.poll() is not None:
                        self.log("⚠️ MPV stopped, reconnecting...")
                        break
                    
                    if logger_process.poll() is not None:
                        self.log("⚠️ Logger stopped, restarting...")
                        break
                    
                    # Periodic git push
                    if time.time() - self.last_push > self.git_push_interval:
                        self.push_to_git()
                        self.last_push = time.time()
                    
                    time.sleep(1)
                
                # Clean up
                mpv_process.terminate()
                logger_process.terminate()
                time.sleep(2)
                
            except KeyboardInterrupt:
                self.log("👋 Stopping TRIER Live Logger")
                self.running = False
                break
                
            except Exception as e:
                self.log(f"❌ Error: {e}, reconnecting in 10 seconds...")
                time.sleep(10)
    
    def run(self):
        """Main loop"""
        self.log("="*60)
        self.log("🎵🔍 TRIER LIVE LOGGER")
        self.log("Auto-reconnects on interruptions")
        self.log(f"Git push every {self.git_push_interval//60} minutes")
        self.log("="*60)
        
        # Handle Ctrl+C gracefully
        def signal_handler(sig, frame):
            self.log("\n👋 Shutting down...")
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Start streaming
        self.run_stream()

if __name__ == "__main__":
    logger = TrierLiveLogger()
    logger.run()
