#!/usr/bin/env python3
import os
import sys
import time
import json
from datetime import datetime

# Bot startup simulation
print("🤖 GawatBaba - Sistem Admin Starting...")

# Load persona
try:
    with open("data/personas/gawatbaba.json", 'r', encoding='utf-8') as f:
        persona = json.load(f)
    
    phone = persona.get('phone', '+447832134241')
    # Use bot name for session file
    session_path = "sessions/gawatbaba.session"
    
    print("📱 Using session: " + session_path)
    
    if os.path.exists(session_path):
        print("✅ Session file exists")
        size = os.path.getsize(session_path)
        print("📊 Session size: " + str(size) + " bytes")
    else:
        print("❌ Session file not found: " + session_path)
        sys.exit(1)
    
    print("🔗 GawatBaba - Sistem Admin is now ONLINE!")
    print("📞 Phone: " + phone)
    print("👤 Character: " + persona.get('name', 'gawatbaba'))
    
    # Log startup
    with open("logs/gawatbaba_startup.log", "a", encoding="utf-8") as f:
        f.write("[" + datetime.now().isoformat() + "] Bot started\n")
    
    # Keep alive loop
    counter = 0
    while True:
        time.sleep(30)  # 30 second intervals
        counter += 1
        
        # Log activity every 5 minutes
        if counter % 10 == 0:
            with open("logs/gawatbaba_activity.log", "a", encoding="utf-8") as f:
                f.write("[" + datetime.now().isoformat() + "] Bot alive - cycle " + str(counter) + "\n")
            
            print("💓 GawatBaba - Sistem Admin heartbeat - cycle " + str(counter))
        
except KeyboardInterrupt:
    print("🛑 GawatBaba - Sistem Admin stopped by user")
except Exception as e:
    print("❌ GawatBaba - Sistem Admin error: " + str(e))
    sys.exit(1)
