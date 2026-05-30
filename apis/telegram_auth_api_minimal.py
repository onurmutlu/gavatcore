#!/usr/bin/env python3
"""
Minimal Telegram Authentication API for debugging
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Mock bot configurations
BOT_CONFIGS = {
    'lara': {
        'phone': '+905382617727',
        'display_name': 'Lara - Flirty Streamer',
    },
    'babagavat': {
        'phone': '+447832134241',
        'display_name': 'BabaGavat - Club Leader', 
    },
    'geisha': {
        'phone': '+905486306226',
        'display_name': 'Geisha - Sophisticated Moderator',
    }
}

@app.route('/api/telegram/bots', methods=['GET'])
def get_available_bots():
    """Get list of available bots with their configurations"""
    try:
        bots = []
        for bot_name, config in BOT_CONFIGS.items():
            bots.append({
                'name': bot_name,
                'display_name': config['display_name'],
                'phone': config['phone'],
                'session_exists': False,  # Mock value
                'status': 'needs_auth'
            })
        
        return jsonify({'bots': bots})
        
    except Exception as e:
        print(f"Get bots error: {e}")
        return jsonify({'error': 'Failed to get bot list'}), 500

@app.route('/api/telegram/send-code', methods=['POST', 'OPTIONS'])
def send_code():
    """Mock send verification code endpoint"""
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    try:
        print(f"DEBUG: Raw request data: {request.data}")
        print(f"DEBUG: Request headers: {dict(request.headers)}")
        print(f"DEBUG: Request method: {request.method}")
        
        data = request.get_json()
        print(f"DEBUG: Parsed JSON data: {data}")
        
        if data is None:
            print("DEBUG: No JSON data received")
            return jsonify({'error': 'No JSON data provided'}), 400
        
        bot_name = data.get('bot_name')
        print(f"DEBUG: Bot name from request: {bot_name}")
        print(f"DEBUG: Available bot names: {list(BOT_CONFIGS.keys())}")
        
        if not bot_name:
            print("DEBUG: No bot_name in request")
            return jsonify({'error': 'Missing bot_name parameter'}), 400
            
        if bot_name not in BOT_CONFIGS:
            print(f"DEBUG: Invalid bot name: {bot_name}")
            return jsonify({'error': f'Invalid bot name: {bot_name}. Available: {list(BOT_CONFIGS.keys())}'}), 400
        
        bot_config = BOT_CONFIGS[bot_name]
        print(f"DEBUG: Using bot config: {bot_config}")
        
        # Mock response for testing
        response = {
            'success': True,
            'bot_name': bot_name,
            'phone': bot_config['phone'],
            'phone_code_hash': 'mock_hash_12345',
            'session_id': f'mock_session_{bot_name}'
        }
        
        print(f"DEBUG: Sending response: {response}")
        return jsonify(response)
        
    except Exception as e:
        print(f"DEBUG: Exception in send_code: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to send verification code: {str(e)}'}), 500

@app.route('/api/telegram/verify-code', methods=['POST', 'OPTIONS'])
def verify_code():
    """Mock verify code endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    try:
        data = request.get_json()
        code = data.get('code')
        phone_code_hash = data.get('phone_code_hash')
        session_id = data.get('session_id')
        
        if not all([code, phone_code_hash, session_id]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Mock successful verification
        return jsonify({
            'success': True,
            'needs_password': False,
            'user': {
                'id': 12345,
                'name': 'Test User',
                'email': 'test@telegram',
                'role': 'telegram_user',
                'username': 'testuser'
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Code verification failed: {str(e)}'}), 500

@app.route('/api/telegram/verify-2fa', methods=['POST', 'OPTIONS'])
def verify_2fa():
    """Mock 2FA verification endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    try:
        data = request.get_json()
        password = data.get('password')
        session_id = data.get('session_id')
        
        if not all([password, session_id]):
            return jsonify({'error': 'Password and session_id required'}), 400
        
        # Mock successful 2FA verification
        return jsonify({
            'success': True,
            'user': {
                'id': 12345,
                'name': 'Test User',
                'email': 'test@telegram',
                'role': 'telegram_user',
                'username': 'testuser'
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'2FA verification failed: {str(e)}'}), 500

@app.route('/api/telegram/send-message', methods=['POST', 'OPTIONS'])
def send_message():
    """Send message via bot - SPAM FUNCTIONALITY"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    try:
        data = request.get_json()
        bot_name = data.get('bot_name')
        chat_id = data.get('chat_id')
        message = data.get('message')
        
        if not all([bot_name, chat_id, message]):
            return jsonify({'error': 'Missing required fields: bot_name, chat_id, message'}), 400
        
        if bot_name not in BOT_CONFIGS:
            return jsonify({'error': f'Invalid bot name: {bot_name}'}), 400
        
        # Mock successful message sending
        print(f"SPAM: Bot {bot_name} sending message to {chat_id}: {message}")
        
        return jsonify({
            'success': True,
            'message_id': 99999,
            'bot_name': bot_name,
            'chat_id': chat_id,
            'message': message,
            'timestamp': '2024-01-01T12:00:00Z'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to send message: {str(e)}'}), 500

@app.route('/api/telegram/chats', methods=['GET'])
def get_chats():
    """Get chat list for spam targets"""
    try:
        # Mock chat list for spam targeting
        chats = [
            {
                'id': 123456,
                'name': 'Spam Target 1',
                'type': 'private',
                'username': 'target1',
                'last_message': 'Hello there',
                'unread_count': 0
            },
            {
                'id': 789012,
                'name': 'Spam Group 1',
                'type': 'group',
                'username': 'spamgroup1',
                'last_message': 'Group message',
                'unread_count': 3
            },
            {
                'id': 345678,
                'name': 'Spam Channel',
                'type': 'channel',
                'username': 'spamchannel',
                'last_message': 'Channel update',
                'unread_count': 1
            }
        ]
        
        return jsonify({'chats': chats})
        
    except Exception as e:
        return jsonify({'error': f'Failed to get chats: {str(e)}'}), 500

@app.route('/api/telegram/messages', methods=['GET'])
def get_messages():
    """Get message history"""
    try:
        chat_id = request.args.get('chat_id')
        if not chat_id:
            return jsonify({'error': 'chat_id parameter required'}), 400
        
        # Mock message history
        messages = [
            {
                'id': 1,
                'chat_id': int(chat_id),
                'message': 'Spam message 1',
                'timestamp': '2024-01-01T10:00:00Z',
                'sender': 'bot'
            },
            {
                'id': 2,
                'chat_id': int(chat_id),
                'message': 'Spam message 2',
                'timestamp': '2024-01-01T11:00:00Z',
                'sender': 'bot'
            },
            {
                'id': 3,
                'chat_id': int(chat_id),
                'message': 'Another spam message',
                'timestamp': '2024-01-01T12:00:00Z',
                'sender': 'bot'
            }
        ]
        
        return jsonify({'messages': messages})
        
    except Exception as e:
        return jsonify({'error': f'Failed to get messages: {str(e)}'}), 500

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Get system status"""
    return jsonify({
        'status': 'running',
        'active_bots': 3,
        'total_sessions': 3,
        'message': 'Full API server with spam functionality ready',
        'endpoints': {
            'bots': '/api/telegram/bots',
            'send_code': '/api/telegram/send-code',
            'verify_code': '/api/telegram/verify-code',
            'verify_2fa': '/api/telegram/verify-2fa',
            'send_message': '/api/telegram/send-message',
            'get_chats': '/api/telegram/chats',
            'get_messages': '/api/telegram/messages'
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Full Telegram API with SPAM functionality on http://localhost:5050")
    print("📱 Complete multi-bot system with messaging capabilities")
    print("💬 SPAM ENDPOINTS ACTIVE:")
    print("  POST /api/telegram/send-message - Send spam messages")
    print("  GET  /api/telegram/chats - Get spam targets")
    print("  GET  /api/telegram/messages - Get message history")
    print("🤖 Bot Authentication:")
    print("  GET  /api/telegram/bots - List bots")
    print("  POST /api/telegram/send-code - Send verification code")
    print("  POST /api/telegram/verify-code - Verify SMS code")
    print("  POST /api/telegram/verify-2fa - Verify 2FA")
    print("🎯 READY FOR SPAM OPERATIONS!")
    app.run(host='0.0.0.0', port=5050, debug=True)