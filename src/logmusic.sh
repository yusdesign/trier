#!/data/data/com.termux/files/usr/bin/bash
echo "🎵 What are you listening to?"
read -p "Artist: " artist
read -p "Track: " track

# Don't proceed if empty
if [ -z "$artist" ] || [ -z "$track" ]; then
    echo "❌ Both artist and track are required!"
    exit 1
fi

cd ~/trier/src
python -c "
from music_lab_collector import MusicLabCollector
c = MusicLabCollector()
c.log_play('$artist', '$track', source='manual')
"
echo "✅ Logged '$artist - $track'"
echo "📊 View at: https://yusdesign.github.io/trier/music.html"
