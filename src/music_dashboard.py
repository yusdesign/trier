#!/usr/bin/env python
"""
Generate TRIER Music Lab Dashboard
"""

from music_analyzer import MusicAnalyzer
from datetime import datetime
import pandas as pd

def generate_music_dashboard():
    analyzer = MusicAnalyzer()
    analyzer.load_data()
    taste = analyzer.analyze_taste()
    
    # Recent discoveries
    discoveries = analyzer.discoveries[-10:] if analyzer.discoveries else []
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TRIER Music Lab 🎵</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; 
                   background: #1a1a1a; color: #e0e0e0; }}
            .dashboard {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                      padding: 30px; border-radius: 15px; margin-bottom: 30px; }}
            .nav {{ display: flex; gap: 20px; margin-bottom: 20px; }}
            .nav a {{ color: white; text-decoration: none; padding: 10px 20px; 
                     background: #2d2d2d; border-radius: 5px; }}
            .nav a:hover {{ background: #404040; }}
            .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }}
            .card {{ background: #2d2d2d; padding: 20px; border-radius: 10px; 
                    border-left: 4px solid #1db954; }}
            .value {{ font-size: 32px; font-weight: bold; color: #1db954; }}
            .section {{ background: #2d2d2d; padding: 20px; border-radius: 10px; margin-top: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #404040; }}
            .discovery {{ background: #363636; padding: 10px; margin: 5px 0; 
                         border-left: 4px solid #ffd93e; }}
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="header">
                <h1>🎵 TRIER Music Lab</h1>
                <p>Your personal music analytics • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                <div class="nav">
                    <a href="index.html">🔍 Fraud Detector</a>
                    <a href="music.html" style="background: #1db954;">🎵 Music Lab</a>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="card">
                    <h3>Total Plays</h3>
                    <div class="value">{taste['total_plays']}</div>
                </div>
                <div class="card">
                    <h3>Unique Artists</h3>
                    <div class="value">{taste['unique_artists']}</div>
                </div>
                <div class="card">
                    <h3>Daily Average</h3>
                    <div class="value">{taste['daily_average']:.1f}</div>
                </div>
                <div class="card">
                    <h3>New Discoveries</h3>
                    <div class="value">{taste['new_discoveries']}</div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
                <div class="section">
                    <h2>🎤 Top Artists</h2>
                    <table>
                        <tr><th>Artist</th><th>Plays</th></tr>
    """
    
    for artist, count in list(taste['top_artists'].items())[:10]:
        html += f"<tr><td>{artist}</td><td>{count}</td></tr>"
    
    html += """
                    </table>
                </div>
                
                <div class="section">
                    <h2>✨ Recent Discoveries</h2>
    """
    
    for d in discoveries[::-1][:5]:  # Show newest first
        html += f"""
            <div class="discovery">
                <strong>{d['artist']}</strong><br>
                {d['track']}<br>
                <small>{d['discovered_at'][:10]}</small>
            </div>
        """
    
    html += f"""
                </div>
            </div>
            
            <div class="section">
                <h2>🎯 Your Music Profile</h2>
                <p>You listen most at {taste['most_active_hour']}:00</p>
                <p>Favorite day: {taste['favorite_day']}</p>
                <p>You've discovered {taste['new_discoveries']} new artists this week</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open('../docs/music.html', 'w') as f:
        f.write(html)
    
    # Also add link to main dashboard
    with open('../docs/index.html', 'r') as f:
        main_dash = f.read()
    
    # Add Music Lab link to main dashboard if not present
    if 'Music Lab' not in main_dash:
        nav_link = '<div class="nav" style="margin-bottom: 20px;"><a href="music.html" style="background: #1db954; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">🎵 Visit Music Lab</a></div>'
        main_dash = main_dash.replace('<div class="header">', f'<div class="header">{nav_link}')
        
        with open('../docs/index.html', 'w') as f:
            f.write(main_dash)
    
    print("✅ Music Lab dashboard generated at docs/music.html")

if __name__ == "__main__":
    generate_music_dashboard()
