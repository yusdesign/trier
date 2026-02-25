import json
import pandas as pd
from datetime import datetime

def generate_html_dashboard():
    # Load results
    with open('../data/fraud_results.json', 'r') as f:
        results = json.load(f)
    
    with open('../data/alerts.json', 'r') as f:
        alerts = json.load(f)
    
    # Calculate metrics
    total_tx = len(results)
    high_risk = len([r for r in results if r['risk_level'] == 'HIGH'])
    medium_risk = len([r for r in results if r['risk_level'] == 'MEDIUM'])
    total_amount = sum(r['amount'] for r in results)
    blocked_amount = sum(r['amount'] for r in results if r['action'] == 'BLOCK')
    
    # Top risky merchants
    merchant_risk = {}
    for r in results:
        if r['risk_level'] == 'HIGH':
            merchant_risk[r['merchant']] = merchant_risk.get(r['merchant'], 0) + 1
    
    top_merchants = sorted(merchant_risk.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fraud Detection Dashboard</title>
        <meta http-equiv="refresh" content="60">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .dashboard {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; }}
            .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .card h3 {{ margin: 0 0 10px 0; color: #666; }}
            .card .value {{ font-size: 32px; font-weight: bold; color: #2c3e50; }}
            .alert {{ background: #e74c3c; color: white; }}
            .warning {{ background: #f39c12; color: white; }}
            .alerts-panel {{ background: white; padding: 20px; border-radius: 10px; margin-top: 20px; }}
            .alert-item {{ padding: 10px; margin: 5px 0; background: #fef9e7; border-left: 4px solid #e74c3c; }}
            .timestamp {{ color: #666; font-size: 12px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ text-align: left; padding: 10px; background: #34495e; color: white; }}
            td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            .high {{ color: #e74c3c; font-weight: bold; }}
            .medium {{ color: #f39c12; }}
            .low {{ color: #27ae60; }}
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="header">
                <h1>🚨 Fraud Detection Dashboard</h1>
                <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="metrics-grid">
                <div class="card">
                    <h3>Total Transactions</h3>
                    <div class="value">{total_tx}</div>
                </div>
                <div class="card">
                    <h3>Total Volume</h3>
                    <div class="value">${total_amount:,.2f}</div>
                </div>
                <div class="card alert">
                    <h3>High Risk</h3>
                    <div class="value">{high_risk}</div>
                </div>
                <div class="card warning">
                    <h3>Medium Risk</h3>
                    <div class="value">{medium_risk}</div>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="card">
                    <h3>Blocked Amount</h3>
                    <div class="value">${blocked_amount:,.2f}</div>
                </div>
                <div class="card">
                    <h3>Fraud Rate</h3>
                    <div class="value">{(high_risk/total_tx*100):.1f}%</div>
                </div>
                <div class="card">
                    <h3>Active Alerts</h3>
                    <div class="value">{len(alerts)}</div>
                </div>
                <div class="card">
                    <h3>Top Risk Merchant</h3>
                    <div class="value">{top_merchants[0][0] if top_merchants else 'None'}</div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
                <div class="alerts-panel">
                    <h2>Recent High Risk Transactions</h2>
                    <table>
                        <tr>
                            <th>Transaction</th>
                            <th>Amount</th>
                            <th>Merchant</th>
                            <th>Risk Score</th>
                            <th>Rules</th>
                        </tr>
    """
    
    for alert in alerts[:10]:
        html += f"""
                        <tr>
                            <td>{alert['transaction_id']}</td>
                            <td>${alert['amount']:,.2f}</td>
                            <td>{alert['merchant']}</td>
                            <td class="high">{alert['risk_score']}</td>
                            <td>{', '.join(alert['rules_triggered'][:2])}</td>
                        </tr>
        """
    
    html += """
                    </table>
                </div>
                
                <div class="alerts-panel">
                    <h2>Risk Distribution</h2>
                    <div style="margin: 20px 0;">
                        <div style="background: #e74c3c; height: 20px; width: """ + str((high_risk/total_tx*100)) + """%;"></div>
                        <div style="background: #f39c12; height: 20px; width: """ + str((medium_risk/total_tx*100)) + """%;"></div>
                        <div style="background: #27ae60; height: 20px; width: """ + str(((total_tx-high_risk-medium_risk)/total_tx*100)) + """%;"></div>
                    </div>
                    
                    <h2>Top Risky Merchants</h2>
                    <table>
                        <tr>
                            <th>Merchant</th>
                            <th>Fraud Count</th>
                        </tr>
    """
    
    for merchant, count in top_merchants:
        html += f"""
                        <tr>
                            <td>{merchant}</td>
                            <td class="high">{count}</td>
                        </tr>
        """
    
    html += """
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open('../docs/index.html', 'w') as f:
        f.write(html)
    
    print("✅ Dashboard generated at /docs/index.html")

if __name__ == "__main__":
    generate_html_dashboard()
