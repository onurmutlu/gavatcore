#!/usr/bin/env python3
"""
🔥 GERÇEK ZAMANLI BOT MONİTORİNG SİSTEMİ 🔥
==========================================

Mock data YOK! Sadece gerçek process'leri monitor eder.
Her 5 saniyede process durumunu kontrol eder.
Gerçek PID, memory, CPU takibi yapar.
"""

import subprocess
import psutil
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional
import asyncio

class LiveBotMonitor:
    """Gerçek zamanlı bot monitoring - Mock data YOK!"""
    
    def __init__(self):
        self.bot_configs = {
            "babagavat": {
                "script": "utils/babagavat_production_launcher.py",
                "process": None,
                "pid": None,
                "status": "stopped",
                "start_time": None
            },
            "lara": {
                "script": "lara_bot_launcher.py", 
                "process": None,
                "pid": None,
                "status": "stopped",
                "start_time": None
            },
            "geisha": {
                "script": "utils/babagavat_production_launcher.py",  # Placeholder
                "process": None,
                "pid": None,
                "status": "stopped", 
                "start_time": None
            }
        }
        
    def start_bot(self, bot_name: str) -> dict:
        """Gerçek bot process'i başlat"""
        if bot_name not in self.bot_configs:
            return {"success": False, "error": f"Bot '{bot_name}' tanımlı değil"}
        
        config = self.bot_configs[bot_name]
        script_path = config["script"]
        
        # Script var mı kontrol et
        if not os.path.exists(script_path):
            return {
                "success": False, 
                "error": f"GERÇEK HATA: Script bulunamadı: {script_path}",
                "is_real": True
            }
        
        # Zaten çalışıyor mu?
        if config["process"] and config["process"].poll() is None:
            return {
                "success": False,
                "error": f"Bot '{bot_name}' zaten çalışıyor (PID: {config['pid']})",
                "is_real": True
            }
        
        try:
            # Gerçek process başlat
            print(f"🚀 {bot_name} bot'u başlatılıyor: {script_path}")
            
            process = subprocess.Popen(
                ["python3", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Config'i güncelle
            config["process"] = process
            config["pid"] = process.pid
            config["status"] = "running"
            config["start_time"] = time.time()
            
            print(f"✅ {bot_name} başlatıldı - PID: {process.pid}")
            
            return {
                "success": True,
                "message": f"{bot_name} başlatıldı",
                "pid": process.pid,
                "is_real": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"GERÇEK HATA: {str(e)}",
                "is_real": True
            }
    
    def stop_bot(self, bot_name: str) -> dict:
        """Gerçek bot process'i durdur"""
        if bot_name not in self.bot_configs:
            return {"success": False, "error": f"Bot '{bot_name}' tanımlı değil"}
        
        config = self.bot_configs[bot_name]
        
        if not config["process"] or config["process"].poll() is not None:
            return {
                "success": False,
                "error": f"Bot '{bot_name}' çalışmıyor",
                "is_real": True
            }
        
        try:
            print(f"🔴 {bot_name} bot'u durduruluyor...")
            
            process = config["process"]
            process.terminate()
            
            # 5 saniye bekle
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Zorla kapat
                process.kill()
                process.wait()
            
            # Config'i temizle
            config["process"] = None
            config["pid"] = None
            config["status"] = "stopped"
            config["start_time"] = None
            
            print(f"✅ {bot_name} durduruldu")
            
            return {
                "success": True,
                "message": f"{bot_name} durduruldu",
                "is_real": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"GERÇEK HATA: {str(e)}",
                "is_real": True
            }
    
    def get_bot_status(self, bot_name: str) -> dict:
        """Gerçek bot durumunu al"""
        if bot_name not in self.bot_configs:
            return {"error": f"Bot '{bot_name}' tanımlı değil"}
        
        config = self.bot_configs[bot_name]
        
        # Process var mı ve çalışıyor mu?
        if not config["process"]:
            return {
                "bot_name": bot_name,
                "status": "stopped",
                "pid": None,
                "uptime_seconds": 0,
                "memory_mb": 0,
                "cpu_percent": 0,
                "is_real": True,
                "message": "Process çalışmıyor"
            }
        
        # Process öldü mü?
        if config["process"].poll() is not None:
            # Process öldü, config'i temizle
            config["process"] = None
            config["pid"] = None
            config["status"] = "crashed"
            config["start_time"] = None
            
            return {
                "bot_name": bot_name,
                "status": "crashed",
                "pid": None,
                "uptime_seconds": 0,
                "memory_mb": 0,
                "cpu_percent": 0,
                "is_real": True,
                "message": "Process crashed"
            }
        
        # Gerçek sistem bilgilerini al
        try:
            pid = config["pid"]
            p = psutil.Process(pid)
            
            # Gerçek memory (MB)
            memory_mb = p.memory_info().rss / 1024 / 1024
            
            # Gerçek CPU (%)
            cpu_percent = p.cpu_percent()
            
            # Gerçek uptime
            uptime_seconds = time.time() - config["start_time"] if config["start_time"] else 0
            
            return {
                "bot_name": bot_name,
                "status": "running",
                "pid": pid,
                "uptime_seconds": uptime_seconds,
                "memory_mb": round(memory_mb, 2),
                "cpu_percent": round(cpu_percent, 2),
                "is_real": True,
                "message": "GERÇEK PROCESS DATA",
                "script_path": config["script"]
            }
            
        except psutil.NoSuchProcess:
            # Process kayboldu
            config["process"] = None
            config["pid"] = None
            config["status"] = "missing"
            config["start_time"] = None
            
            return {
                "bot_name": bot_name,
                "status": "missing",
                "pid": None,
                "uptime_seconds": 0,
                "memory_mb": 0,
                "cpu_percent": 0,
                "is_real": True,
                "message": "Process kayboldu"
            }
        
        except Exception as e:
            return {
                "bot_name": bot_name,
                "status": "error",
                "pid": config["pid"],
                "uptime_seconds": 0,
                "memory_mb": 0,
                "cpu_percent": 0,
                "is_real": True,
                "message": f"GERÇEK HATA: {str(e)}"
            }
    
    def get_all_statuses(self) -> List[dict]:
        """Tüm bot durumlarını al"""
        statuses = []
        for bot_name in self.bot_configs.keys():
            status = self.get_bot_status(bot_name)
            statuses.append(status)
        return statuses
    
    def start_all_bots(self) -> dict:
        """Tüm botları başlat"""
        results = []
        success_count = 0
        
        for bot_name in self.bot_configs.keys():
            result = self.start_bot(bot_name)
            results.append({
                "bot_name": bot_name,
                "success": result["success"],
                "message": result.get("message", result.get("error"))
            })
            if result["success"]:
                success_count += 1
        
        return {
            "success": success_count > 0,
            "message": f"{success_count}/{len(self.bot_configs)} bot başlatıldı",
            "results": results,
            "is_real": True
        }
    
    def stop_all_bots(self) -> dict:
        """Tüm botları durdur"""
        results = []
        success_count = 0
        
        for bot_name in self.bot_configs.keys():
            result = self.stop_bot(bot_name)
            results.append({
                "bot_name": bot_name,
                "success": result["success"],
                "message": result.get("message", result.get("error"))
            })
            if result["success"]:
                success_count += 1
        
        return {
            "success": success_count > 0,
            "message": f"{success_count} bot durduruldu",
            "results": results,
            "is_real": True
        }
    
    def monitor_loop(self):
        """Sürekli monitoring loop"""
        print(f"""
🔥 GERÇEK ZAMANLI BOT MONİTORİNG BAŞLADI!
========================================
✅ Gerçek process monitoring
✅ Gerçek PID/memory/CPU takibi  
❌ Mock data YOK!
========================================
Bot sayısı: {len(self.bot_configs)}
Update interval: 5 saniye
========================================
        """)
        
        try:
            while True:
                print(f"\n📊 BOT DURUM RAPORU - {datetime.now().strftime('%H:%M:%S')}")
                print("=" * 60)
                
                statuses = self.get_all_statuses()
                
                for status in statuses:
                    bot_name = status["bot_name"]
                    bot_status = status["status"]
                    pid = status.get("pid", "N/A")
                    memory = status.get("memory_mb", 0)
                    cpu = status.get("cpu_percent", 0)
                    uptime = status.get("uptime_seconds", 0)
                    
                    status_emoji = {
                        "running": "🟢",
                        "stopped": "🔴",
                        "crashed": "💥",
                        "missing": "❓",
                        "error": "⚠️"
                    }.get(bot_status, "❓")
                    
                    uptime_min = int(uptime / 60)
                    
                    print(f"{status_emoji} {bot_name.upper():<12} | "
                          f"PID: {str(pid):<8} | "
                          f"RAM: {memory:>6.1f}MB | "
                          f"CPU: {cpu:>5.1f}% | "
                          f"Uptime: {uptime_min:>3}min")
                
                print("=" * 60)
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring durduruldu")
        except Exception as e:
            print(f"\n❌ Monitoring hatası: {e}")

# Global instance
live_monitor = LiveBotMonitor()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            bot_name = sys.argv[2] if len(sys.argv) > 2 else None
            if bot_name:
                result = live_monitor.start_bot(bot_name)
                print(json.dumps(result, indent=2))
            else:
                result = live_monitor.start_all_bots()
                print(json.dumps(result, indent=2))
        
        elif command == "stop":
            bot_name = sys.argv[2] if len(sys.argv) > 2 else None
            if bot_name:
                result = live_monitor.stop_bot(bot_name)
                print(json.dumps(result, indent=2))
            else:
                result = live_monitor.stop_all_bots()
                print(json.dumps(result, indent=2))
        
        elif command == "status":
            bot_name = sys.argv[2] if len(sys.argv) > 2 else None
            if bot_name:
                result = live_monitor.get_bot_status(bot_name)
                print(json.dumps(result, indent=2))
            else:
                result = live_monitor.get_all_statuses()
                print(json.dumps(result, indent=2))
        
        elif command == "monitor":
            live_monitor.monitor_loop()
        
        else:
            print("Kullanım: python3 real_bot_monitor_live.py [start|stop|status|monitor] [bot_name]")
    
    else:
        print("🔥 GERÇEK BOT MONİTORİNG - Komutlar:")
        print("python3 real_bot_monitor_live.py start        # Tüm botları başlat")
        print("python3 real_bot_monitor_live.py start lara   # Sadece lara'yı başlat")
        print("python3 real_bot_monitor_live.py stop         # Tüm botları durdur")
        print("python3 real_bot_monitor_live.py status       # Durumları göster")
        print("python3 real_bot_monitor_live.py monitor      # Canlı monitoring") 