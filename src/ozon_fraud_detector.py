#!/usr/bin/env python
"""
🛒 Ozon Marketplace Fraud Detector
Uses GitHub Secrets for authentication
"""

import os
import requests
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

class OzonFraudDetector:
    def __init__(self):
        # Load from environment (GitHub Secrets)
        self.client_id = os.environ.get('OZON_CLIENT_ID')
        self.api_key = os.environ.get('OZON_API_KEY')
        
        if not self.client_id or not self.api_key:
            raise ValueError("❌ OZON_CLIENT_ID and OZON_API_KEY must be set")
        
        self.base_url = "https://api.ozon.ru"
        self.headers = {
            'Client-Id': self.client_id,
            'Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Setup database
        self.setup_database()
    
    def setup_database(self):
        """Create Ozon-specific fraud database"""
        conn = sqlite3.connect('../data/ozon_fraud.db')
        
        # FBS Orders table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ozon_fbs_orders (
                order_id TEXT PRIMARY KEY,
                posting_number TEXT,
                status TEXT,
                created_at DATETIME,
                products_price REAL,
                commission REAL,
                delivery_charge REAL,
                customer_city TEXT,
                risk_score REAL,
                fraud_flags TEXT
            )
        ''')
        
        # FBO Orders table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ozon_fbo_orders (
                order_id TEXT PRIMARY KEY,
                supply_order_id TEXT,
                status TEXT,
                created_at DATETIME,
                products_price REAL,
                customer_city TEXT,
                risk_score REAL,
                fraud_flags TEXT
            )
        ''')
        
        # Returns table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ozon_returns (
                return_id TEXT PRIMARY KEY,
                order_id TEXT,
                product_id TEXT,
                reason TEXT,
                created_at DATETIME,
                status TEXT,
                risk_score REAL
            )
        ''')
        
        # Fraud alerts table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ozon_fraud_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                order_id TEXT,
                risk_score REAL,
                details TEXT,
                detected_at DATETIME,
                action_taken TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Ozon fraud database ready")
    
    def fetch_fbs_orders(self, days_back=7):
        """Fetch FBS orders with financial data"""
        
        payload = {
            "dir": "ASC",
            "filter": {
                "since": (datetime.now() - timedelta(days=days_back)).isoformat()
            },
            "limit": 100,
            "with": {
                "analytics_data": True,
                "financial_data": True
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v3/posting/fbs/list",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                orders = data.get('result', [])
                print(f"✅ Fetched {len(orders)} FBS orders")
                return orders
            else:
                print(f"❌ Ozon API error: {response.status_code}")
                print(response.text[:200])
                return []
                
        except Exception as e:
            print(f"❌ Failed to fetch FBS orders: {e}")
            return []
    
    def fetch_fbo_orders(self, days_back=7):
        """Fetch FBO orders"""
        
        payload = {
            "filter": {
                "since": (datetime.now() - timedelta(days=days_back)).isoformat()
            },
            "limit": 100
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v3/supply-order/list",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                orders = data.get('result', [])
                print(f"✅ Fetched {len(orders)} FBO orders")
                return orders
            else:
                print(f"❌ Ozon API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Failed to fetch FBO orders: {e}")
            return []
    
    def detect_card_testing(self, orders):
        """
        Detect card testing fraud pattern
        Multiple small orders from same customer/IP
        """
        
        alerts = []
        customer_orders = {}
        
        for order in orders:
            # Group by customer (use order_id as proxy - in real API you'd have customer ID)
            customer_id = order.get('order_id', '').split('_')[0]
            if customer_id not in customer_orders:
                customer_orders[customer_id] = []
            customer_orders[customer_id].append(order)
        
        for customer_id, cust_orders in customer_orders.items():
            if len(cust_orders) >= 3:  # Multiple orders
                # Check amounts
                amounts = []
                for o in cust_orders:
                    if 'financial_data' in o:
                        price = o['financial_data'].get('products_price', 0)
                        amounts.append(price)
                
                # Card testing = multiple small orders
                small_orders = [a for a in amounts if a < 1000]  # Under 1000 RUB
                
                if len(small_orders) >= 3:
                    alerts.append({
                        'type': 'CARD_TESTING',
                        'customer_id': customer_id,
                        'order_count': len(cust_orders),
                        'small_orders': len(small_orders),
                        'amounts': amounts,
                        'risk_score': 0.95,
                        'action': 'BLOCK'
                    })
        
        return alerts
    
    def detect_velocity_anomaly(self, orders):
        """
        Detect unusual order velocity
        Many orders in short time
        """
        
        alerts = []
        
        if len(orders) > 20:  # More than 20 orders in period
            # Calculate orders per day
            days = 7
            orders_per_day = len(orders) / days
            
            if orders_per_day > 10:  # More than 10 orders/day average
                alerts.append({
                    'type': 'HIGH_VELOCITY',
                    'order_count': len(orders),
                    'orders_per_day': orders_per_day,
                    'risk_score': 0.85,
                    'action': 'REVIEW'
                })
        
        return alerts
    
    def detect_return_abuse(self, returns):
        """
        Detect return abuse patterns
        """
        
        alerts = []
        customer_returns = {}
        
        for ret in returns:
            cust_id = ret.get('order_id', '').split('_')[0]
            if cust_id not in customer_returns:
                customer_returns[cust_id] = []
            customer_returns[cust_id].append(ret)
        
        for cust_id, cust_returns in customer_returns.items():
            if len(cust_returns) > 3:  # High return rate
                alerts.append({
                    'type': 'RETURN_ABUSE',
                    'customer_id': cust_id,
                    'return_count': len(cust_returns),
                    'risk_score': 0.90,
                    'action': 'FLAG_ACCOUNT'
                })
        
        return alerts
    
    def save_alerts(self, alerts):
        """Save fraud alerts to database"""
        
        conn = sqlite3.connect('../data/ozon_fraud.db')
        
        for alert in alerts:
            conn.execute('''
                INSERT INTO ozon_fraud_alerts 
                (alert_type, order_id, risk_score, details, detected_at, action_taken)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                alert['type'],
                alert.get('order_id', 'N/A'),
                alert['risk_score'],
                json.dumps(alert),
                datetime.now().isoformat(),
                alert.get('action', 'MONITOR')
            ))
        
        conn.commit()
        conn.close()
        print(f"✅ Saved {len(alerts)} alerts to database")
    
    def generate_report(self):
        """Generate fraud report"""
        
        # Fetch data
        fbs_orders = self.fetch_fbs_orders()
        fbo_orders = self.fetch_fbo_orders()
        
        # Detect fraud
        all_alerts = []
        all_alerts.extend(self.detect_card_testing(fbs_orders + fbo_orders))
        all_alerts.extend(self.detect_velocity_anomaly(fbs_orders + fbo_orders))
        
        # Save alerts
        self.save_alerts(all_alerts)
        
        # Generate summary
        print("\n" + "="*60)
        print("🛒 OZON FRAUD DETECTION REPORT")
        print("="*60)
        print(f"📊 FBS Orders: {len(fbs_orders)}")
        print(f"📊 FBO Orders: {len(fbo_orders)}")
        print(f"🚨 Fraud Alerts: {len(all_alerts)}")
        
        for alert in all_alerts:
            print(f"\n⚠️ {alert['type']}")
            print(f"   Risk: {alert['risk_score']*100:.0f}%")
            print(f"   Action: {alert['action']}")
        
        return all_alerts

if __name__ == "__main__":
    detector = OzonFraudDetector()
    detector.generate_report()
