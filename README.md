
### 🔍 TRIER, “Orient”, Pattern Fraud Detector

<div align="center">

![TRIER Banner](https://img.shields.io/badge/TRIER-Fraud%20Detector%20%26%20Music%20Lab-ffffff?style=for-the-badge&logo=github&logoColor=black)  

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-3.0.1-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-222222?style=flat-square&logo=github-pages&logoColor=white)](https://pages.github.com)  

[![🐳 DEEPSEEK](https://img.shields.io/badge/🐳-DEEPSEEK-4A6CF7?style=for-the-badge)](https://deepseek.com)  

[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)  
[![Last Commit](https://img.shields.io/github/last-commit/yusdesign/trier?style=flat-square&color=blue)](https://github.com/yusdesign/trier/commits)
[![Stars](https://img.shields.io/github/stars/yusdesign/trier?style=flat-square&color=yellow)](https://github.com/yusdesign/trier/stargazers)  

</div>

## 🎯 Overview

**TRIER** is a unified platform that combines:
- **🔍 Oriental Pattern Fraud Detection** - Specialized in RU/CN patterns
- **🎵 Music Lab** - Personal music analytics from SomaFM Indie Pop
- **📊 Live Dashboards** - Auto-updating GitHub Pages visualizations

## ✨ Features

| | Component | Description |
|---|-----------|-------------|
| 🔍 | **Fraud Detector** | Pattern-based risk scoring with oriental focus |
| 🎵 | **Music Lab** | Real-time SomaFM logging with artist discovery |
| 📈 | **Live Dashboards** | Auto-updating GitHub Pages with metrics |
| 🤖 | **Session Manager** | One script to stream, log, update, and push |
| 📱 | **Mobile Ready** | Works perfectly in Termux on Android |

## 📊 Live Dashboards

<div align="center">

| **Fraud Detector** | **Music Lab** |
|:---:|:---:|
| [![Fraud Dashboard](https://img.shields.io/badge/🔍-View%20Fraud%20Dashboard-ff6b6b?style=for-the-badge)](https://yusdesign.github.io/trier/) | [![Music Dashboard](https://img.shields.io/badge/🎵-View%20Music%20Lab-1db954?style=for-the-badge)](https://yusdesign.github.io/trier/music.html) |

</div>

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yusdesign/trier.git
cd trier

# Install dependencies
pip install pandas numpy requests

# Run the session manager (all-in-one!)
cd src
python trier_sm.py
```

📁 Project Structure

```
trier/
├── src/                    # All scripts
│   ├── trier_sm.py            # Main session manager
│   ├── trier_unified_logger.py # Stream logger
│   ├── trier_fraud_detector.py # Fraud detection
│   ├── music_analyzer.py       # Music taste analysis
│   └── ...
│
├── data/                   # Fraud detection data
│   ├── users.db            # User profiles
│   ├── transactions.csv    # Transaction history
│   └── historical_frauds.csv
│
├── music/                   # Music Lab data
│   ├── artists.db           # Artist database
│   ├── plays.csv            # Listening history
│   └── discoveries.json
│
├── docs/                    # GitHub Pages output
│   ├── index.html           # Fraud dashboard
│   └── music.html           # Music dashboard
│
└── .github/workflows/       # GitHub Actions
    └── daily-enrich.yml
```

🎯 Current Stats

<div align="center">

Metric Value
Total Transactions 1000+
Music Plays 106+
Unique Artists 95+
Last Updated 2026-02-26

</div>

🎵 Recent Music Discoveries

From your latest session:

· Ratatat - Lex
· Yo La Tengo - Sugarcube
· Throwing Muses - You're Clouds
· Wet Leg - Davina Mccall
· Alvvays - Next Of Kin
· They Might Be Giants - Answer
· Stars - Hold On When You Get Love
· Camera Obscura - Happy New Year
· Clap Your Hands Say Yeah - Details Of The War

📱 Termux Setup

```bash
pkg install python mpv
pip install pandas numpy requests
git clone https://github.com/yusdesign/trier.git
cd trier/src
python trier_sm.py
```

🌐 Auto-Updates

· Every 30 min → Dashboards regenerate
· Every 2 hours → Git push → Website updates
· GitHub Actions → Daily backup at 3 AM

🏆 Achievements

· ✅ 100+ plays in Music Lab
· ✅ 95+ artists discovered
· ✅ Real-time unified logging working
· ✅ Auto-push to GitHub every 2 hours
· ✅ Live dashboards on GitHub Pages

🤝 Contributing

Feel free to:

· 🐛 Report issues
· 💡 Suggest new patterns
· 🎵 Add more music stations
· 🔧 Improve detection algorithms

📜 License

MIT © yusdesign

---

<div align="center">

⭐ Star TRIER on GitHub! ⭐

https://img.shields.io/github/stars/yusdesign/trier?style=social

Live long and TRIER! 🖖

</div>
