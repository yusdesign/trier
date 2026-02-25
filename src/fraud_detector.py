import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

class SimpleFraudDetector:
    def __init__(self, data_path='../data/'):
        self.data_path = data_path
        self.load_data()
        
    def load_data(self):
        """Load all data sources (like Trino connectors)"""
        print("📊 Loading data sources...")
        
        # Load transactions (like Kafka/S3 in Trino)
        self.transactions = pd.read_csv(
            os.path.join(self.data_path, 'transactions.csv'),
            parse_dates=['timestamp']
        )
        
        # Load users from SQLite (like PostgreSQL in Trino)
        conn = sqlite3.connect(os.path.join(self.data_path, 'users.db'))
        self.users = pd.read_sql_query("SELECT * FROM users", conn)
        conn.close()
        
        # Load historical frauds (like S3 data lake in Trino)
        self.historical_frauds = pd.read_csv(
            os.path.join(self.data_path, 'historical_frauds.csv'),
            parse_dates=['timestamp']
        )
        
        print(f"✅ Loaded {len(self.transactions)} transactions")
        print(f"✅ Loaded {len(self.users)} users")
        print(f"✅ Loaded {len(self.historical_frauds)} historical frauds")
    
    def calculate_velocity(self, user_id, current_time, hours=24):
        """Calculate transaction velocity (like Trino window functions)"""
        time_threshold = current_time - timedelta(hours=hours)
        user_tx = self.transactions[
            (self.transactions['user_id'] == user_id) & 
            (self.transactions['timestamp'] > time_threshold)
        ]
        return len(user_tx), user_tx['amount'].sum()
    
    def check_fraud_patterns(self, merchant, location, device_id):
        """Check against historical fraud patterns"""
        # Look for similar frauds in history
        similar_frauds = self.historical_frauds[
            (self.historical_frauds['merchant'] == merchant) |
            (self.historical_frauds['location'] == location) |
            (self.historical_frauds['device_id'] == device_id)
        ]
        
        if len(similar_frauds) > 0:
            return {
                'pattern_matched': True,
                'similar_count': len(similar_frauds),
                'avg_amount': similar_frauds['amount'].mean(),
                'common_fraud_types': similar_frauds['fraud_type'].mode().tolist()[:3]
            }
        return {'pattern_matched': False, 'similar_count': 0}
    
    def score_transaction(self, transaction):
        """Score a single transaction (like Trino query)"""
        user = self.users[self.users['user_id'] == transaction['user_id']].iloc[0]
        
        # Calculate velocities
        tx_24h, amount_24h = self.calculate_velocity(
            transaction['user_id'], 
            transaction['timestamp'], 
            24
        )
        tx_1h, _ = self.calculate_velocity(
            transaction['user_id'], 
            transaction['timestamp'], 
            1
        )
        
        # Check fraud patterns
        patterns = self.check_fraud_patterns(
            transaction['merchant'],
            transaction['location'],
            transaction['device_id']
        )
        
        # Calculate risk score (0-100)
        risk_score = 0
        rules_triggered = []
        
        # Rule 1: New account + large amount
        if user['account_age_days'] < 7 and transaction['amount'] > 500:
            risk_score += 30
            rules_triggered.append('new_account_large_tx')
        
        # Rule 2: High velocity (>10 tx in 1h)
        if tx_1h > 10:
            risk_score += 25
            rules_triggered.append('high_velocity_1h')
        
        # Rule 3: Unusual amount (>3x normal)
        if tx_24h > 0 and transaction['amount'] > amount_24h * 0.5:  # >50% of daily total
            risk_score += 20
            rules_triggered.append('unusual_amount')
        
        # Rule 4: Known fraud pattern
        if patterns['pattern_matched']:
            risk_score += 25
            rules_triggered.append('matches_fraud_pattern')
        
        # Rule 5: High risk country
        if transaction['location'] in ['RU', 'CN', 'NG']:
            risk_score += 15
            rules_triggered.append('high_risk_location')
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = 'HIGH'
            action = 'BLOCK'
        elif risk_score >= 25:
            risk_level = 'MEDIUM'
            action = 'REVIEW'
        else:
            risk_level = 'LOW'
            action = 'ALLOW'
        
        return {
            'transaction_id': transaction['transaction_id'],
            'user_id': transaction['user_id'],
            'amount': transaction['amount'],
            'merchant': transaction['merchant'],
            'risk_score': risk_score,
            'risk_level': risk_level,
            'action': action,
            'rules_triggered': rules_triggered,
            'velocity_1h': tx_1h,
            'velocity_24h': tx_24h,
            'pattern_match': patterns['pattern_matched'],
            'user_age_days': user['account_age_days']
        }
    
    def process_all_transactions(self):
        """Process all transactions and generate alerts"""
        print("\n🔍 Processing transactions...")
        
        results = []
        alerts = []
        
        for _, tx in self.transactions.iterrows():
            score = self.score_transaction(tx)
            results.append(score)
            
            # Generate alert for high risk
            if score['risk_level'] == 'HIGH':
                alerts.append(score)
            
            # Debug: print actual fraud detection
            if tx['is_actual_fraud'] and score['risk_level'] != 'HIGH':
                print(f"⚠️ Missed fraud: {tx['transaction_id']} (risk: {score['risk_level']})")
            elif not tx['is_actual_fraud'] and score['risk_level'] == 'HIGH':
                print(f"⚠️ False positive: {tx['transaction_id']}")
        
        # Calculate accuracy
        df_results = pd.DataFrame(results)
        df_actual = self.transactions
        
        # Merge with actual labels
        comparison = df_results.merge(
            df_actual[['transaction_id', 'is_actual_fraud']], 
            on='transaction_id'
        )
        
        correct = len(comparison[
            ((comparison['risk_level'] == 'HIGH') & comparison['is_actual_fraud']) |
            ((comparison['risk_level'] != 'HIGH') & ~comparison['is_actual_fraud'])
        ])
        accuracy = correct / len(comparison) * 100
        
        print(f"\n📊 Results:")
        print(f"   Total transactions: {len(results)}")
        print(f"   High risk: {len([r for r in results if r['risk_level'] == 'HIGH'])}")
        print(f"   Medium risk: {len([r for r in results if r['risk_level'] == 'MEDIUM'])}")
        print(f"   Low risk: {len([r for r in results if r['risk_level'] == 'LOW'])}")
        print(f"   Alerts generated: {len(alerts)}")
        print(f"   Accuracy: {accuracy:.1f}%")
        
        # Save results
        with open('../data/fraud_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        with open('../data/alerts.json', 'w') as f:
            json.dump(alerts, f, indent=2, default=str)
        
        print("\n✅ Results saved to /data/fraud_results.json")
        return results, alerts

if __name__ == "__main__":
    detector = SimpleFraudDetector()
    results, alerts = detector.process_all_transactions()
    
    # Show some sample alerts
    print("\n🚨 Sample Alerts:")
    for alert in alerts[:5]:
        print(f"   {alert['transaction_id']}: ${alert['amount']} - {alert['merchant']} (Score: {alert['risk_score']})")
