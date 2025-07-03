#!/usr/bin/env python3
"""
🧠 Simple Behavioral Insights Dashboard
=======================================

Basit ve debug-friendly behavioral insights paneli.
"""

import time
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
import statistics

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Simple behavioral analyzer
class SimpleBehavioralAnalyzer:
    """Basit behavioral analysis."""
    
    def analyze_big_five(self, text: str) -> Dict[str, Any]:
        """Basit Big Five analizi."""
        words = text.lower().split()
        word_count = len(words)
        
        # Basit keyword analizi
        positive_words = ['good', 'great', 'amazing', 'love', 'happy', 'beautiful', 'wonderful']
        negative_words = ['bad', 'terrible', 'hate', 'sad', 'angry', 'worst', 'awful']
        social_words = ['we', 'us', 'together', 'everyone', 'community', 'friends']
        
        positive_score = sum(1 for word in words if word in positive_words) / max(word_count, 1)
        negative_score = sum(1 for word in words if word in negative_words) / max(word_count, 1)
        social_score = sum(1 for word in words if word in social_words) / max(word_count, 1)
        
        return {
            'traits': {
                'openness': min(1.0, 0.3 + positive_score * 2),
                'conscientiousness': min(1.0, 0.4 + (1 - negative_score)),
                'extraversion': min(1.0, 0.2 + social_score * 3),
                'agreeableness': min(1.0, 0.5 + positive_score - negative_score),
                'neuroticism': min(1.0, negative_score * 2)
            },
            'confidence': 0.7
        }

# Initialize analyzer
analyzer = SimpleBehavioralAnalyzer()

