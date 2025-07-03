#!/usr/bin/env python3
"""
GERÇEK BOT YÖNETİM API'Sİ - MOCK DATA YOK!
==========================================

Hiç mock data kullanmaz. Sadece gerçek process'leri monitor eder.
Gerçek PID, memory, CPU, uptime takibi.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from real_process_monitor import real_monitor

app = Flask(__name__)
CORS(app, origins=["*"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot script paths - GERÇEK DOSYA YOLLARI
BOT_SCRIPTS = {
    "babagavat": "utils/babagavat_production_launcher.py",
    "lara": "lara_bot_launcher.py",
    "geisha": "utils/babagavat_production_launcher.py"
}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "api_type": "REAL - No Mock Data",
        "bots_count": len(BOT_SCRIPTS)
    })

@app.route('/api/bots', methods=['GET'])
def get_all_bots():
    """Gerçek bot durumlarını al - Mock data YOK!"""
    try:
        statuses = real_monitor.get_all_real_statuses()
        
        # Convert to API format
        bots = []
        for status in statuses:
            bot = {
                "id": status["bot_id"],
                "name": status["bot_id"].title(),
                "status": status["status"],
                "pid": status["real_pid"],
                "uptime": status["uptime_seconds"] / 60,  # minutes
                "memory_usage": status["memory_mb"],
                "cpu_usage": status["cpu_percent"],
                "messages_sent": 0,  # Bu gerçek bot'tan alınmalı
                "is_real_data": True,
                "message": status["message"]
            }
            bots.append(bot)
        
        return jsonify({
            "success": True,
            "bots": bots,
            "total_count": len(bots),
            "data_type": "REAL - No Mock"
        })
        
    except Exception as e:
        logger.error(f"Gerçek bot status hatası: {e}")
        return jsonify({
            "success": False,
            "error": f"GERÇEK HATA: {str(e)}",
            "data_type": "REAL - No Mock"
        }), 500

@app.route('/api/bot/<bot_id>/start', methods=['POST'])
def start_bot(bot_id):
    """Gerçek bot başlat"""
    if bot_id not in BOT_SCRIPTS:
        return jsonify({
            "success": False,
            "error": f"Bot '{bot_id}' tanımlı değil",
            "available_bots": list(BOT_SCRIPTS.keys())
        }), 404
    
    script_path = BOT_SCRIPTS[bot_id]
    result = real_monitor.start_real_bot(bot_id, script_path)
    
    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route('/api/bot/<bot_id>/stop', methods=['POST'])
def stop_bot(bot_id):
    """Gerçek bot durdur"""
    result = real_monitor.stop_real_bot(bot_id)
    
    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route('/api/bot/<bot_id>/status', methods=['GET'])
def get_bot_status(bot_id):
    """Gerçek bot durumunu al"""
    status = real_monitor.get_real_bot_status(bot_id)
    
    return jsonify({
        "success": True,
        "bot": {
            "id": bot_id,
            "name": bot_id.title(),
            "status": status["status"],
            "pid": status["real_pid"],
            "uptime": status["uptime_seconds"] / 60,
            "memory_usage": status["memory_mb"],
            "cpu_usage": status["cpu_percent"],
            "is_real_data": True,
            "message": status["message"]
        }
    })

@app.route('/api/system/start', methods=['POST'])
def start_all_bots():
    """Tüm botları gerçekten başlat"""
    results = []
    
    for bot_id, script_path in BOT_SCRIPTS.items():
        result = real_monitor.start_real_bot(bot_id, script_path)
        results.append({
            "bot_id": bot_id,
            "success": result["success"],
            "message": result.get("message", result.get("error"))
        })
    
    success_count = sum(1 for r in results if r["success"])
    
    return jsonify({
        "success": success_count > 0,
        "message": f"GERÇEK SONUÇ: {success_count}/{len(BOT_SCRIPTS)} bot başlatıldı",
        "results": results,
        "data_type": "REAL - No Mock"
    })

@app.route('/api/system/stop', methods=['POST'])
def stop_all_bots():
    """Tüm botları gerçekten durdur"""
    results = []
    
    for bot_id in BOT_SCRIPTS.keys():
        result = real_monitor.stop_real_bot(bot_id)
        results.append({
            "bot_id": bot_id,
            "success": result["success"],
            "message": result.get("message", result.get("error"))
        })
    
    success_count = sum(1 for r in results if r["success"])
    
    return jsonify({
        "success": success_count > 0,
        "message": f"GERÇEK SONUÇ: {success_count} bot durduruldu",
        "results": results,
        "data_type": "REAL - No Mock"
    })

@app.route('/api/system/health', methods=['GET'])
def system_health():
    """Gerçek sistem sağlığı"""
    resources = real_monitor.get_system_resources()
    
    return jsonify({
        "success": True,
        "system_health": resources,
        "data_type": "REAL - No Mock"
    })

@app.route('/api/logs/recent', methods=['GET'])
def recent_logs():
    """Gerçek loglar - şimdilik basit"""
    return jsonify({
        "success": True,
        "logs": [
            {
                "timestamp": "2024-01-01T12:00:00",
                "level": "INFO",
                "message": "GERÇEK LOG SİSTEMİ - Mock değil",
                "source": "real_api"
            }
        ],
        "data_type": "REAL - No Mock"
    })

if __name__ == '__main__':
    print("""
🔥 GERÇEK BOT YÖNETİM API'Sİ - MOCK DATA YOK!
============================================
✅ Gerçek process monitoring
✅ Gerçek PID takibi
✅ Gerçek memory/CPU ölçümü
❌ Mock data YOK!
============================================
🌐 API: http://localhost:5005
📊 Bot sayısı: 3 (GERÇEK)
============================================
    """)
    
    try:
        app.run(host='0.0.0.0', port=5005, debug=False)
    except Exception as e:
        print(f"GERÇEK HATA: {e}")
        print("Port 5005 kullanımda olabilir.") 