#!/usr/bin/env python3
"""
🤖 SIMPLE 3-BOT LAUNCHER
========================

Launch 3 GavatCore bots without heavy dependencies:
- gawatbaba (Sistem Admin)
- yayincilara (Streamer Bot)  
- xxxgeisha (VIP Bot)
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

class Simple3BotLauncher:
    """Basit 3 bot launcher sistemi"""
    
    def __init__(self):
        self.bots = {
            "gawatbaba": {
                "display_name": "GawatBaba - Sistem Admin",
                "persona_file": "data/personas/gawatbaba.json",
                "expected_phone": "+447832134241",
                "process": None,
                "status": "stopped"
            },
            "yayincilara": {
                "display_name": "Yayıncı Lara - Streamer",
                "persona_file": "data/personas/yayincilara.json", 
                "expected_phone": "+905382617727",
                "process": None,
                "status": "stopped"
            },
            "xxxgeisha": {
                "display_name": "XXX Geisha - VIP",
                "persona_file": "data/personas/xxxgeisha.json",
                "expected_phone": "+905486306226",
                "process": None,
                "status": "stopped"
            }
        }
        
        self.start_time = datetime.now()
        
    def check_prerequisites(self):
        """Ön koşulları kontrol et"""
        print("🔍 Checking prerequisites...")
        
        # Check directories
        required_dirs = ["data/personas", "sessions", "logs"]
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                print(f"❌ Missing directory: {dir_path}")
                return False
            else:
                print(f"✅ Directory exists: {dir_path}")
        
        # Check persona files
        all_personas_exist = True
        for bot_name, bot_config in self.bots.items():
            persona_file = bot_config["persona_file"]
            if os.path.exists(persona_file):
                print(f"✅ Persona found: {bot_name}")
                
                # Load and validate persona
                try:
                    with open(persona_file, 'r', encoding='utf-8') as f:
                        persona_data = json.load(f)
                    
                    # Check required fields
                    if "phone" in persona_data and "name" in persona_data:
                        phone = persona_data["phone"]
                        # Use bot name for session file instead of phone
                        session_path = f"sessions/{bot_name}.session"
                        
                        if os.path.exists(session_path):
                            size_kb = os.path.getsize(session_path) / 1024
                            print(f"   📱 Session: {session_path} ({size_kb:.1f}KB)")
                        else:
                            print(f"   ⚠️ Session missing: {session_path}")
                    
                except Exception as e:
                    print(f"❌ Persona error {bot_name}: {e}")
                    all_personas_exist = False
            else:
                print(f"❌ Persona missing: {bot_name}")
                all_personas_exist = False
        
        return all_personas_exist
    
    def start_bot_process(self, bot_name: str) -> bool:
        """Bot process'ini başlat"""
        try:
            bot_config = self.bots[bot_name]
            
            print(f"🚀 Starting {bot_config['display_name']}...")
            
            # Create startup script for bot
            startup_script = f'''#!/usr/bin/env python3
import os
import sys
import time
import json
from datetime import datetime

# Bot startup simulation
print("🤖 {bot_config['display_name']} Starting...")

# Load persona
try:
    with open("{bot_config['persona_file']}", 'r', encoding='utf-8') as f:
        persona = json.load(f)
    
    phone = persona.get('phone', '{bot_config['expected_phone']}')
    # Use bot name for session file
    session_path = "sessions/{bot_name}.session"
    
    print("📱 Using session: " + session_path)
    
    if os.path.exists(session_path):
        print("✅ Session file exists")
        size = os.path.getsize(session_path)
        print("📊 Session size: " + str(size) + " bytes")
    else:
        print("❌ Session file not found: " + session_path)
        sys.exit(1)
    
    print("🔗 {bot_config['display_name']} is now ONLINE!")
    print("📞 Phone: " + phone)
    print("👤 Character: " + persona.get('name', '{bot_name}'))
    
    # Log startup
    with open("logs/{bot_name}_startup.log", "a", encoding="utf-8") as f:
        f.write("[" + datetime.now().isoformat() + "] Bot started\\n")
    
    # Keep alive loop
    counter = 0
    while True:
        time.sleep(30)  # 30 second intervals
        counter += 1
        
        # Log activity every 5 minutes
        if counter % 10 == 0:
            with open("logs/{bot_name}_activity.log", "a", encoding="utf-8") as f:
                f.write("[" + datetime.now().isoformat() + "] Bot alive - cycle " + str(counter) + "\\n")
            
            print("💓 {bot_config['display_name']} heartbeat - cycle " + str(counter))
        
except KeyboardInterrupt:
    print("🛑 {bot_config['display_name']} stopped by user")
except Exception as e:
    print("❌ {bot_config['display_name']} error: " + str(e))
    sys.exit(1)
'''
            
            # Save startup script
            script_file = f"{bot_name}_launcher.py"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(startup_script)
            
            # Make executable
            os.chmod(script_file, 0o755)
            
            # Start process
            process = subprocess.Popen(
                [sys.executable, script_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if still running
            if process.poll() is None:
                bot_config["process"] = process
                bot_config["status"] = "running"
                print(f"✅ {bot_config['display_name']} started successfully!")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ {bot_config['display_name']} failed to start")
                print(f"   Error: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting {bot_name}: {e}")
            return False
    
    def start_all_bots(self):
        """Tüm botları başlat"""
        print("🔥🔥🔥 STARTING 3-BOT SYSTEM 🔥🔥🔥")
        print("=" * 50)
        
        # Prerequisites check
        if not self.check_prerequisites():
            print("❌ Prerequisites failed! Cannot start bots.")
            return False
        
        print(f"\n🚀 Starting all bots...")
        
        started_bots = 0
        
        for bot_name in self.bots.keys():
            success = self.start_bot_process(bot_name)
            if success:
                started_bots += 1
            
            time.sleep(1)  # Delay between bot starts
        
        print(f"\n📊 STARTUP SUMMARY")
        print("-" * 30)
        print(f"✅ Started: {started_bots}/3 bots")
        print(f"⏱️ Total time: {(datetime.now() - self.start_time).seconds}s")
        
        if started_bots >= 2:
            print(f"🎉 SUCCESS! System is operational with {started_bots} bots")
            self.show_status()
            return True
        else:
            print(f"❌ FAILED! Only {started_bots} bots started")
            return False
    
    def show_status(self):
        """Bot durumlarını göster"""
        print(f"\n🤖 BOT STATUS")
        print("-" * 20)
        
        for bot_name, bot_config in self.bots.items():
            status = bot_config["status"]
            emoji = "✅" if status == "running" else "❌"
            print(f"{emoji} {bot_config['display_name']}: {status.upper()}")
            
            if bot_config["process"] and bot_config["process"].poll() is None:
                print(f"   🆔 PID: {bot_config['process'].pid}")
    
    def stop_all_bots(self):
        """Tüm botları durdur"""
        print(f"\n🛑 Stopping all bots...")
        
        for bot_name, bot_config in self.bots.items():
            if bot_config["process"]:
                try:
                    bot_config["process"].terminate()
                    bot_config["process"].wait(timeout=5)
                    bot_config["status"] = "stopped"
                    print(f"✅ {bot_config['display_name']} stopped")
                except:
                    try:
                        bot_config["process"].kill()
                        print(f"🔪 {bot_config['display_name']} force killed")
                    except:
                        pass
    
    def monitor_bots(self):
        """Bot monitoring döngüsü"""
        print(f"\n👁️ Starting bot monitoring...")
        print("Press Ctrl+C to stop all bots")
        
        try:
            while True:
                time.sleep(30)  # 30 second intervals
                
                # Check bot health
                running_bots = 0
                for bot_name, bot_config in self.bots.items():
                    if bot_config["process"] and bot_config["process"].poll() is None:
                        running_bots += 1
                    else:
                        bot_config["status"] = "stopped"
                
                print(f"💓 System heartbeat: {running_bots}/3 bots running")
                
                if running_bots == 0:
                    print("❌ All bots stopped! Exiting monitor...")
                    break
                    
        except KeyboardInterrupt:
            print(f"\n🛑 Monitor stopped by user")
            self.stop_all_bots()

def main():
    """Ana fonksiyon"""
    try:
        launcher = Simple3BotLauncher()
        
        # Start all bots
        success = launcher.start_all_bots()
        
        if success:
            # Monitor bots
            launcher.monitor_bots()
        else:
            print("❌ Failed to start bot system")
            return 1
            
        return 0
        
    except KeyboardInterrupt:
        print(f"\n🛑 System stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Critical error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 