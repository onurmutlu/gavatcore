#!/usr/bin/env python3
"""
GERÇEK PROCESS MONİTORİNG SİSTEMİ
================================

Mock data YOK! Gerçek process'leri monitor eder.
Gerçek PID, memory, CPU, uptime takibi.
"""

import subprocess
import psutil
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional

class RealProcessMonitor:
    """Gerçek process monitoring - Mock data YOK!"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.process_info: Dict[str, dict] = {}
        
    def start_real_bot(self, bot_id: str, script_path: str) -> dict:
        """Gerçek bot process'i başlat"""
        try:
            # Eğer script yoksa gerçek hatayı döndür
            if not os.path.exists(script_path):
                return {
                    "success": False,
                    "error": f"GERÇEK HATA: Script bulunamadı: {script_path}",
                    "is_real": True
                }
            
            # Gerçek process başlat
            process = subprocess.Popen(
                ["python3", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Process'i kaydet
            self.processes[bot_id] = process
            self.process_info[bot_id] = {
                "start_time": time.time(),
                "script_path": script_path,
                "real_pid": process.pid
            }
            
            print(f"✅ GERÇEK BOT BAŞLATILDI: {bot_id} (PID: {process.pid})")
            
            return {
                "success": True,
                "message": f"GERÇEK process başlatıldı",
                "real_pid": process.pid,
                "is_real": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"GERÇEK HATA: {str(e)}",
                "is_real": True
            }
    
    def stop_real_bot(self, bot_id: str) -> dict:
        """Gerçek bot process'i durdur"""
        if bot_id not in self.processes:
            return {
                "success": False,
                "error": f"GERÇEK DURUM: {bot_id} çalışmıyor",
                "is_real": True
            }
        
        try:
            process = self.processes[bot_id]
            process.terminate()
            
            # 5 saniye bekle, sonra zorla kapat
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            # Temizle
            del self.processes[bot_id]
            if bot_id in self.process_info:
                del self.process_info[bot_id]
            
            print(f"🔴 GERÇEK BOT DURDURULDU: {bot_id}")
            
            return {
                "success": True,
                "message": f"GERÇEK process durduruldu",
                "is_real": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"GERÇEK HATA: {str(e)}",
                "is_real": True
            }
    
    def get_real_bot_status(self, bot_id: str) -> dict:
        """Gerçek bot durumunu al - Mock data YOK!"""
        
        if bot_id not in self.processes:
            return {
                "bot_id": bot_id,
                "status": "stopped",
                "real_pid": None,
                "uptime_seconds": 0,
                "memory_mb": 0,
                "cpu_percent": 0,
                "is_real": True,
                "message": "GERÇEK DURUM: Process çalışmıyor"
            }
        
        process = self.processes[bot_id]
        
        # Process hala çalışıyor mu?
        if process.poll() is not None:
            # Process öldü, temizle
            del self.processes[bot_id]
            if bot_id in self.process_info:
                del self.process_info[bot_id]
            
            return {
                "bot_id": bot_id,
                "status": "crashed",
                "real_pid": None,
                "uptime_seconds": 0,
                "memory_mb": 0,
                "cpu_percent": 0,
                "is_real": True,
                "message": "GERÇEK DURUM: Process crashed"
            }
        
        # Gerçek process bilgilerini al
        try:
            # psutil ile gerçek bilgileri al
            p = psutil.Process(process.pid)
            
            # Gerçek memory kullanımı (MB)
            memory_mb = p.memory_info().rss / 1024 / 1024
            
            # Gerçek CPU kullanımı (%)
            cpu_percent = p.cpu_percent()
            
            # Gerçek uptime
            start_time = self.process_info[bot_id]["start_time"]
            uptime_seconds = time.time() - start_time
            
            return {
                "bot_id": bot_id,
                "status": "running",
                "real_pid": process.pid,
                "uptime_seconds": uptime_seconds,
                "memory_mb": round(memory_mb, 2),
                "cpu_percent": round(cpu_percent, 2),
                "is_real": True,
                "message": "GERÇEK PROCESS - Mock data değil!",
                "script_path": self.process_info[bot_id]["script_path"]
            }
            
        except psutil.NoSuchProcess:
            # Process kayboldu
            del self.processes[bot_id]
            if bot_id in self.process_info:
                del self.process_info[bot_id]
            
            return {
                "bot_id": bot_id,
                "status": "missing",
                "real_pid": None,
                "uptime_seconds": 0,
                "memory_mb": 0,
                "cpu_percent": 0,
                "is_real": True,
                "message": "GERÇEK DURUM: Process kayboldu"
            }
        
        except Exception as e:
            return {
                "bot_id": bot_id,
                "status": "error",
                "real_pid": process.pid,
                "uptime_seconds": 0,
                "memory_mb": 0,
                "cpu_percent": 0,
                "is_real": True,
                "message": f"GERÇEK HATA: {str(e)}"
            }
    
    def get_all_real_statuses(self) -> List[dict]:
        """Tüm botların gerçek durumunu al"""
        bot_configs = {
            "babagavat": "utils/babagavat_production_launcher.py",
            "lara": "lara_bot_launcher.py", 
            "geisha": "utils/babagavat_production_launcher.py"
        }
        
        statuses = []
        for bot_id, script_path in bot_configs.items():
            status = self.get_real_bot_status(bot_id)
            status["expected_script"] = script_path
            statuses.append(status)
        
        return statuses
    
    def get_system_resources(self) -> dict:
        """Gerçek sistem kaynaklarını al"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "active_processes": len(self.processes),
                "is_real": True,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "cpu_percent": 0,
                "memory_percent": 0, 
                "disk_percent": 0,
                "active_processes": 0,
                "is_real": True,
                "error": f"GERÇEK HATA: {str(e)}"
            }

# Global instance
real_monitor = RealProcessMonitor()

if __name__ == "__main__":
    print("🔍 GERÇEK PROCESS MONİTORİNG TEST")
    print("=" * 40)
    
    # Sistem kaynaklarını göster
    resources = real_monitor.get_system_resources()
    print(f"CPU: {resources['cpu_percent']}%")
    print(f"Memory: {resources['memory_percent']}%")
    print(f"Disk: {resources['disk_percent']}%")
    
    # Bot durumlarını göster
    print("\nBot Durumları:")
    statuses = real_monitor.get_all_real_statuses()
    for status in statuses:
        print(f"{status['bot_id']}: {status['status']} - {status['message']}") 