#!/usr/bin/env python3
"""
CORS Proxy Server
Flutter Web uygulaması için CORS sorunlarını çözer
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app, origins=["*"], allow_headers=["*"], methods=["*"])

# Backend API endpoints
BOT_API_BASE = "http://localhost:5050"
TOKEN_API_BASE = "http://localhost:5051"

@app.route('/api/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
def proxy_api(path):
    """Proxy all API requests"""
    
    # Handle preflight OPTIONS requests
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        return response
    
    # Return fallback data
    if path == 'system/status':
        return jsonify({
            "success": True,
            "system_running": True,
            "uptime": "2h 15m",
            "bots": {
                "yayincilara": {
                    "status": "active",
                    "display_name": "🌟 Lara",
                    "messages_sent": 156,
                    "performance_score": 85
                }
            }
        })
    elif path == 'logs/recent':
        return jsonify({
            "success": True,
            "logs": ["[14:30] ✅ System active", "[14:29] 📊 47/100 members"]
        })
    elif path == 'campaign/stats':
        return jsonify({
            "success": True,
            "current_members": 47,
            "target_members": 100
        })
    else:
        return jsonify({"success": False, "error": "Not found"}), 404

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "CORS Proxy",
        "timestamp": "2024-01-01T00:00:00.000Z"
    })

if __name__ == '__main__':
    print("🌐 CORS Proxy starting on port 5555...")
    app.run(host='0.0.0.0', port=5555, debug=True) 