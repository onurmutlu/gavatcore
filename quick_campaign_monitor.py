#!/usr/bin/env python3
"""
🎯 VIP Campaign Quick Monitor
Kampanya durumunu hızlı monitor et
"""

import os
import time
import subprocess
from vip_campaign_module import get_campaign_stats

def quick_monitor():
    """Hızlı kampanya durumu"""
    
    print("""
🎯 VIP CAMPAIGN QUICK MONITOR
=============================""")
    
    # Process durumu
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        production_line = [line for line in result.stdout.split('\n') if 'production_multi_bot' in line and 'grep' not in line]
        
        if production_line:
            process_info = production_line[0].split()
            pid = process_info[1]
            cpu = process_info[2] 
            mem = process_info[3]
            print(f"✅ Bot Status: AKTIF (PID: {pid})")
            print(f"📊 CPU: {cpu}% | Memory: {mem}%")
        else:
            print("❌ Bot Status: KAPALI")
    except:
        print("⚠️ Process check hatası")
    
    # Campaign stats
    stats = get_campaign_stats()
    print(f"\n🎯 Campaign: {'✅ AKTIF' if stats['active'] else '❌ PASIF'}")
    print(f"👥 Üyeler: {stats['current_members']}/{stats['target_members']} (%{stats['progress_percentage']})")
    print(f"🎁 Kalan slot: {stats['remaining_spots']}")
    print(f"💰 XP/Davet: {stats['xp_per_invite']}")
    print(f"🎯 Hedef: {stats['target_group']}")
    print(f"👨‍💼 Admin: {stats['campaign_admin']}")
    
    # Log check
    if os.path.exists("production_logs.txt"):
        print(f"\n📋 Son log entries:")
        with open("production_logs.txt", "r") as f:
            lines = f.readlines()
            for line in lines[-3:]:
                print(f"  {line.strip()}")
    
    print(f"\n⏰ Monitor time: {time.strftime('%H:%M:%S')}")
    print("="*40)

if __name__ == "__main__":
    quick_monitor() 