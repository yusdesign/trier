import json
import os
from datetime import datetime

def update_dashboard_with_gists():
    """Add Gist links to the dashboard"""
    
    # Load existing dashboard
    dashboard_path = '../docs/index.html'
    gists_path = '../docs/gists.json'
    
    if not os.path.exists(dashboard_path):
        print("❌ Dashboard not found")
        return
    
    # Read existing dashboard
    with open(dashboard_path, 'r') as f:
        dashboard = f.read()
    
    # Load Gist links
    gists = []
    if os.path.exists(gists_path):
        with open(gists_path, 'r') as f:
            for line in f:
                try:
                    gists.append(json.loads(line))
                except:
                    continue
    
    # Get latest unique Gists (by filename)
    latest_gists = {}
    for gist in reversed(gists):
        if gist['filename'] not in latest_gists:
            latest_gists[gist['filename']] = gist
    
    # Create Gist gallery HTML
    gallery_html = '''
    <div class="alerts-panel" style="margin-top: 30px;">
        <h2>📋 TRIER Source Code & Data Gists</h2>
        <p>Click to view the latest versions on GitHub Gist:</p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 20px;">
    '''
    
    for filename, info in latest_gists.items():
        icon = "🐍" if filename.endswith('.py') else "📊" if 'results' in filename else "🚨"
        gallery_html += f'''
            <a href="{info['gist_url']}" target="_blank" style="text-decoration: none;">
                <div style="background: #363636; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea;">
                    <div style="font-size: 24px; margin-bottom: 5px;">{icon}</div>
                    <div style="color: white; font-weight: bold;">{filename}</div>
                    <div style="color: #a0a0a0; font-size: 12px; margin-top: 5px;">{info.get('description', '')[:60]}</div>
                    <div style="color: #4caf50; font-size: 10px; margin-top: 8px;">🕒 {info['created_at'][:10]}</div>
                </div>
            </a>
        '''
    
    gallery_html += '''
        </div>
    </div>
    '''
    
    # Insert gallery before closing body tag
    if '</body>' in dashboard:
        dashboard = dashboard.replace('</body>', gallery_html + '\n</body>')
        
        # Write updated dashboard
        with open(dashboard_path, 'w') as f:
            f.write(dashboard)
        
        print(f"✅ Dashboard updated with {len(latest_gists)} Gist links")
    else:
        print("❌ Could not find </body> tag in dashboard")

if __name__ == "__main__":
    update_dashboard_with_gists()
