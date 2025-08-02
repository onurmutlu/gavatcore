#!/usr/bin/env python3
"""
Production Telegram Authentication API for GavatCore Panel
Handles phone authentication, code verification, and 2FA with real Telegram integration
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
from telethon import TelegramClient, events
from telethon.errors import (
    PhoneNumberInvalidError, 
    PhoneCodeInvalidError, 
    SessionPasswordNeededError,
    PasswordHashInvalidError,
    FloodWaitError
)
from telethon.sessions import StringSession

app = Flask(__name__)
CORS(app)

# Configuration - Load from .env
from dotenv import load_dotenv
load_dotenv()

# Telegram API credentials
API_ID = int(os.getenv('TELEGRAM_API_ID', '22526488'))
API_HASH = os.getenv('TELEGRAM_API_HASH', '69924629dedc1034559fb4527238212a')
SESSION_DIR = Path('sessions')
SESSION_DIR.mkdir(exist_ok=True)

# Bot configurations with their phone numbers
BOT_CONFIGS = {
    'lara': {
        'phone': os.getenv('YAYINCILARA_PHONE', '+905382617727'),
        'display_name': 'Lara - Flirty Streamer',
        'persona_file': 'data/personas/yayincilara.json'
    },
    'babagavat': {
        'phone': os.getenv('GAWATBABA_PHONE', '+447832134241'),
        'display_name': 'BabaGavat - Club Leader', 
        'persona_file': 'data/personas/babagavat.json'
    },
    'geisha': {
        'phone': os.getenv('XXXGEISHA_PHONE', '+905486306226'),
        'display_name': 'Geisha - Sophisticated Moderator',
        'persona_file': 'data/personas/xxxgeisha.json'
    }
}

# Store active clients and auth sessions per bot
active_clients: Dict[str, TelegramClient] = {}
auth_sessions: Dict[str, Dict] = {}

def get_session_file(bot_name: str, phone: str = None) -> Path:
    """Get session file path for a specific bot"""
    if phone is None:
        phone = BOT_CONFIGS.get(bot_name, {}).get('phone', '')
    clean_phone = phone.replace('+', '').replace('-', '').replace(' ', '')
    return SESSION_DIR / f"{bot_name}_{clean_phone}.session"

def get_bot_config(bot_name: str) -> Dict:
    """Get bot configuration by name"""
    return BOT_CONFIGS.get(bot_name, {})

@app.route('/api/telegram/bots', methods=['GET'])
def get_available_bots():
    """Get list of available bots with their configurations"""
    try:
        bots = []
        for bot_name, config in BOT_CONFIGS.items():
            session_file = get_session_file(bot_name)
            session_exists = session_file.exists()
            
            bots.append({
                'name': bot_name,
                'display_name': config['display_name'],
                'phone': config['phone'],
                'session_exists': session_exists,
                'status': 'authenticated' if session_exists else 'needs_auth'
            })
        
        return jsonify({'bots': bots})
        
    except Exception as e:
        print(f"Get bots error: {e}")
        return jsonify({'error': 'Failed to get bot list'}), 500

@app.route('/api/telegram/send-code', methods=['POST', 'OPTIONS'])
def send_code():
    """Send verification code to phone number for a specific bot"""
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})
    
    try:
        data = request.get_json()
        bot_name = data.get('bot_name') if data else None
        
        print(f"DEBUG: Received send-code request for bot: {bot_name}")
        
        if not bot_name or bot_name not in BOT_CONFIGS:
            print(f"DEBUG: Invalid bot name: {bot_name}")
            return jsonify({'error': 'Invalid or missing bot name'}), 400
        
        bot_config = BOT_CONFIGS[bot_name]
        phone = bot_config['phone']
        
        print(f"DEBUG: Using phone: {phone} for bot: {bot_name}")
        
        # Check if we have valid credentials
        if not API_ID or not API_HASH:
            print("DEBUG: Missing Telegram API credentials")
            return jsonify({'error': 'Telegram API credentials not configured'}), 500
        
        # Create new client for this bot
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        
        async def send_auth_code():
            try:
                print("DEBUG: Connecting to Telegram...")
                await client.connect()
                print("DEBUG: Connected successfully")
                
                print(f"DEBUG: Sending code request to {phone}")
                # Send code request
                code_request = await client.send_code_request(phone)
                print(f"DEBUG: Code request successful")
                
                # Store client and session info with bot name
                session_id = f"{bot_name}_{datetime.now().timestamp()}"
                active_clients[session_id] = client
                auth_sessions[session_id] = {
                    'bot_name': bot_name,
                    'phone': phone,
                    'phone_code_hash': code_request.phone_code_hash,
                    'client': client,
                    'timestamp': datetime.now().isoformat()
                }
                
                print(f"DEBUG: Session created with ID: {session_id}")
                
                return {
                    'success': True,
                    'bot_name': bot_name,
                    'phone': phone,
                    'phone_code_hash': code_request.phone_code_hash,
                    'session_id': session_id
                }
            except FloodWaitError as e:
                print(f"DEBUG: Flood wait error: {e}")
                return {'error': f'Rate limited. Please wait {e.seconds} seconds and try again.'}
            except Exception as inner_e:
                print(f"DEBUG: Inner error: {inner_e}")
                raise inner_e
        
        # Handle asyncio event loop issue in Flask threads
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(send_auth_code())
        
        if 'error' in result:
            return jsonify(result), 429  # Too Many Requests
        
        print(f"DEBUG: Send code successful: {result}")
        return jsonify(result)
        
    except PhoneNumberInvalidError as e:
        print(f"DEBUG: Phone number invalid: {e}")
        return jsonify({'error': 'Invalid phone number'}), 400
    except Exception as e:
        print(f"DEBUG: Send code error: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to send verification code: {str(e)}'}), 500

@app.route('/api/telegram/verify-code', methods=['POST'])
def verify_code():
    """Verify the authentication code for a specific bot"""
    try:
        data = request.get_json()
        code = data.get('code')
        phone_code_hash = data.get('phone_code_hash')
        session_id = data.get('session_id')
        
        if not all([code, phone_code_hash, session_id]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Find session by session_id
        session_info = auth_sessions.get(session_id)
        if not session_info:
            return jsonify({'error': 'Session not found or expired'}), 400
        
        if session_info['phone_code_hash'] != phone_code_hash:
            return jsonify({'error': 'Invalid session data'}), 400
        
        client = session_info['client']
        bot_name = session_info['bot_name']
        phone = session_info['phone']
        
        async def verify_auth_code():
            try:
                # Sign in with code
                await client.sign_in(phone, code)
                
                # Get user info
                me = await client.get_me()
                
                # Save session with bot-specific filename
                session_string = client.session.save()
                session_file = get_session_file(bot_name, phone)
                
                # Save session to file for persistence
                with open(session_file, 'w') as f:
                    f.write(session_string)
                
                return {
                    'success': True,
                    'needs_password': False,
                    'bot_name': bot_name,
                    'session_data': session_string,
                    'user': {
                        'id': me.id,
                        'name': f"{me.first_name or ''} {me.last_name or ''}".strip(),
                        'email': f"{me.username}@telegram" if me.username else f"{me.id}@telegram",
                        'role': 'telegram_user',
                        'username': me.username,
                        'first_name': me.first_name,
                        'last_name': me.last_name,
                        'phone': me.phone,
                    }
                }
                
            except SessionPasswordNeededError:
                # 2FA is enabled
                return {
                    'success': False,
                    'needs_password': True,
                    'bot_name': bot_name,
                    'message': '2FA password required'
                }
        
        # Handle asyncio event loop issue in Flask threads
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(verify_auth_code())
        return jsonify(result)
        
    except PhoneCodeInvalidError:
        return jsonify({'error': 'Invalid verification code'}), 400
    except Exception as e:
        print(f"Code verification error: {e}")
        return jsonify({'error': 'Code verification failed'}), 500

@app.route('/api/telegram/verify-2fa', methods=['POST'])
def verify_2fa():
    """Verify 2FA password for a specific bot session"""
    try:
        data = request.get_json()
        password = data.get('password')
        session_id = data.get('session_id')
        
        if not all([password, session_id]):
            return jsonify({'error': 'Password and session_id required'}), 400
        
        # Find the specific session
        session_info = auth_sessions.get(session_id)
        if not session_info:
            return jsonify({'error': 'Session not found or expired'}), 400
        
        client = session_info['client']
        bot_name = session_info['bot_name']
        phone = session_info['phone']
        
        async def verify_2fa_password():
            try:
                # Sign in with 2FA password
                await client.sign_in(password=password)
                
                # Get user info
                me = await client.get_me()
                
                # Save session with bot-specific filename
                session_string = client.session.save()
                session_file = get_session_file(bot_name, phone)
                
                with open(session_file, 'w') as f:
                    f.write(session_string)
                
                return {
                    'success': True,
                    'bot_name': bot_name,
                    'session_data': session_string,
                    'user': {
                        'id': me.id,
                        'name': f"{me.first_name or ''} {me.last_name or ''}".strip(),
                        'email': f"{me.username}@telegram" if me.username else f"{me.id}@telegram",
                        'role': 'telegram_user',
                        'username': me.username,
                        'first_name': me.first_name,
                        'last_name': me.last_name,
                        'phone': me.phone,
                    }
                }
                
            except PasswordHashInvalidError:
                return {
                    'success': False,
                    'bot_name': bot_name,
                    'error': 'Invalid 2FA password'
                }
        
        # Handle asyncio event loop issue in Flask threads
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(verify_2fa_password())
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        print(f"2FA verification error: {e}")
        return jsonify({'error': '2FA verification failed'}), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with system information"""
    return jsonify({
        'service': 'GavatCore Multi-Bot Telegram Authentication API',
        'version': '1.0.0',
        'status': 'running',
        'mode': 'production',
        'endpoints': {
            'bots': '/api/telegram/bots',
            'send_code': '/api/telegram/send-code',
            'verify_code': '/api/telegram/verify-code',
            'verify_2fa': '/api/telegram/verify-2fa',
            'status': '/api/system/status'
        },
        'available_bots': list(BOT_CONFIGS.keys()),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Get system status"""
    return jsonify({
        'status': 'running',
        'active_bots': len(active_clients),
        'total_sessions': len(list(SESSION_DIR.glob("*.session"))),
        'timestamp': datetime.now().isoformat(),
        'mode': 'production'
    })

if __name__ == '__main__':
    print("🚀 Starting Production Telegram Auth API on http://localhost:5050")
    print("📱 Multi-Bot Authentication System")
    print("🔐 Real Telegram Integration Enabled")
    print("\n📋 Available Endpoints:")
    print("  GET  /api/telegram/bots - List available bots")
    print("  POST /api/telegram/send-code - Send verification code")
    print("  POST /api/telegram/verify-code - Verify SMS code")
    print("  POST /api/telegram/verify-2fa - Verify 2FA password")
    print("  GET  /api/system/status - System status")
    print("\n🤖 Available Bots:")
    for name, config in BOT_CONFIGS.items():
        print(f"  - {config['display_name']} ({config['phone']})")
    
    app.run(host='0.0.0.0', port=5050, debug=True)