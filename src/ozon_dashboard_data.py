#!/usr/bin/env python
"""
🛒 OZON Real Data Fetcher
DEBUG VERSION - Shows exact error
"""

import os
import requests
import sqlite3
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

class OzonRealDataFetcher:
    def __init__(self):
        # Credentials from GitHub Secrets
        self.client_id = os.environ.get('OZON_CLIENT_ID')
        self.api_key = os.environ.get('OZON_API_KEY')
        
        print(f"🔑 Client ID: {self.client_id[:5]}...{self.client_id[-5:] if self.client_id else 'None'}")
        print(f"🔑 API Key: {self.api_key[:5]}...{self.api_key[-5:] if self.api_key else 'None'}")
        
        if not self.client_id or not self.api_key:
            raise ValueError("❌ OZON credentials not found in environment")
        
        # Real data paths
        self.real_data_path = Path('../real_data/ozon')
        self.real_data_path.mkdir(parents=True, exist_ok=True)
        
        # TRY DIFFERENT BASE URLS
        self.base_urls = [
            "https://api.ozon.ru",
            "https://api-seller.ozon.ru",
            "https://seller-api.ozon.ru"
        ]
        
        self.headers = {
            'Client-Id': self.client_id,
            'Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        self.setup_databases()
        self.init_metrics_file()
    
    def test_all_endpoints(self):
        """Test different API endpoints to find which works"""
        print("\n🔍 Testing different API endpoints...")
        
        test_payload = {
            "dir": "ASC",
            "filter": {
                "since": (datetime.now() - timedelta(days=1)).isoformat()
            },
            "limit": 1,
            "with": {
                "analytics_data": True,
                "financial_data": True
            }
        }
        
        for base_url in self.base_urls:
            url = f"{base_url}/v3/posting/fbs/list"
            print(f"\n📡 Testing: {url}")
            try:
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=test_payload,
                    timeout=10
                )
                print(f"   Status: {response.status_code}")
                if response.status_code != 200:
                    print(f"   Response: {response.text[:200]}")
                else:
                    print(f"   ✅ SUCCESS! Using {base_url}")
                    self.base_url = base_url
                    return True
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return False
    
    def fetch_fbs_orders(self, hours_back=24):
        """Fetch real FBS orders with financial data"""
        
        # Try v2 endpoint as fallback
        endpoints = [
            "/v3/posting/fbs/list",
            "/v2/posting/fbs/list",
            "/v1/posting/fbs/list"
        ]
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            print(f"\n📡 Trying: {url}")
            
            payload = {
                "dir": "ASC",
                "filter": {
                    "since": (datetime.now() - timedelta(hours=hours_back)).isoformat()
                },
                "limit": 10,
                "with": {
                    "analytics_data": True,
                    "financial_data": True
                }
            }
            
            try:
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    orders = data.get('result', [])
                    print(f"   ✅ Success! Found {len(orders)} orders")
                    
                    # Save to database
                    if orders:
                        conn = sqlite3.connect(self.orders_db)
                        for order in orders:
                            financial = order.get('financial_data', {})
                            conn.execute('''
                                INSERT OR REPLACE INTO fbs_orders 
                                (order_id, posting_number, created_at, status, 
                                 products_price, commission, delivery_charge, customer_city)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                order.get('order_id'),
                                order.get('posting_number'),
                                order.get('created_at'),
                                order.get('status'),
                                financial.get('products_price', 0),
                                financial.get('commission', 0),
                                financial.get('delivery_charge', 0),
                                order.get('analytics_data', {}).get('city', 'unknown')
                            ))
                        conn.commit()
                        conn.close()
                    
                    return orders
                else:
                    print(f"   ❌ Failed: {response.text[:200]}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return []
    
    def run(self):
        """Main fetch and detect cycle"""
        print("\n" + "="*60)
        print("🛒 OZON REAL DATA FETCHER (DEBUG MODE)")
        print("="*60)
        
        # First test which endpoint works
        if not self.test_all_endpoints():
            print("\n❌ Could not find working endpoint!")
            print("Please check:")
            print("1. Your API keys are correct")
            print("2. Your account has access to these endpoints")
            print("3. The API hasn't changed")
            return
        
        # Fetch real data
        print("\n📡 Fetching FBS orders...")
        fbs_orders = self.fetch_fbs_orders()
        
        print(f"\n📊 Summary:")
        print(f"   Real orders fetched: {len(fbs_orders)}")
        print(f"   Database: {self.orders_db}")
        print("="*60)

if __name__ == "__main__":
    fetcher = OzonRealDataFetcher()
    fetcher.run()
