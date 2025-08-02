#!/usr/bin/env python3
"""
Telegram Authentication API for GavatCore Panel
Handles phone authentication, code verification, and 2FA
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
    PasswordHashInvalidError
)
from telethon.sessions import StringSession

app = Flask(__name__)
CORS(app)

# Configuration - Load from .env
from dotenv import load_dotenv
load_dotenv()

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

@app.route('/api/telegram/validate-session', methods=['POST'])
def validate_session():
    """Validate an existing Telegram session for a specific bot"""
    try:
        data = request.get_json()
        bot_name = data.get('bot_name')
        session_data = data.get('session_data')
        
        if not bot_name or bot_name not in BOT_CONFIGS:
            return jsonify({'error': 'Invalid or missing bot name'}), 400
            
        if not session_data:
            # Try to load from session file
            session_file = get_session_file(bot_name)
            if session_file.exists():
                with open(session_file, 'r') as f:
                    session_data = f.read().strip()
            else:
                return jsonify({'valid': False, 'error': 'No session found'}), 400
            
        # Try to create client with session string
        client = TelegramClient(StringSession(session_data), API_ID, API_HASH)
        
        async def check_auth():
            await client.connect()
            if await client.is_user_authorized():
                me = await client.get_me()
                return {
                    'valid': True,
                    'bot_name': bot_name,
                    'user': {
                        'id': me.id,
                        'username': me.username,
                        'first_name': me.first_name,
                        'last_name': me.last_name,
                        'phone': me.phone,
                    }
                }
            await client.disconnect()
            return {'valid': False, 'bot_name': bot_name}
        
        result = asyncio.run(check_auth())
        return jsonify(result)
        
    except Exception as e:
        print(f"Session validation error: {e}")
        return jsonify({'error': 'Session validation failed'}), 500

@app.route('/api/telegram/send-code', methods=['POST'])
def send_code():
    """Send verification code to phone number for a specific bot"""
    try:
        data = request.get_json()
        bot_name = data.get('bot_name')
        
        print(f"DEBUG: Received send-code request: {data}")
        print(f"DEBUG: Bot name: {bot_name}")
        print(f"DEBUG: Available bots: {list(BOT_CONFIGS.keys())}")
        
        if not bot_name or bot_name not in BOT_CONFIGS:
            print(f"DEBUG: Invalid bot name: {bot_name}")
            return jsonify({'error': 'Invalid or missing bot name'}), 400
        
        bot_config = BOT_CONFIGS[bot_name]
        phone = bot_config['phone']
        
        print(f"DEBUG: Using phone: {phone} for bot: {bot_name}")
        print(f"DEBUG: API_ID: {API_ID}, API_HASH: {API_HASH[:10]}...")
        
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
                print(f"DEBUG: Code request successful, hash: {code_request.phone_code_hash[:10]}...")
                
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
            except Exception as inner_e:
                print(f"DEBUG: Inner async error: {inner_e}")
                print(f"DEBUG: Inner async error type: {type(inner_e)}")
                raise inner_e
        
        result = asyncio.run(send_auth_code())
        print(f"DEBUG: Send code result: {result}")
        return jsonify(result)
        
    except PhoneNumberInvalidError as e:
        print(f"DEBUG: Phone number invalid: {e}")
        return jsonify({'error': 'Invalid phone number'}), 400
    except Exception as e:
        print(f"DEBUG: Send code error: {e}")
        print(f"DEBUG: Send code error type: {type(e)}")
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
        
        result = asyncio.run(verify_auth_code())
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
        
        result = asyncio.run(verify_2fa_password())
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        print(f"2FA verification error: {e}")
        return jsonify({'error': '2FA verification failed'}), 500

@app.route('/api/telegram/send-message', methods=['POST'])
def send_message():
    """Send a message through Telegram using a specific bot"""
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        message = data.get('message')
        bot_name = data.get('bot_name')
        
        if not all([chat_id, message, bot_name]):
            return jsonify({'error': 'Chat ID, message, and bot_name required'}), 400
        
        if bot_name not in BOT_CONFIGS:
            return jsonify({'error': 'Invalid bot name'}), 400
        
        # Load bot-specific session
        session_file = get_session_file(bot_name)
        if not session_file.exists():
            return jsonify({'error': f'No session found for bot {bot_name}'}), 400
        
        with open(session_file, 'r') as f:
            session_string = f.read().strip()
        
        client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
        
        async def send_telegram_message():
            await client.connect()
            
            if not await client.is_user_authorized():
                return {'error': f'Bot {bot_name} session not authorized'}
            
            # Send message
            sent_message = await client.send_message(int(chat_id), message)
            
            await client.disconnect()
            
            return {
                'success': True,
                'bot_name': bot_name,
                'message_id': sent_message.id,
                'date': sent_message.date.isoformat(),
                'text': sent_message.text
            }
        
        result = asyncio.run(send_telegram_message())
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Send message error: {e}")
        return jsonify({'error': 'Failed to send message'}), 500

@app.route('/api/telegram/messages', methods=['GET'])
def get_messages():
    """Get messages from Telegram using a specific bot"""
    try:
        chat_id = request.args.get('chat_id')
        bot_name = request.args.get('bot_name')
        limit = int(request.args.get('limit', 50))
        
        if not bot_name:
            return jsonify({'error': 'bot_name parameter required'}), 400
        
        if bot_name not in BOT_CONFIGS:
            return jsonify({'error': 'Invalid bot name'}), 400
        
        # Load bot-specific session
        session_file = get_session_file(bot_name)
        if not session_file.exists():
            return jsonify({'error': f'No session found for bot {bot_name}'}), 400
        
        with open(session_file, 'r') as f:
            session_string = f.read().strip()
        
        client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
        
        async def get_telegram_messages():
            await client.connect()
            
            if not await client.is_user_authorized():
                return {'error': f'Bot {bot_name} session not authorized'}
            
            messages = []
            
            if chat_id:
                # Get messages from specific chat
                async for message in client.iter_messages(int(chat_id), limit=limit):
                    messages.append({
                        'id': message.id,
                        'text': message.text or '',
                        'date': message.date.isoformat(),
                        'from_id': message.from_id.user_id if message.from_id else None,
                        'from_bot': message.out,  # True if sent by us
                    })
            
            await client.disconnect()
            return {'messages': messages, 'bot_name': bot_name}
        
        result = asyncio.run(get_telegram_messages())
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Get messages error: {e}")
        return jsonify({'error': 'Failed to get messages'}), 500

@app.route('/api/telegram/chats', methods=['GET'])
def get_chats():
    """Get list of chats for a specific bot"""
    try:
        bot_name = request.args.get('bot_name')
        
        if not bot_name:
            return jsonify({'error': 'bot_name parameter required'}), 400
        
        if bot_name not in BOT_CONFIGS:
            return jsonify({'error': 'Invalid bot name'}), 400
        
        # Load bot-specific session
        session_file = get_session_file(bot_name)
        if not session_file.exists():
            return jsonify({'error': f'No session found for bot {bot_name}'}), 400
        
        with open(session_file, 'r') as f:
            session_string = f.read().strip()
        
        client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
        
        async def get_telegram_chats():
            await client.connect()
            
            if not await client.is_user_authorized():
                return {'error': f'Bot {bot_name} session not authorized'}
            
            chats = []
            
            # Get dialogs (recent chats)
            async for dialog in client.iter_dialogs(limit=50):
                chat_info = {
                    'id': dialog.id,
                    'title': dialog.title or dialog.name,
                    'is_user': dialog.is_user,
                    'is_group': dialog.is_group,
                    'is_channel': dialog.is_channel,
                }
                
                if dialog.is_user:
                    chat_info['first_name'] = getattr(dialog.entity, 'first_name', '')
                    chat_info['last_name'] = getattr(dialog.entity, 'last_name', '')
                    chat_info['username'] = getattr(dialog.entity, 'username', '')
                
                chats.append(chat_info)
            
            await client.disconnect()
            return {'chats': chats, 'bot_name': bot_name}
        
        result = asyncio.run(get_telegram_chats())
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Get chats error: {e}")
        return jsonify({'error': 'Failed to get chats'}), 500

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Get system status"""
    return jsonify({
        'status': 'running',
        'active_bots': len(active_clients),
        'total_sessions': len(list(SESSION_DIR.glob("*.session"))),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Telegram Auth API on http://localhost:5050")
    print("📱 Endpoints:")
    print("  POST /api/telegram/send-code - Send verification code")
    print("  POST /api/telegram/verify-code - Verify code")
    print("  POST /api/telegram/verify-2fa - Verify 2FA")
    print("  POST /api/telegram/send-message - Send message")
    print("  GET  /api/telegram/messages - Get messages")
    print("  GET  /api/telegram/chats - Get chats")
    print("  GET  /api/system/status - System status")
    
    app.run(host='0.0.0.0', port=5050, debug=True)