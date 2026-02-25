import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

class TrierFraudDetector:
    def __init__(self, data_path='../data/'):
        self.data_path = data_path
        self.load_data()
        self.initialize_pattern_ratings()
        
    def initialize_pattern_ratings(self):
        """Initialize the pattern rating matrix (ENHANCED oriental focus)"""
        self.pattern_ratings = {
            # ===== RUSSIAN PATTERNS (RU) =====
            # Russian merchants
            ('RU Store', 'RU'): 95,           # Russian store in Russia
            ('RU Store', 'CN'): 85,            # Russian store in China (suspicious)
            ('RU Store', 'US'): 80,            # Russian store in US (suspicious)
            ('RU Store', 'UK'): 80,            # Russian store in UK
            ('RU Store', 'DE'): 75,            # Russian store in Germany
        
            # Russian marketplaces
            ('Yandex Market', 'RU'): 70,       # Legit Russian marketplace
            ('Yandex Market', 'CN'): 90,        # Yandex in China? Suspicious!
            ('Ozon', 'RU'): 65,                 # Russian Amazon
            ('Ozon', 'CN'): 85,                  # Ozon in China? Fraud!
            ('Wildberries', 'RU'): 60,          # Russian fashion retailer
            ('Wildberries', 'CN'): 85,           # Wildberries in China? NO!
        
            # ===== CHINESE PATTERNS (CN) =====
            # Chinese merchants
            ('CN Store', 'CN'): 90,            # Chinese store in China
            ('CN Store', 'RU'): 85,             # Chinese store in Russia
            ('CN Store', 'US'): 75,             # Chinese store in US
            ('CN Store', 'UK'): 75,             # Chinese store in UK
        
            # Chinese marketplaces
            ('Alibaba', 'CN'): 60,              # Legit in China
            ('Alibaba', 'RU'): 85,               # Alibaba in Russia? Suspicious!
            ('Alibaba', 'US'): 70,               # Alibaba in US (common but monitor)
            ('JD.com', 'CN'): 55,                # Legit Chinese retailer
            ('JD.com', 'RU'): 80,                 # JD.com in Russia? Unusual!
            ('Taobao', 'CN'): 65,                 # Chinese eBay
            ('Taobao', 'RU'): 85,                  # Taobao in Russia? Fraud!
        
            # ===== AMAZON PATTERNS (Unusual Locations) =====
            ('Amazon', 'US'): 10,                # Normal
            ('Amazon', 'UK'): 15,                 # Normal
            ('Amazon', 'CA'): 15,                  # Normal
            ('Amazon', 'DE'): 20,                   # Normal EU
            ('Amazon', 'FR'): 20,                    # Normal EU
            ('Amazon', 'JP'): 25,                    # Normal Japan
        
            # Amazon in unexpected places
            ('Amazon', 'RU'): 85,                   # Amazon Russia? Very unusual!
            ('Amazon', 'CN'): 80,                    # Amazon China? Alibaba territory!
            ('Amazon', 'IN'): 45,                    # Amazon India exists but monitor
            ('Amazon', 'BR'): 50,                    # Amazon Brazil exists but monitor
            ('Amazon', 'NG'): 95,                    # Amazon Nigeria? Definitely fraud!
            ('Amazon', 'Unknown'): 70,                # Unknown location with Amazon
        
            # ===== WALMART PATTERNS (Unusual Locations) =====
            ('Walmart', 'US'): 5,                  # Very normal
            ('Walmart', 'CA'): 10,                   # Normal Canada
            ('Walmart', 'MX'): 15,                    # Normal Mexico
        
            # Walmart in unexpected places
            ('Walmart', 'RU'): 90,                   # Walmart Russia? NO!
            ('Walmart', 'CN'): 90,                    # Walmart China? They have stores but monitor
            ('Walmart', 'UK'): 60,                    # Walmart owns Asda in UK
            ('Walmart', 'DE'): 75,                    # Walmart Germany failed years ago - suspicious!
            ('Walmart', 'JP'): 80,                     # Walmart Japan (Seiyu) but monitor
            ('Walmart', 'Unknown'): 65,                 # Unknown location
        
            # ===== UNKNOWN STORE PATTERNS (High Risk) =====
            ('Unknown Store', 'RU'): 98,             # Maximum risk
            ('Unknown Store', 'CN'): 95,              # Maximum risk
            ('Unknown Store', 'NG'): 98,               # Nigeria high risk
            ('Unknown Store', 'BR'): 70,                # Brazil medium-high
            ('Unknown Store', 'IN'): 65,                 # India medium
            ('Unknown Store', 'US'): 50,                 # Unknown in US (suspicious but possible)
            ('Unknown Store', 'UK'): 55,                  # Unknown in UK
        
            # ===== CROSS-BORDER ORIENTAL FRAUD =====
            ('RU Store', 'CN'): 92,                    # Russian store IN China? VERY SUSPICIOUS!
            ('CN Store', 'RU'): 92,                     # Chinese store IN Russia? VERY SUSPICIOUS!
            ('Alibaba', 'RU'): 88,                       # Chinese marketplace in Russia
            ('Yandex', 'CN'): 90,                        # Russian service in China
        }
    
        # Default ratings by location
        self.default_ratings = {
            'US': 10, 'UK': 15, 'CA': 15, 'AU': 20,     # Low risk
            'DE': 20, 'FR': 20, 'JP': 25, 'KR': 25,      # Medium-low
            'IN': 35, 'BR': 40, 'MX': 35,                 # Medium
            'RU': 70,                                      # HIGH RISK
            'CN': 68,                                       # HIGH RISK
            'NG': 85, 'KE': 75, 'ZA': 60,                   # Africa (varies)
            'Unknown': 50                                    # Unknown location
        }
    
        # Add regional patterns
        self.regional_risk = {
            'Eastern Europe': ['RU', 'UA', 'BY', 'RO'],     # Higher risk
            'Asia': ['CN', 'HK', 'SG', 'MY'],                # Mixed risk
            'Africa': ['NG', 'KE', 'ZA', 'EG'],              # Higher risk
        }

    def get_pattern_category(self, merchant, location):
        """Categorize the pattern for better analytics"""
    
        # RU patterns
        ru_merchants = ['RU Store', 'Yandex', 'Ozon', 'Wildberries', 'Kaspersky', 'Mail.ru']
        cn_merchants = ['CN Store', 'Alibaba', 'JD.com', 'Taobao', 'Baidu', 'Tencent']
    
        category = 'normal'
    
        if any(ru in merchant for ru in ru_merchants):
            if location == 'RU':
                category = 'ru_domestic'
            elif location in ['CN', 'US', 'UK', 'DE']:
                category = 'ru_international_suspicious'
            else:
                category = 'ru_other'
    
        elif any(cn in merchant for cn in cn_merchants):
            if location == 'CN':
                category = 'cn_domestic'
            elif location in ['RU', 'US', 'UK', 'JP']:
                category = 'cn_international_suspicious'
            else:
                category = 'cn_other'
    
        elif merchant in ['Amazon', 'Walmart']:
            if location in ['US', 'CA', 'UK', 'DE', 'FR', 'JP']:
                category = f'{merchant.lower()}_normal'
            else:
                category = f'{merchant.lower()}_unusual'
    
        return category
    
    def get_pattern_rating(self, merchant, location):
        """Get risk rating for merchant-location pattern"""
        # Try exact match
        rating = self.pattern_ratings.get((merchant, location))
        
        if rating is not None:
            return rating
        
        # Try merchant with wildcard location
        for (m, l), r in self.pattern_ratings.items():
            if m == merchant and l == 'Unknown':
                return r
        
        # Return default based on location
        return self.default_ratings.get(location, 30)
    
    def load_data(self):
        """Load all data sources"""
        print("📊 Loading data sources for TRIER...")
        
        # Generate or load transactions with oriental patterns
        if not os.path.exists(os.path.join(self.data_path, 'transactions.csv')):
            self.generate_oriental_transactions()
        else:
            self.transactions = pd.read_csv(
                os.path.join(self.data_path, 'transactions.csv'),
                parse_dates=['timestamp']
            )
        
        # Load users
        conn = sqlite3.connect(os.path.join(self.data_path, 'users.db'))
        self.users = pd.read_sql_query("SELECT * FROM users", conn)
        conn.close()
        
        # Load or generate historical frauds
        if not os.path.exists(os.path.join(self.data_path, 'historical_frauds.csv')):
            self.generate_historical_frauds()
        else:
            self.historical_frauds = pd.read_csv(
                os.path.join(self.data_path, 'historical_frauds.csv'),
                parse_dates=['timestamp']
            )
        
        print(f"✅ Loaded {len(self.transactions)} transactions")
        print(f"✅ Loaded {len(self.users)} users")
        print(f"✅ Loaded {len(self.historical_frauds)} historical frauds")
    
    def generate_oriental_transactions(self, n=1000):
        """Generate transactions with oriental patterns"""
        print("🔄 Generating oriental-pattern transactions...")
        
        merchants = [
            'Amazon', 'Walmart', 'Target', 'Best Buy',
            'RU Store', 'CN Store', 'Unknown Store',
            'Local Store', 'Alibaba', 'JD.com'
        ]
        
        locations = ['US', 'UK', 'CA', 'AU', 'DE', 'RU', 'CN', 'IN', 'Unknown']
        
        transactions = []
        start_date = datetime.now() - timedelta(days=7)
        
        for i in range(1, n + 1):
            # Bias towards oriental patterns for more interesting fraud detection
            pattern_bias = random.random()
            
            if pattern_bias < 0.3:  # 30% oriental patterns
                merchant = random.choice(['RU Store', 'CN Store', 'Unknown Store', 'Alibaba'])
                location = random.choice(['RU', 'CN', 'Unknown'])
                amount = random.uniform(500, 3000)
                is_fraudulent = random.random() < 0.4  # Higher fraud rate
            elif pattern_bias < 0.6:  # 30% Amazon/Walmart patterns
                merchant = random.choice(['Amazon', 'Walmart'])
                location = random.choice(['US', 'UK', 'CA', 'RU', 'CN'])
                amount = random.uniform(50, 800)
                is_fraudulent = location in ['RU', 'CN']  # Fraud if unusual location
            else:  # 40% normal patterns
                merchant = random.choice(['Target', 'Best Buy', 'Local Store'])
                location = random.choice(['US', 'UK', 'CA', 'AU'])
                amount = random.uniform(10, 300)
                is_fraudulent = random.random() < 0.02  # Low fraud rate
            
            transaction = {
                'transaction_id': f'TX_{i:06d}',
                'user_id': random.randint(1, 100),
                'amount': round(amount, 2),
                'merchant': merchant,
                'merchant_category': self.get_merchant_category(merchant),
                'location': location,
                'device_id': f'DEV_{random.randint(100, 999)}',
                'timestamp': (start_date + timedelta(
                    hours=random.randint(1, 168)
                )).isoformat(),
                'is_actual_fraud': is_fraudulent
            }
            transactions.append(transaction)
        
        self.transactions = pd.DataFrame(transactions)
        self.transactions.to_csv(os.path.join(self.data_path, 'transactions.csv'), index=False)
        print(f"✅ Generated {n} transactions")
    
    def get_merchant_category(self, merchant):
        """Categorize merchants"""
        if 'RU' in merchant:
            return 'russian'
        elif 'CN' in merchant or merchant in ['Alibaba', 'JD.com']:
            return 'chinese'
        elif merchant in ['Amazon', 'Walmart']:
            return 'global_retail'
        else:
            return 'other'
    
    def generate_historical_frauds(self):
        """Generate historical frauds with oriental patterns"""
        frauds = []
        start_date = datetime.now() - timedelta(days=90)
        
        fraud_patterns = [
            # Russian patterns
            {'merchant': 'RU Store', 'locations': ['RU'], 'amount': (1000, 5000)},
            {'merchant': 'Unknown Store', 'locations': ['RU'], 'amount': (500, 3000)},
            {'merchant': 'Amazon', 'locations': ['RU'], 'amount': (800, 4000)},  # Amazon RU frauds
            
            # Chinese patterns
            {'merchant': 'CN Store', 'locations': ['CN'], 'amount': (800, 4000)},
            {'merchant': 'Alibaba', 'locations': ['CN', 'Unknown'], 'amount': (600, 3500)},
            {'merchant': 'Walmart', 'locations': ['CN'], 'amount': (700, 3000)},  # Walmart CN frauds
            
            # Cross-border oriental frauds
            {'merchant': 'RU Store', 'locations': ['CN'], 'amount': (1500, 6000)},
            {'merchant': 'CN Store', 'locations': ['RU'], 'amount': (1200, 5000)},
        ]
        
        for i in range(1, 301):  # 300 historical frauds
            pattern = random.choice(fraud_patterns)
            fraud = {
                'transaction_id': f'HIST_FRAUD_{i:04d}',
                'user_id': random.randint(1, 100),
                'amount': round(random.uniform(*pattern['amount']), 2),
                'merchant': pattern['merchant'],
                'location': random.choice(pattern['locations']),
                'device_id': f'DEV_{random.randint(100, 999)}',
                'timestamp': (start_date + timedelta(
                    hours=random.randint(1, 2160)
                )).isoformat(),
                'fraud_type': random.choice(['card_not_present', 'identity_theft', 'friendly_fraud']),
                'pattern_type': 'oriental' if any(x in pattern['merchant'] for x in ['RU', 'CN']) else 'other'
            }
            frauds.append(fraud)
        
        self.historical_frauds = pd.DataFrame(frauds)
        self.historical_frauds.to_csv(os.path.join(self.data_path, 'historical_frauds.csv'), index=False)
        print(f"✅ Generated {len(frauds)} historical frauds")
    
    def score_transaction(self, transaction):
        """Score transaction with oriental pattern focus"""
        user = self.users[self.users['user_id'] == transaction['user_id']].iloc[0]
    
        # IMPORTANT: Initialize variables FIRST!
        risk_score = 0
        rules_triggered = []
    
        # Get pattern category
        pattern_category = self.get_pattern_category(transaction['merchant'], transaction['location'])
    
        # Bonus risk for cross-border oriental patterns
        if pattern_category in ['ru_international_suspicious', 'cn_international_suspicious']:
            risk_score += 15
            rules_triggered.append(f'CROSS_BORDER_ORIENTAL:{transaction["merchant"]}-{transaction["location"]}')
    
        # Extra scrutiny for Amazon/Walmart in RU/CN
        if pattern_category in ['amazon_unusual', 'walmart_unusual']:
            if transaction['amount'] > 200:  # Lower threshold for unusual locations
                risk_score += 20
                rules_triggered.append('UNUSUAL_RETAILER_LOCATION_HIGH_AMOUNT')
    
        # Get pattern rating (THIS IS THE KEY ORIENTAL FEATURE)
        pattern_rating = self.get_pattern_rating(
            transaction['merchant'],
            transaction['location']
        )
    
        # Calculate velocities
        tx_24h, amount_24h = self.calculate_velocity(
            transaction['user_id'], 
            transaction['timestamp'], 
            24
        )
    
        # Check historical patterns
        historical_match = self.check_historical_patterns(
            transaction['merchant'],
            transaction['location'],
            transaction['amount']
        )
    
        # 1. Pattern rating (0-100) - THIS IS YOUR ORIENTAL FOCUS
        risk_score += pattern_rating * 0.5  # 50% weight on pattern
        if pattern_rating > 70:
            rules_triggered.append(f'HIGH_RISK_PATTERN:{transaction["merchant"]}-{transaction["location"]}')
        elif pattern_rating > 50:
            rules_triggered.append(f'MEDIUM_RISK_PATTERN:{transaction["merchant"]}-{transaction["location"]}')
    
        # 2. Amount check with pattern context
        expected_amount = self.get_expected_amount(transaction['merchant'], transaction['location'])
        if transaction['amount'] > expected_amount * 2:
            risk_score += 15
            rules_triggered.append('AMOUNT_ABOVE_PATTERN_EXPECTATION')
    
        # 3. Velocity check (especially for oriental patterns)
        if tx_24h > 5 and pattern_rating > 60:
            risk_score += 20
            rules_triggered.append('HIGH_VELOCITY_WITH_RISKY_PATTERN')
        elif tx_24h > 10:
            risk_score += 10
            rules_triggered.append('HIGH_VELOCITY')
    
        # 4. Historical pattern match
        if historical_match['matches']:
            risk_score += historical_match['confidence'] * 15
            rules_triggered.append(f'HISTORICAL_PATTERN_MATCH:{historical_match["similar_count"]}similar')
    
        # 5. User risk profile
        if user['risk_score'] > 0.7:
            risk_score += 10
            rules_triggered.append('HIGH_RISK_USER')
    
        # Cap at 100
        risk_score = min(100, risk_score)
    
        # Determine action
        if risk_score >= 70:
            risk_level = 'HIGH'
            action = 'BLOCK'
        elif risk_score >= 40:
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
            'location': transaction['location'],
            'pattern_rating': pattern_rating,
            'risk_score': round(risk_score, 1),
            'risk_level': risk_level,
            'action': action,
            'rules_triggered': rules_triggered,
            'pattern_category': self.get_merchant_category(transaction['merchant']),
            'velocity_24h': tx_24h,
            'historical_similar': historical_match['similar_count']
        }
   
    def calculate_velocity(self, user_id, current_time, hours):
        """Calculate transaction velocity"""
        time_threshold = current_time - timedelta(hours=hours)
        user_tx = self.transactions[
            (self.transactions['user_id'] == user_id) & 
            (pd.to_datetime(self.transactions['timestamp']) > time_threshold)
        ]
        return len(user_tx), user_tx['amount'].sum()
    
    def get_expected_amount(self, merchant, location):
        """Get expected transaction amount based on pattern"""
        pattern_key = (merchant, location)
        
        # Define expected amounts for patterns
        expected = {
            ('Amazon', 'US'): 150,
            ('Amazon', 'UK'): 130,
            ('Walmart', 'US'): 100,
            ('Walmart', 'CA'): 90,
            ('RU Store', 'RU'): 200,
            ('CN Store', 'CN'): 180,
            ('Unknown Store', 'RU'): 150,
            ('Unknown Store', 'CN'): 150,
        }
        
        return expected.get(pattern_key, 100)
    
    def check_historical_patterns(self, merchant, location, amount):
        """Check if transaction matches historical fraud patterns"""
        similar = self.historical_frauds[
            (self.historical_frauds['merchant'] == merchant) |
            (self.historical_frauds['location'] == location)
        ]
        
        if len(similar) > 0:
            amount_range = similar['amount'].agg(['mean', 'std'])
            amount_std = amount_range['std'] if not pd.isna(amount_range['std']) else 0
            
            # Calculate confidence based on amount proximity
            if amount_std > 0:
                z_score = abs(amount - amount_range['mean']) / amount_std
                confidence = max(0, 1 - (z_score / 3))  # 0-1 confidence
            else:
                confidence = 0.5
            
            return {
                'matches': True,
                'similar_count': len(similar),
                'confidence': confidence,
                'mean_amount': amount_range['mean']
            }
        
        return {'matches': False, 'similar_count': 0, 'confidence': 0}

    # Add this test function
    def test_patterns(self):
        """Test your new patterns"""
        test_cases = [
            ('RU Store', 'RU', 1500),      # Should be HIGH
            ('CN Store', 'CN', 2000),      # Should be HIGH
            ('Amazon', 'RU', 300),          # Should be MEDIUM-HIGH
            ('Walmart', 'CN', 400),          # Should be MEDIUM-HIGH
            ('Alibaba', 'RU', 500),          # Should be HIGH
            ('Yandex', 'CN', 600),            # Should be HIGH
            ('Unknown Store', 'RU', 100),     # Should be HIGH
            ('Amazon', 'US', 500),             # Should be LOW
        ]
    
        print("\n🧪 Testing Enhanced Patterns:")
        for merchant, location, amount in test_cases:
            rating = self.get_pattern_rating(merchant, location)
            category = self.get_pattern_category(merchant, location)
            print(f"   {merchant:12} in {location:2}: rating={rating:3}, category={category}")
    
    def process_all_transactions(self):
        """Process all transactions with oriental focus"""
        print("\n🔍 TRIER - Processing with Oriental Pattern Focus...")
        
        results = []
        alerts = []
        pattern_stats = {
            'RU_patterns': 0,
            'CN_patterns': 0,
            'Amazon_unusual': 0,
            'Walmart_unusual': 0
        }
        
        for _, tx in self.transactions.iterrows():
            score = self.score_transaction(tx)
            results.append(score)
            
            # Track pattern stats
            if score['merchant'] in ['RU Store', 'Unknown Store'] and score['location'] == 'RU':
                pattern_stats['RU_patterns'] += 1
            if score['merchant'] in ['CN Store', 'Unknown Store'] and score['location'] == 'CN':
                pattern_stats['CN_patterns'] += 1
            if score['merchant'] == 'Amazon' and score['location'] in ['RU', 'CN']:
                pattern_stats['Amazon_unusual'] += 1
            if score['merchant'] == 'Walmart' and score['location'] in ['RU', 'CN']:
                pattern_stats['Walmart_unusual'] += 1
            
            # Generate alert for high risk
            if score['risk_level'] == 'HIGH':
                alerts.append(score)
        
        # Calculate accuracy
        df_results = pd.DataFrame(results)
        df_actual = self.transactions
        
        comparison = df_results.merge(
            df_actual[['transaction_id', 'is_actual_fraud']], 
            on='transaction_id'
        )
        
        # Detection metrics
        true_positives = len(comparison[
            (comparison['risk_level'] == 'HIGH') & 
            (comparison['is_actual_fraud'] == True)
        ])
        false_positives = len(comparison[
            (comparison['risk_level'] == 'HIGH') & 
            (comparison['is_actual_fraud'] == False)
        ])
        false_negatives = len(comparison[
            (comparison['risk_level'] != 'HIGH') & 
            (comparison['is_actual_fraud'] == True)
        ])
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\n📊 TRIER Results:")
        print(f"   Total transactions: {len(results)}")
        print(f"   High risk: {len([r for r in results if r['risk_level'] == 'HIGH'])}")
        print(f"   Medium risk: {len([r for r in results if r['risk_level'] == 'MEDIUM'])}")
        print(f"   Low risk: {len([r for r in results if r['risk_level'] == 'LOW'])}")
        
        print(f"\n🎯 Pattern Detection Stats:")
        print(f"   🇷🇺 RU pattern transactions: {pattern_stats['RU_patterns']}")
        print(f"   🇨🇳 CN pattern transactions: {pattern_stats['CN_patterns']}")
        print(f"   📦 Amazon unusual location: {pattern_stats['Amazon_unusual']}")
        print(f"   🛒 Walmart unusual location: {pattern_stats['Walmart_unusual']}")
        
        print(f"\n📈 Performance Metrics:")
        print(f"   True Positives: {true_positives}")
        print(f"   False Positives: {false_positives}")
        print(f"   False Negatives: {false_negatives}")
        print(f"   Precision: {precision:.2%}")
        print(f"   Recall: {recall:.2%}")
        print(f"   F1 Score: {f1:.2f}")
        
        # Save results
        with open('../data/trier_results.json', 'w') as f:
            json.dump({
                'results': results,
                'pattern_stats': pattern_stats,
                'metrics': {
                    'precision': precision,
                    'recall': recall,
                    'f1': f1
                }
            }, f, indent=2, default=str)
        
        with open('../data/trier_alerts.json', 'w') as f:
            json.dump(alerts, f, indent=2, default=str)
        
        print("\n✅ TRIER results saved")
        return results, alerts, pattern_stats

if __name__ == "__main__":
    import random  # Import here for generation functions
    detector = TrierFraudDetector()
    results, alerts, stats = detector.process_all_transactions()
    
    # Show oriental pattern alerts
    print("\n🚨 Top Oriental Pattern Alerts:")
    oriental_alerts = [a for a in alerts if a['pattern_category'] in ['russian', 'chinese']]
    for alert in oriental_alerts[:5]:
        print(f"   {alert['transaction_id']}: {alert['merchant']} in {alert['location']} - "
              f"${alert['amount']} (Pattern Rating: {alert['pattern_rating']})")
