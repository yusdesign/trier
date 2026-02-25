import json
import pandas as pd
from datetime import datetime

def generate_trier_dashboard():
    # Load results
    with open('../data/trier_results.json', 'r') as f:
        data = json.load(f)
    
    results = data['results']
    pattern_stats = data['pattern_stats']
    metrics = data['metrics']
    
    # Calculate metrics
    total_tx = len(results)
    high_risk = len([r for r in results if r['risk_level'] == 'HIGH'])
    medium_risk = len([r for r in results if r['risk_level'] == 'MEDIUM'])
    
    # Oriental pattern breakdown
    ru_pattern_high = len([r for r in results 
                          if r['merchant'] in ['RU Store', 'Unknown Store'] 
                          and r['location'] == 'RU'
                          and r['risk_level'] == 'HIGH'])
    
    cn_pattern_high = len([r for r in results 
                          if r['merchant'] in ['CN Store', 'Unknown Store'] 
                          and r['location'] == 'CN'
                          and r['risk_level'] == 'HIGH'])
    
    amazon_unusual = len([r for r in results 
                         if r['merchant'] == 'Amazon' 
                         and r['location'] in ['RU', 'CN']
                         and r['risk_level'] == 'HIGH'])
    
    walmart_unusual = len([r for r in results 
                          if r['merchant'] == 'Walmart' 
                          and r['location'] in ['RU', 'CN']
                          and r['risk_level'] == 'HIGH'])
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TRIER - Oriental Pattern Fraud Detector</title>
        <meta http-equiv="refresh" content="60">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #e0e0e0; }}
            .dashboard {{ max-width: 1400px; margin: 0 auto; }}
            .header {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 30px; border-radius: 15px; margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }}
            .header h1 {{ margin: 0; font-size: 2.5em; }}
            .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
            
            .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; }}
            
            .card {{ 
                background: #2d2d2d; 
                padding: 20px; 
                border-radius: 10px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                border-left: 4px solid #667eea;
            }}
            .card h3 {{ margin: 0 0 10px 0; color: #a0a0a0; font-size: 0.9em; text-transform: uppercase; }}
            .card .value {{ font-size: 32px; font-weight: bold; color: #fff; }}
            .card .trend {{ font-size: 14px; color: #4caf50; margin-top: 5px; }}
            
            .pattern-card {{ 
                background: #2d2d2d;
                border-left: 4px solid #ff6b6b;
            }}
            
            .pattern-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }}
            
            .pattern-box {{
                background: #2d2d2d;
                padding: 20px;
                border-radius: 10px;
                border-top: 4px solid #ffd93e;
            }}
            
            .pattern-box.ru {{ border-top-color: #ff6b6b; }}
            .pattern-box.cn {{ border-top-color: #ffd93e; }}
            
            .alerts-panel {{ 
                background: #2d2d2d; 
                padding: 20px; 
                border-radius: 10px; 
                margin-top: 20px;
            }}
            
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th {{ text-align: left; padding: 12px; background: #363636; color: #fff; }}
            td {{ padding: 12px; border-bottom: 1px solid #404040; }}
            
            .high {{ color: #ff6b6b; font-weight: bold; }}
            .medium {{ color: #ffd93e; }}
            .low {{ color: #6bff6b; }}
            
            .pattern-tag {{
                display: inline-block;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }}
            .tag-ru {{ background: #ff6b6b; color: white; }}
            .tag-cn {{ background: #ffd93e; color: black; }}
            .tag-amazon {{ background: #ff9900; color: black; }}
            .tag-walmart {{ background: #0071ce; color: white; }}
            
            .stats-row {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: #363636; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="header">
                <h1>🔍 TRIER - Oriental Pattern Fraud Detector</h1>
                <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Focus: RU/CN patterns | Amazon/Walmart unusual locations | Pattern-based rating system</p>
            </div>
            
            <div class="metrics-grid">
                <div class="card">
                    <h3>Total Transactions</h3>
                    <div class="value">{total_tx}</div>
                </div>
                <div class="card">
                    <h3>Total Volume</h3>
                    <div class="value">${sum(r['amount'] for r in results):,.2f}</div>
                </div>
                <div class="card pattern-card">
                    <h3>High Risk (Oriental Focus)</h3>
                    <div class="value">{high_risk}</div>
                    <div class="trend">{high_risk/total_tx*100:.1f}% of total</div>
                </div>
                <div class="card">
                    <h3>Precision/Recall</h3>
                    <div class="value">{metrics['precision']:.0%}</div>
                    <div class="trend">F1: {metrics['f1']:.2f}</div>
                </div>
            </div>
            
            <div class="pattern-grid">
                <div class="pattern-box ru">
                    <h3>🇷🇺 Russian Pattern Analysis</h3>
                    <div class="stats-row">
                        <span>RU Store transactions:</span>
                        <span class="high">{pattern_stats['RU_patterns']}</span>
                    </div>
                    <div class="stats-row">
                        <span>High risk RU patterns:</span>
                        <span class="high">{ru_pattern_high}</span>
                    </div>
                    <div class="stats-row">
                        <span>Unknown Store in RU:</span>
                        <span class="high">{len([r for r in results if r['merchant'] == 'Unknown Store' and r['location'] == 'RU' and r['risk_level'] == 'HIGH'])}</span>
                    </div>
                </div>
                
                <div class="pattern-box cn">
                    <h3>🇨🇳 Chinese Pattern Analysis</h3>
                    <div class="stats-row">
                        <span>CN Store transactions:</span>
                        <span class="medium">{pattern_stats['CN_patterns']}</span>
                    </div>
                    <div class="stats-row">
                        <span>High risk CN patterns:</span>
                        <span class="medium">{cn_pattern_high}</span>
                    </div>
                    <div class="stats-row">
                        <span>Unknown Store in CN:</span>
                        <span class="medium">{len([r for r in results if r['merchant'] == 'Unknown Store' and r['location'] == 'CN' and r['risk_level'] == 'HIGH'])}</span>
                    </div>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="card">
                    <h3>📦 Amazon Unusual Locations</h3>
                    <div class="value">{pattern_stats['Amazon_unusual']}</div>
                    <div class="trend">High risk: {amazon_unusual}</div>
                </div>
                <div class="card">
                    <h3>🛒 Walmart Unusual Locations</h3>
                    <div class="value">{pattern_stats['Walmart_unusual']}</div>
                    <div class="trend">High risk: {walmart_unusual}</div>
                </div>
                <div class="card">
                    <h3>🎯 Pattern Accuracy</h3>
                    <div class="value">{(ru_pattern_high + cn_pattern_high) / max(1, pattern_stats['RU_patterns'] + pattern_stats['CN_patterns']) * 100:.0f}%</div>
                    <div class="trend">Pattern detection rate</div>
                </div>
                <div class="card">
                    <h3>⚡ Avg Pattern Rating</h3>
                    <div class="value">{sum(r['pattern_rating'] for r in results)/len(results):.0f}</div>
                    <div class="trend">Base risk score</div>
                </div>
            </div>
            
            <div class="alerts-panel">
                <h2>🚨 High Risk Oriental Pattern Alerts</h2>
                <table>
                    <tr>
                        <th>Transaction</th>
                        <th>Merchant</th>
                        <th>Location</th>
                        <th>Amount</th>
                        <th>Pattern Rating</th>
                        <th>Risk Score</th>
                        <th>Category</th>
                    </tr>
    """
    
    # Add alerts (filter for oriental patterns)
    alerts = [r for r in results if r['risk_level'] == 'HIGH' 
              and r['pattern_category'] in ['russian', 'chinese']]
    
    for alert in alerts[:15]:
        category_tag = ""
        if alert['pattern_category'] == 'russian':
            category_tag = '<span class="pattern-tag tag-ru">RU</span>'
        elif alert['pattern_category'] == 'chinese':
            category_tag = '<span class="pattern-tag tag-cn">CN</span>'
        elif alert['merchant'] == 'Amazon':
            category_tag = '<span class="pattern-tag tag-amazon">Amazon</span>'
        elif alert['merchant'] == 'Walmart':
            category_tag = '<span class="pattern-tag tag-walmart">Walmart</span>'
        
        html += f"""
                    <tr>
                        <td>{alert['transaction_id']}</td>
                        <td>{alert['merchant']}</td>
                        <td>{alert['location']}</td>
                        <td>${alert['amount']:,.2f}</td>
                        <td class="high">{alert['pattern_rating']}</td>
                        <td class="high">{alert['risk_score']}</td>
                        <td>{category_tag}</td>
                    </tr>
        """
    
    html += """
                </table>
            </div>
            
            <div class="alerts-panel">
                <h2>📊 Pattern Rating Matrix (RU/CN Focus)</h2>
                <table>
                    <tr>
                        <th>Merchant</th>
                        <th>Location</th>
                        <th>Base Rating</th>
                        <th>Risk Level</th>
                        <th>Volume</th>
                    </tr>
    """
    
    # Add pattern matrix summary
    pattern_summary = {}
    for r in results:
        key = (r['merchant'], r['location'])
        if key not in pattern_summary:
            pattern_summary[key] = {
                'count': 0,
                'high_risk': 0,
                'avg_rating': 0,
                'total_amount': 0
            }
        pattern_summary[key]['count'] += 1
        if r['risk_level'] == 'HIGH':
            pattern_summary[key]['high_risk'] += 1
        pattern_summary[key]['avg_rating'] = (
            (pattern_summary[key]['avg_rating'] * (pattern_summary[key]['count'] - 1) + r['pattern_rating']) 
            / pattern_summary[key]['count']
        )
        pattern_summary[key]['total_amount'] += r['amount']
    
    # Sort by avg rating
    sorted_patterns = sorted(pattern_summary.items(), 
                           key=lambda x: x[1]['avg_rating'], 
                           reverse=True)[:10]
    
    for (merchant, location), stats in sorted_patterns:
        risk_color = 'high' if stats['avg_rating'] > 70 else 'medium' if stats['avg_rating'] > 40 else 'low'
        html += f"""
                    <tr>
                        <td>{merchant}</td>
                        <td>{location}</td>
                        <td class="{risk_color}">{stats['avg_rating']:.0f}</td>
                        <td>{stats['high_risk']}/{stats['count']}</td>
                        <td>${stats['total_amount']:,.0f}</td>
                    </tr>
        """
    
    html += """
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open('../docs/index.html', 'w') as f:
        f.write(html)
    
    print("✅ TRIER dashboard generated with oriental pattern focus")

if __name__ == "__main__":
    generate_trier_dashboard()
