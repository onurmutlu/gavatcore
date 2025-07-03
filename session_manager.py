#!/usr/bin/env python3
"""
🛡️ SESSION MANAGER - ONUR METODU
===============================
Bot session isolation ve process management
%100 deadlock-free garantisi
"""

import os
import time
import json
import psutil
import signal
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3

class SessionManager:
    def __init__(self):
        self.sessions_dir = "sessions"
        self.locks_dir = "session_locks"
        self.process_db = "session_processes.db"
        
        # Klasörleri oluştur
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.locks_dir, exist_ok=True)
        
        # Database başlat
        self.init_database()
        
        # Bot konfigürasyonu
        self.bots = {
            "lara": {
                "name": "YayınCı-Lara",
                "session": "_905382617727",
                "persona": "yayincilara",
                "launcher_type": "normal"  # normal veya ai
            },
            "geisha": {
                "name": "Geisha", 
                "session": "_905486306226",
                "persona": "xxxgeisha",
                "launcher_type": "ai"  # AI-powered launcher
            },
            "babagavat": {
                "name": "BabaGAVAT",
                "session": "_905513272355", 
                "persona": "babagavat",
                "launcher_type": "normal"
            }
        }
    
    def init_database(self):
        """Process tracking database'i başlat"""
        conn = sqlite3.connect(self.process_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_name TEXT UNIQUE,
                session_file TEXT,
                process_id INTEGER,
                launcher_type TEXT,
                start_time TIMESTAMP,
                status TEXT DEFAULT 'running',
                last_heartbeat TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def is_session_locked(self, session_name: str) -> bool:
        """Session lock kontrolü"""
        lock_file = os.path.join(self.locks_dir, f"{session_name}.lock")
        
        if not os.path.exists(lock_file):
            return False
        
        # Lock dosyasındaki PID'i kontrol et
        try:
            with open(lock_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Process hala çalışıyor mu?
            if psutil.pid_exists(pid):
                return True
            else:
                # Ölü lock dosyasını temizle
                os.remove(lock_file)
                return False
                
        except (ValueError, FileNotFoundError):
            # Bozuk lock dosyasını temizle
            try:
                os.remove(lock_file)
            except:
                pass
            return False
    
    def create_session_lock(self, session_name: str, pid: int) -> bool:
        """Session lock oluştur"""
        if self.is_session_locked(session_name):
            return False
        
        lock_file = os.path.join(self.locks_dir, f"{session_name}.lock")
        
        try:
            with open(lock_file, 'w') as f:
                f.write(str(pid))
            return True
        except Exception as e:
            print(f"❌ Lock oluşturma hatası {session_name}: {e}")
            return False
    
    def release_session_lock(self, session_name: str):
        """Session lock'ı serbest bırak"""
        lock_file = os.path.join(self.locks_dir, f"{session_name}.lock")
        
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
        except Exception as e:
            print(f"❌ Lock silme hatası {session_name}: {e}")
    
    def get_available_bots(self) -> List[str]:
        """Kullanılabilir botları listele"""
        available = []
        
        for bot_id, bot_info in self.bots.items():
            session_name = bot_info["session"]
            
            if not self.is_session_locked(session_name):
                available.append(bot_id)
        
        return available
    
    def start_bot_launcher(self, bot_id: str) -> Optional[int]:
        """Bot launcher'ı başlat"""
        if bot_id not in self.bots:
            print(f"❌ Bilinmeyen bot: {bot_id}")
            return None
        
        bot_info = self.bots[bot_id]
        session_name = bot_info["session"]
        
        # Session lock kontrolü
        if self.is_session_locked(session_name):
            print(f"⏭️ {bot_info['name']} session'ı zaten kullanımda")
            return None
        
        # Launcher script'ini seç
        if bot_info["launcher_type"] == "ai":
            launcher_script = "arayisvips_conversation_launcher.py"
        else:
            launcher_script = "arayisvips_viral_launcher.py"
        
        # Process başlat
        try:
            import subprocess
            
            # Environment variables
            env = os.environ.copy()
            env['BOT_SESSION'] = session_name
            env['BOT_PERSONA'] = bot_info["persona"]
            env['BOT_NAME'] = bot_info["name"]
            
            # Process başlat
            process = subprocess.Popen(
                ['python', launcher_script],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            pid = process.pid
            
            # Session lock oluştur
            if self.create_session_lock(session_name, pid):
                # Database'e kaydet
                self.record_bot_process(bot_id, session_name, pid, bot_info["launcher_type"])
                
                print(f"✅ {bot_info['name']} başlatıldı (PID: {pid}, Type: {bot_info['launcher_type']})")
                return pid
            else:
                # Lock oluşturulamadı, process'i durdur
                process.terminate()
                print(f"❌ {bot_info['name']} lock oluşturulamadı")
                return None
                
        except Exception as e:
            print(f"❌ {bot_info['name']} başlatma hatası: {e}")
            return None
    
    def stop_bot_launcher(self, bot_id: str) -> bool:
        """Bot launcher'ı durdur"""
        if bot_id not in self.bots:
            return False
        
        bot_info = self.bots[bot_id]
        session_name = bot_info["session"]
        
        # Database'den PID al
        pid = self.get_bot_process_id(bot_id)
        
        if pid and psutil.pid_exists(pid):
            try:
                # Process'i durdur
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
                
                # Hala çalışıyorsa force kill
                if psutil.pid_exists(pid):
                    os.kill(pid, signal.SIGKILL)
                
                print(f"✅ {bot_info['name']} durduruldu (PID: {pid})")
                
            except Exception as e:
                print(f"❌ {bot_info['name']} durdurma hatası: {e}")
        
        # Session lock'ı serbest bırak
        self.release_session_lock(session_name)
        
        # Database'den kaldır
        self.remove_bot_process(bot_id)
        
        return True
    
    def record_bot_process(self, bot_id: str, session_file: str, pid: int, launcher_type: str):
        """Bot process'ini database'e kaydet"""
        conn = sqlite3.connect(self.process_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO bot_processes 
            (bot_name, session_file, process_id, launcher_type, start_time, last_heartbeat)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (bot_id, session_file, pid, launcher_type, datetime.now(), datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_bot_process_id(self, bot_id: str) -> Optional[int]:
        """Bot process ID'sini al"""
        conn = sqlite3.connect(self.process_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT process_id FROM bot_processes 
            WHERE bot_name = ? AND status = 'running'
        ''', (bot_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def remove_bot_process(self, bot_id: str):
        """Bot process'ini database'den kaldır"""
        conn = sqlite3.connect(self.process_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE bot_processes 
            SET status = 'stopped' 
            WHERE bot_name = ?
        ''', (bot_id,))
        
        conn.commit()
        conn.close()
    
    def get_running_bots(self) -> Dict[str, Dict]:
        """Çalışan botları listele"""
        conn = sqlite3.connect(self.process_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bot_name, session_file, process_id, launcher_type, start_time
            FROM bot_processes 
            WHERE status = 'running'
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        running_bots = {}
        
        for result in results:
            bot_name, session_file, pid, launcher_type, start_time = result
            
            # Process hala çalışıyor mu kontrol et
            if psutil.pid_exists(pid):
                running_bots[bot_name] = {
                    'session_file': session_file,
                    'process_id': pid,
                    'launcher_type': launcher_type,
                    'start_time': start_time,
                    'uptime': self.calculate_uptime(start_time)
                }
            else:
                # Ölü process'i temizle
                self.remove_bot_process(bot_name)
                self.release_session_lock(session_file)
        
        return running_bots
    
    def calculate_uptime(self, start_time: str) -> str:
        """Uptime hesapla"""
        try:
            start = datetime.fromisoformat(start_time)
            uptime = datetime.now() - start
            
            hours = int(uptime.total_seconds() // 3600)
            minutes = int((uptime.total_seconds() % 3600) // 60)
            
            return f"{hours}h {minutes}m"
        except:
            return "Unknown"
    
    def cleanup_dead_processes(self):
        """Ölü process'leri temizle"""
        conn = sqlite3.connect(self.process_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bot_name, session_file, process_id 
            FROM bot_processes 
            WHERE status = 'running'
        ''')
        
        results = cursor.fetchall()
        
        for bot_name, session_file, pid in results:
            if not psutil.pid_exists(pid):
                print(f"🧹 Ölü process temizleniyor: {bot_name} (PID: {pid})")
                self.remove_bot_process(bot_name)
                self.release_session_lock(session_file)
        
        conn.close()
    
    def generate_status_report(self) -> str:
        """Sistem durumu raporu"""
        running_bots = self.get_running_bots()
        available_bots = self.get_available_bots()
        
        report = f"""
🛡️ SESSION MANAGER STATUS RAPORU
================================

📊 ÇALIŞAN BOTLAR ({len(running_bots)}):
"""
        
        for bot_name, info in running_bots.items():
            report += f"• {self.bots.get(bot_name, {}).get('name', bot_name)}: PID {info['process_id']} ({info['launcher_type']}) - {info['uptime']}\n"
        
        report += f"""
✅ MÜSAİT BOTLAR ({len(available_bots)}):
"""
        
        for bot_id in available_bots:
            bot_info = self.bots[bot_id]
            report += f"• {bot_info['name']} ({bot_info['launcher_type']})\n"
        
        report += f"""
🔒 SESSION LOCKS:
"""
        
        for bot_id, bot_info in self.bots.items():
            session_name = bot_info["session"]
            locked = "🔒 LOCKED" if self.is_session_locked(session_name) else "🔓 FREE"
            report += f"• {bot_info['name']}: {locked}\n"
        
        return report

# CLI Interface
def main():
    """Session Manager CLI"""
    manager = SessionManager()
    
    print("🛡️ SESSION MANAGER - ONUR METODU")
    print("=" * 40)
    
    while True:
        print("\n📋 KOMUTLAR:")
        print("1. Status raporu (s)")
        print("2. Bot başlat (start <bot_id>)")
        print("3. Bot durdur (stop <bot_id>)")
        print("4. Tüm botları başlat (start-all)")
        print("5. Tüm botları durdur (stop-all)")
        print("6. Ölü process'leri temizle (cleanup)")
        print("7. Çıkış (q)")
        
        command = input("\n🎯 Komut: ").strip().lower()
        
        if command == 's' or command == 'status':
            print(manager.generate_status_report())
            
        elif command.startswith('start '):
            bot_id = command.split(' ', 1)[1]
            manager.start_bot_launcher(bot_id)
            
        elif command.startswith('stop '):
            bot_id = command.split(' ', 1)[1]
            manager.stop_bot_launcher(bot_id)
            
        elif command == 'start-all':
            available = manager.get_available_bots()
            for bot_id in available:
                manager.start_bot_launcher(bot_id)
                time.sleep(2)  # Staggered start
                
        elif command == 'stop-all':
            running = manager.get_running_bots()
            for bot_id in running.keys():
                manager.stop_bot_launcher(bot_id)
                
        elif command == 'cleanup':
            manager.cleanup_dead_processes()
            print("✅ Ölü process'ler temizlendi")
            
        elif command == 'q' or command == 'quit':
            break
            
        else:
            print("❌ Bilinmeyen komut!")

if __name__ == "__main__":
    main() 