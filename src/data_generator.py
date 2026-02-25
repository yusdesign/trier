import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Generate user profiles
def create_user_database():
    conn = sqlite3.connect('../data/users.db')
    
    users = []
    for i in range(1, 101):  # 100 users
        user = {
            'user_id': i,
            'email': f'user{i}@example.com',
            'country': random.choice(['US', 'UK', 'CA', 'AU', 'DE']),
            'account_age_days': random.randint(1, 365),
            'risk_score': round(random.uniform(0, 1), 2),
            'is_vip': random.choice([0, 1])
        }
        users.append(user)
    
    pd.DataFrame(users).to_sql('users', conn, if_exists='replace', index=False)
    conn.close()
    print("✅ User database created")

# Generate historical fraud patterns
def create_historical_frauds():
    frauds = []
    start_date = datetime.now() - timedelta(days=90)
    
    fraud_patterns = [
        {'merchant': 'Amazon', 'amount_range': (500, 2000), 'locations': ['US', 'UK']},
        {'merchant': 'Walmart', 'amount_range': (100, 500), 'locations': ['US', 'CA']},
        {'merchant': 'Unknown Store', 'amount_range': (50, 300), 'locations': ['RU', 'CN']},
    ]
    
    for i in range(1, 201):  # 200 historical frauds
        pattern = random.choice(fraud_patterns)
        fraud = {
            'transaction_id': f'FRAUD_{i:04d}',
            'user_id': random.randint(1, 100),
            'amount': round(random.uniform(*pattern['amount_range']), 2),
            'merchant': pattern['merchant'],
            'location': random.choice(pattern['locations']),
            'device_id': f'DEV_{random.randint(100, 999)}',
            'timestamp': (start_date + timedelta(
                hours=random.randint(1, 2160)
            )).isoformat(),
            'fraud_type': random.choice(['chargeback', 'stolen_card', 'account_takeover'])
        }
        frauds.append(fraud)
    
    pd.DataFrame(frauds).to_csv('../data/historical_frauds.csv', index=False)
    print("✅ Historical fraud data created")

# Generate live transactions
def generate_live_transactions(n=1000):
    transactions = []
    start_date = datetime.now() - timedelta(days=7)
    
    merchants = ['Amazon', 'Walmart', 'Target', 'Starbucks', 'Uber', 'Netflix', 'Spotify']
    
    for i in range(1, n + 1):
        # Most transactions are normal
        is_fraudulent = random.random() < 0.03  # 3% fraud rate
        
        if is_fraudulent:
            # Fraudulent patterns
            amount = random.uniform(800, 3000)
            merchant = random.choice(['Unknown Store', 'Amazon'])
            location = random.choice(['RU', 'CN', 'NG'])
        else:
            # Normal patterns
            amount = random.uniform(5, 200)
            merchant = random.choice(merchants)
            location = random.choice(['US', 'UK', 'CA', 'AU'])
        
        transaction = {
            'transaction_id': f'TX_{i:06d}',
            'user_id': random.randint(1, 100),
            'amount': round(amount, 2),
            'merchant': merchant,
            'location': location,
            'device_id': f'DEV_{random.randint(100, 999)}',
            'timestamp': (start_date + timedelta(
                hours=random.randint(1, 168)
            )).isoformat(),
            'is_actual_fraud': is_fraudulent  # For testing accuracy
        }
        transactions.append(transaction)
    
    pd.DataFrame(transactions).to_csv('../data/transactions.csv', index=False)
    print(f"✅ {n} live transactions created")

if __name__ == "__main__":
    print("🚀 Generating fraud detection dataset...")
    create_user_database()
    create_historical_frauds()
    generate_live_transactions(1000)
    print("✅ Dataset ready! Check the /data folder")
