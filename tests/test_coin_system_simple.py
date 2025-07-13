#!/usr/bin/env python3
"""
🪙 SIMPLE COIN SYSTEM TEST
Test coin functionality without heavy dependencies
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any

class SimpleCoinTester:
    """Basit coin sistemi test edici"""
    
    def __init__(self):
        self.test_data_file = "test_coin_data.json"
        self.load_test_data()
    
    def load_test_data(self):
        """Test verilerini yükle"""
        if os.path.exists(self.test_data_file):
            with open(self.test_data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "users": {},
                "transactions": [],
                "daily_limits": {}
            }
    
    def save_test_data(self):
        """Test verilerini kaydet"""
        with open(self.test_data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_balance(self, user_id: int) -> int:
        """Kullanıcı bakiyesini al"""
        return self.data["users"].get(str(user_id), {}).get("balance", 0)
    
    def add_coins(self, user_id: int, amount: int, description: str) -> bool:
        """Coin ekle"""
        try:
            user_key = str(user_id)
            
            # Kullanıcı yoksa oluştur
            if user_key not in self.data["users"]:
                self.data["users"][user_key] = {
                    "balance": 0,
                    "total_earned": 0,
                    "total_spent": 0,
                    "created_at": datetime.now().isoformat()
                }
            
            # Günlük limit kontrolü
            today = datetime.now().strftime("%Y-%m-%d")
            daily_key = f"{user_id}_{today}"
            
            if daily_key not in self.data["daily_limits"]:
                self.data["daily_limits"][daily_key] = {"earned": 0, "spent": 0}
            
            # Max günlük kazanç: 100 coin
            if self.data["daily_limits"][daily_key]["earned"] + amount > 100:
                print(f"⚠️ Günlük kazanç limiti aşıldı (100 coin)")
                return False
            
            # Coin ekle
            self.data["users"][user_key]["balance"] += amount
            self.data["users"][user_key]["total_earned"] += amount
            self.data["daily_limits"][daily_key]["earned"] += amount
            
            # Transaction kaydet
            self.data["transactions"].append({
                "user_id": user_id,
                "amount": amount,
                "type": "earn",
                "description": description,
                "timestamp": datetime.now().isoformat()
            })
            
            self.save_test_data()
            return True
            
        except Exception as e:
            print(f"❌ Coin ekleme hatası: {e}")
            return False
    
    def spend_coins(self, user_id: int, amount: int, description: str) -> bool:
        """Coin harca"""
        try:
            user_key = str(user_id)
            
            # Kullanıcı kontrolü
            if user_key not in self.data["users"]:
                print(f"❌ Kullanıcı bulunamadı: {user_id}")
                return False
            
            # Bakiye kontrolü
            current_balance = self.data["users"][user_key]["balance"]
            if current_balance < amount:
                print(f"❌ Yetersiz bakiye: {current_balance} < {amount}")
                return False
            
            # Günlük limit kontrolü
            today = datetime.now().strftime("%Y-%m-%d")
            daily_key = f"{user_id}_{today}"
            
            if daily_key not in self.data["daily_limits"]:
                self.data["daily_limits"][daily_key] = {"earned": 0, "spent": 0}
            
            # Max günlük harcama: 500 coin
            if self.data["daily_limits"][daily_key]["spent"] + amount > 500:
                print(f"⚠️ Günlük harcama limiti aşıldı (500 coin)")
                return False
            
            # Coin harca
            self.data["users"][user_key]["balance"] -= amount
            self.data["users"][user_key]["total_spent"] += amount
            self.data["daily_limits"][daily_key]["spent"] += amount
            
            # Transaction kaydet
            self.data["transactions"].append({
                "user_id": user_id,
                "amount": -amount,
                "type": "spend",
                "description": description,
                "timestamp": datetime.now().isoformat()
            })
            
            self.save_test_data()
            return True
            
        except Exception as e:
            print(f"❌ Coin harcama hatası: {e}")
            return False
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcı istatistikleri"""
        user_key = str(user_id)
        
        if user_key not in self.data["users"]:
            return {"error": "Kullanıcı bulunamadı"}
        
        user_data = self.data["users"][user_key]
        
        # Günlük limitler
        today = datetime.now().strftime("%Y-%m-%d")
        daily_key = f"{user_id}_{today}"
        daily_data = self.data["daily_limits"].get(daily_key, {"earned": 0, "spent": 0})
        
        # Tier hesapla
        balance = user_data["balance"]
        if balance < 50:
            tier = "bronze"
        elif balance < 200:
            tier = "silver"
        elif balance < 500:
            tier = "gold"
        else:
            tier = "platinum"
        
        return {
            "user_id": user_id,
            "balance": user_data["balance"],
            "total_earned": user_data["total_earned"],
            "total_spent": user_data["total_spent"],
            "tier": tier,
            "daily_earned": daily_data["earned"],
            "daily_spent": daily_data["spent"],
            "daily_earn_limit_remaining": 100 - daily_data["earned"],
            "daily_spend_limit_remaining": 500 - daily_data["spent"]
        }
    
    def run_comprehensive_test(self):
        """Kapsamlı test çalıştır"""
        print("🪙 COIN SYSTEM TEST BAŞLADI!")
        print("=" * 50)
        
        test_user_id = 999999
        
        # Test 1: İlk bakiye
        print(f"💰 Test 1: İlk bakiye kontrolü")
        initial_balance = self.get_balance(test_user_id)
        print(f"   İlk bakiye: {initial_balance} coin")
        
        # Test 2: Coin ekleme
        print(f"\n💰 Test 2: Coin ekleme (100 coin)")
        success = self.add_coins(test_user_id, 100, "Test coin ekleme")
        if success:
            new_balance = self.get_balance(test_user_id)
            print(f"   ✅ Başarılı: {new_balance} coin")
        else:
            print(f"   ❌ Başarısız")
        
        # Test 3: Coin harcama
        print(f"\n💰 Test 3: Coin harcama (25 coin)")
        spend_success = self.spend_coins(test_user_id, 25, "Test coin harcama")
        if spend_success:
            spend_balance = self.get_balance(test_user_id)
            print(f"   ✅ Başarılı: {spend_balance} coin")
        else:
            print(f"   ❌ Başarısız")
        
        # Test 4: Günlük limitler
        print(f"\n💰 Test 4: Günlük limit testi (120 coin ekleme)")
        limit_test = self.add_coins(test_user_id, 120, "Limit test")
        if not limit_test:
            print(f"   ✅ Günlük limit koruması çalışıyor")
        else:
            print(f"   ❌ Günlük limit koruması çalışmıyor")
        
        # Test 5: Yetersiz bakiye
        print(f"\n💰 Test 5: Yetersiz bakiye testi (10000 coin harcama)")
        insufficient_test = self.spend_coins(test_user_id, 10000, "Yetersiz bakiye test")
        if not insufficient_test:
            print(f"   ✅ Yetersiz bakiye koruması çalışıyor")
        else:
            print(f"   ❌ Yetersiz bakiye koruması çalışmıyor")
        
        # Test 6: Kullanıcı istatistikleri
        print(f"\n💰 Test 6: Kullanıcı istatistikleri")
        stats = self.get_user_stats(test_user_id)
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print(f"\n🎯 COIN SYSTEM TEST TAMAMLANDI!")
        print("=" * 50)
        
        return True

def main():
    """Ana test fonksiyonu"""
    tester = SimpleCoinTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main() 