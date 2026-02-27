#!/usr/bin/env python
"""
Generate OZON Real Data Dashboard
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

def load_real_metrics():
    """Load real OZON data"""
    metrics_file = Path('../real_data/ozon/ozon_metrics.json')
    with open(metrics_file, 'r') as f:
        return json.load(f)

def generate_html(metrics):
    """Generate dashboard HTML with real data"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🛒 OZON Real Fraud Data</title>
        <style>
            body {{ font-family: monospace; background: #1a1a1a; color: #e0e0e0; }}
            .dashboard {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #005bff; padding: 20px; border-radius: 10px; }}
            .stats {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 20px; margin: 20px 0; }}
            .card {{ background: #2d2d2d; padding: 20px; border-radius: 8px; }}
            .value {{ font-size: 2em; font-weight: bold; color: #005bff; }}
            .update {{ color: #888; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="header">
                <h1>🛒 OZON Real-Time Fraud Data</h1>
                <p>Pure real marketplace data - No synthetic</p>
            </div>
            
            <div class="stats">
                <div class="card">
                    <h3>Orders (24h)</h3>
                    <div class="value">{metrics['total_orders_24h']}</div>
                </div>
                <div class="card">
                    <h3>Fraud Alerts</h3>
                    <div class="value">{metrics['fraud_alerts_24h']}</div>
                </div>
                <div class="card">
                    <h3>Amount at Risk</h3>
                    <div class="value">₽{metrics['amount_at_risk']:,.0f}</div>
                </div>
                <div class="card">
                    <h3>Detection Rate</h3>
                    <div class="value">{metrics['detection_rate']*100:.0f}%</div>
                </div>
            </div>
            
            <div class="update">
                Last updated: {metrics['last_update']}
            </div>
        </div>
    </body>
    </html>
    """
    
    with open('../docs/ozon_dashboard.html', 'w') as f:
        f.write(html)
    
    print("✅ OZON real dashboard generated")

if __name__ == "__main__":
    metrics = load_real_metrics()
    generate_html(metrics)
