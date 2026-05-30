#!/usr/bin/env python3
import os
import sys
import time
import json
from datetime import datetime

# Bot startup simulation
print("🤖 Yayıncı Lara - Streamer Starting...")

# Load persona
try:
    with open("data/personas/yayincilara.json", 'r', encoding='utf-8') as f:
        persona = json.load(f)
    
    phone = persona.get('phone', '+905382617727')
    # Use bot name for session file
    session_path = "sessions/yayincilara.session"
    
    print("📱 Using session: " + session_path)
    
    if os.path.exists(session_path):
        print("✅ Session file exists")
        size = os.path.getsize(session_path)
        print("📊 Session size: " + str(size) + " bytes")
    else:
        print("❌ Session file not found: " + session_path)
        sys.exit(1)
    
    print("🔗 Yayıncı Lara - Streamer is now ONLINE!")
    print("📞 Phone: " + phone)
    print("👤 Character: " + persona.get('name', 'yayincilara'))
    
    # Log startup
    with open("logs/yayincilara_startup.log", "a", encoding="utf-8") as f:
        f.write("[" + datetime.now().isoformat() + "] Bot started\n")
    
    # Keep alive loop
    counter = 0
    while True:
        time.sleep(30)  # 30 second intervals
        counter += 1
        
        # Log activity every 5 minutes
        if counter % 10 == 0:
            with open("logs/yayincilara_activity.log", "a", encoding="utf-8") as f:
                f.write("[" + datetime.now().isoformat() + "] Bot alive - cycle " + str(counter) + "\n")
            
            print("💓 Yayıncı Lara - Streamer heartbeat - cycle " + str(counter))
        
except KeyboardInterrupt:
    print("🛑 Yayıncı Lara - Streamer stopped by user")
except Exception as e:
    print("❌ Yayıncı Lara - Streamer error: " + str(e))
    sys.exit(1)