# FastAPI app
app = FastAPI(title="🧠 Simple Behavioral Insights", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    """Get database connection."""
    try:
        conn = sqlite3.connect('gavatcore_v2.db', timeout=30)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Ana dashboard."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🧠 Behavioral Insights</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1000px; margin: 0 auto; }
            .card { background: white; padding: 20px; margin: 15px 0; border-radius: 10px; 
                   box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     color: white; padding: 20px; border-radius: 10px; text-align: center; }
            .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
            .metric { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }
            .metric h3 { margin: 0 0 10px 0; color: #495057; }
            .metric .value { font-size: 1.5em; font-weight: bold; color: #007bff; }
            .endpoints { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
            .endpoint { background: #e9ecef; padding: 15px; border-radius: 8px; }
            .endpoint h4 { margin: 0 0 10px 0; }
            .endpoint a { color: #007bff; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 Behavioral Insights Dashboard</h1>
                <p>User behavioral analysis with cache optimization</p>
            </div>
            
            <div class="card">
                <h2>🎯 Test Endpoints</h2>
                <div class="endpoints">
                    <div class="endpoint">
                        <h4>📊 User Profile Analysis</h4>
                        <a href="/api/profile/demo_user_1">/api/profile/demo_user_1</a>
                    </div>
                    <div class="endpoint">
                        <h4>📈 System Metrics</h4>
                        <a href="/api/metrics">/api/metrics</a>
                    </div>
                    <div class="endpoint">
                        <h4>👥 All Users</h4>
                        <a href="/api/users">/api/users</a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/api/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get user behavioral profile."""
    try:
        start_time = time.time()
        
        # Get database connection
        conn = get_db_connection()
        
        # Get user info
        user_query = "SELECT user_id, username FROM users WHERE user_id = ?"
        user_data = conn.execute(user_query, (user_id,)).fetchone()
        
        if not user_data:
            conn.close()
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        # Get messages
        messages_query = """
            SELECT message_text, timestamp, sentiment_score 
            FROM messages 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 50
        """
        messages = conn.execute(messages_query, (user_id,)).fetchall()
        
        if not messages:
            conn.close()
            return JSONResponse(content={
                'user_id': user_id,
                'username': user_data['username'],
                'error': 'No messages found for analysis'
            })
        
        # Analyze text
        combined_text = " ".join([msg['message_text'] for msg in messages if msg['message_text']])
        big_five_result = analyzer.analyze_big_five(combined_text)
        
        # Calculate sentiment stats
        sentiments = [float(msg['sentiment_score']) for msg in messages if msg['sentiment_score'] is not None]
        avg_sentiment = statistics.mean(sentiments) if sentiments else 0.0
        sentiment_variance = statistics.variance(sentiments) if len(sentiments) > 1 else 0.0
        
        # Calculate basic stats
        total_messages = len(messages)
        avg_message_length = statistics.mean([len(msg['message_text'] or "") for msg in messages])
        
        # Simple risk assessment
        neuroticism = big_five_result['traits']['neuroticism']
        risk_score = (neuroticism * 0.6) + (max(0, -avg_sentiment) * 0.4)
        
        analysis_time = time.time() - start_time
        
        conn.close()
        
        return JSONResponse(content={
            'user_id': user_id,
            'username': user_data['username'],
            'big_five_traits': big_five_result['traits'],
            'confidence': big_five_result['confidence'],
            'sentiment_analysis': {
                'average_sentiment': avg_sentiment,
                'sentiment_variance': sentiment_variance,
                'total_messages': total_messages
            },
            'statistics': {
                'total_messages': total_messages,
                'avg_message_length': avg_message_length,
                'analysis_time': f"{analysis_time:.4f}s"
            },
            'risk_assessment': {
                'overall_risk': risk_score,
                'risk_level': 'High' if risk_score > 0.7 else 'Medium' if risk_score > 0.4 else 'Low'
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'error': f'Analysis error: {str(e)}'}
        )

@app.get("/api/users")
async def get_all_users():
    """Get all users in database."""
    try:
        conn = get_db_connection()
        
        # Get users with message counts
        query = """
            SELECT u.user_id, u.username, COUNT(m.id) as message_count
            FROM users u
            LEFT JOIN messages m ON u.user_id = m.user_id
            GROUP BY u.user_id, u.username
            ORDER BY message_count DESC
        """
        
        users = conn.execute(query).fetchall()
        conn.close()
        
        user_list = []
        for user in users:
            user_list.append({
                'user_id': user['user_id'],
                'username': user['username'],
                'message_count': user['message_count']
            })
        
        return JSONResponse(content={
            'total_users': len(user_list),
            'users': user_list
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'error': f'Users query error: {str(e)}'}
        )

@app.get("/api/metrics")
async def get_system_metrics():
    """Get system metrics."""
    try:
        conn = get_db_connection()
        
        # Get basic counts
        users_count = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
        messages_count = conn.execute("SELECT COUNT(*) as count FROM messages").fetchone()['count']
        
        # Get recent activity
        recent_messages = conn.execute("""
            SELECT COUNT(*) as count FROM messages 
            WHERE datetime(timestamp) > datetime('now', '-24 hours')
        """).fetchone()['count']
        
        conn.close()
        
        return JSONResponse(content={
            'database_stats': {
                'total_users': users_count,
                'total_messages': messages_count,
                'recent_messages_24h': recent_messages
            },
            'system_health': 'healthy',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'error': f'Metrics error: {str(e)}'}
        )

@app.get("/health")
async def health_check():
    """Health check."""
    return {
        'status': 'healthy',
        'service': 'simple_behavioral_insights',
        'timestamp': datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🧠 Starting Simple Behavioral Insights Dashboard...")
    print("=" * 55)
    print("🌐 Dashboard: http://localhost:5057")
    print("🔍 Test profile: http://localhost:5057/api/profile/demo_user_1")
    print("📊 Metrics: http://localhost:5057/api/metrics")
    print("👥 Users: http://localhost:5057/api/users")
    print("=" * 55)
    
    uvicorn.run(app, host="0.0.0.0", port=5057, log_level="info") 