#!/usr/bin/env python
"""
TRIER Daily Enrichment
Runs fraud detector and updates dashboards
"""

import subprocess
import os
import sys
from datetime import datetime

def log(msg):
    """Print with timestamp"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 📍 {msg}")

def main():
    log("🔄 TRIER Daily Enrichment Started")
    log("=" * 40)
    
    # Step 1: Run fraud detector
    log("🔍 Step 1: Running fraud detector...")
    try:
        result = subprocess.run(
            [sys.executable, "trier_fraud_detector.py"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            log("✅ Fraud detector completed")
            # Show key metrics
            for line in result.stdout.split('\n'):
                if 'True Positives:' in line or 'Precision:' in line:
                    print(f"     {line.strip()}")
        else:
            log(f"⚠️ Fraud detector failed: {result.stderr[:200]}")
    except Exception as e:
        log(f"❌ Error: {e}")
    
    # Step 2: Generate fraud dashboard
    log("\n📈 Step 2: Generating fraud dashboard...")
    try:
        result = subprocess.run(
            [sys.executable, "trier_dashboard.py"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            log("✅ Fraud dashboard updated")
        else:
            log(f"⚠️ Dashboard failed: {result.stderr[:200]}")
    except Exception as e:
        log(f"❌ Error: {e}")
    
    # Step 3: Generate music dashboard
    log("\n🎵 Step 3: Generating music dashboard...")
    try:
        result = subprocess.run(
            [sys.executable, "music_dashboard.py"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            log("✅ Music dashboard updated")
            # Show play count
            for line in result.stdout.split('\n'):
                if "✅ Loaded" in line and "plays" in line:
                    print(f"     {line.strip()}")
        else:
            log(f"⚠️ Music dashboard failed: {result.stderr[:200]}")
    except Exception as e:
        log(f"❌ Error: {e}")
    
    log("=" * 40)
    log("✅ Daily enrichment complete!")

if __name__ == "__main__":
    main()
