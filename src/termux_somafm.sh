#!/data/data/com.termux/files/usr/bin/bash

echo "📱 SomaFM Indie Pop Mobile Listener"
echo "Press Ctrl+C to stop logging"

# Start playing SomaFM in background (requires mpv)
mpv https://ice1.somafm.com/indiepop-128-aac &

# Start logging daemon
python ~/trier/src/somafm_daemon.py &

echo "✅ Listening and logging..."
echo "Check your dashboard at: https://yusdesign.github.io/trier"

# Wait for user to stop
wait
