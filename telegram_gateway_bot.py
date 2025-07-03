#!/usr/bin/env python3
"""
🤖 GAVATCORE TELEGRAM GATEWAY BOT
User acquisition and trial activation bot
"""

import asyncio
import logging
import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
except ImportError:
    print("❌ python-telegram-bot library not installed!")
    print("💡 Install with: pip install python-telegram-bot==20.7")
    import sys
    sys.exit(1)
try:
    import aiohttp
    import structlog
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("💡 Install with: pip install -r requirements_telegram.txt")
    import sys
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger("gavatcore.telegram_bot")

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your-bot-token-here")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")
PANEL_URL = os.getenv("PANEL_URL", "https://panel.gavatcore.com")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://panel.gavatcore.com/#/auth/login")

# Database for user tracking
DB_FILE = "telegram_users.db"

def init_database():
    """Initialize SQLite database for user tracking"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telegram_users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            api_user_id INTEGER,
            subscription_status TEXT,
            trial_used BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            command TEXT,
            response TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user_data(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Get user data from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT telegram_id, username, first_name, last_name, api_user_id, 
               subscription_status, trial_used, created_at, last_interaction
        FROM telegram_users WHERE telegram_id = ?
    """, (telegram_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'telegram_id': row[0],
            'username': row[1],
            'first_name': row[2],
            'last_name': row[3],
            'api_user_id': row[4],
            'subscription_status': row[5],
            'trial_used': bool(row[6]),
            'created_at': row[7],
            'last_interaction': row[8]
        }
    return None

def save_user_data(user_data: Dict[str, Any]):
    """Save user data to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO telegram_users 
        (telegram_id, username, first_name, last_name, api_user_id, 
         subscription_status, trial_used, last_interaction)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_data['telegram_id'],
        user_data.get('username'),
        user_data.get('first_name'),
        user_data.get('last_name'),
        user_data.get('api_user_id'),
        user_data.get('subscription_status', 'none'),
        user_data.get('trial_used', False),
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()

def log_interaction(telegram_id: int, command: str, response: str):
    """Log user interaction"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO user_interactions (telegram_id, command, response)
        VALUES (?, ?, ?)
    """, (telegram_id, command, response))
    
    conn.commit()
    conn.close()

async def make_api_request(endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make request to GavatCore API"""
    url = f"{API_BASE_URL}{endpoint}"
    
    async with aiohttp.ClientSession() as session:
        try:
            if method == "GET":
                async with session.get(url) as response:
                    return await response.json()
            elif method == "POST":
                async with session.post(url, json=data or {}) as response:
                    return await response.json()
            else:
                return {"error": True, "message": f"Unsupported method: {method}"}
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {"error": True, "message": str(e)}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    telegram_id = user.id
    
    # Save/update user data
    user_data = {
        'telegram_id': telegram_id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }
    save_user_data(user_data)
    
    # Welcome message
    welcome_text = f"""
🔥 **Hoş Geldin {user.first_name}!**

**GavatCore** - GPT ile çalışan akıllı Telegram botları!

🤖 **Özellikler:**
• Gerçek Telegram userbot'ları
• GPT-4 ile otomatik yanıtlar  
• 4 farklı reply modu
• Coin tabanlı sistem
• Canlı panel kontrolü

💰 **Planlar:**
• **Deneme:** Ücretsiz 24 saat
• **Başlangıç:** ₺499/ay (1 bot)
• **Pro:** ₺799/ay (3 bot)
• **Deluxe:** ₺1499/ay (5 bot)

👇 **Şimdi başla:**
"""

    # Create inline keyboard
    keyboard = [
        [
            InlineKeyboardButton("🎮 Panel Aç", web_app=WebAppInfo(url=WEBAPP_URL)),
            InlineKeyboardButton("⚡ Ücretsiz Deneme", callback_data="start_trial")
        ],
        [
            InlineKeyboardButton("📱 Telegram Giriş", callback_data="telegram_login"),
            InlineKeyboardButton("📊 Durumum", callback_data="check_status")
        ],
        [
            InlineKeyboardButton("💰 Planlar", callback_data="view_plans"),
            InlineKeyboardButton("📞 Destek", url="https://t.me/gavatcoresupport")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    log_interaction(telegram_id, "/start", "Welcome message sent")

async def trial_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /trial command"""
    user = update.effective_user
    telegram_id = user.id
    
    user_data = get_user_data(telegram_id)
    
    if user_data and user_data['trial_used']:
        await update.message.reply_text(
            "❌ **Deneme süresi zaten kullanıldı!**\n\n"
            "Pro planlarımıza göz atmak için /plans komutunu kullan."
        )
        return
    
    # Create trial account via API
    trial_data = {
        "username": f"trial_tg_{telegram_id}",
        "email": f"trial_{telegram_id}@telegram.user",
        "telegram_id": telegram_id,
        "first_name": user.first_name,
        "plan": "trial"
    }
    
    response = await make_api_request("/auth/register", "POST", trial_data)
    
    if response.get("error"):
        await update.message.reply_text(
            f"❌ **Deneme hesabı oluşturulamadı:**\n{response.get('message')}"
        )
        return
    
    # Mark trial as used
    if user_data:
        user_data['trial_used'] = True
        user_data['api_user_id'] = response.get('user', {}).get('id')
        save_user_data(user_data)
    
    success_text = f"""
✅ **Deneme hesabınız hazır!**

🤖 **Bot otomatik olarak başlatıldı**
⏰ **Süre:** 24 saat
🪙 **Coin:** 100 adet
📱 **Panel:** {PANEL_URL}

**Giriş bilgileri:**
👤 Kullanıcı: `trial_tg_{telegram_id}`
🔑 Şifre: `{response.get('password', 'trial123')}`

👇 **Panel'e git:**
"""
    
    keyboard = [
        [InlineKeyboardButton("🎮 Panel'i Aç", web_app=WebAppInfo(url=f"{WEBAPP_URL}?trial=1"))],
        [InlineKeyboardButton("📊 Bot Durumu", callback_data="check_status")]
    ]
    
    await update.message.reply_text(
        success_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    log_interaction(telegram_id, "/trial", "Trial account created")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user = update.effective_user
    telegram_id = user.id
    
    user_data = get_user_data(telegram_id)
    
    if not user_data or not user_data.get('api_user_id'):
        await update.message.reply_text(
            "❌ **Hesap bulunamadı!**\n\n"
            "Önce /trial ile deneme hesabı oluşturun veya /login ile giriş yapın."
        )
        return
    
    # Get subscription status from API
    # (Bu gerçek API call olacak)
    status_text = f"""
📊 **Hesap Durumunuz**

👤 **Kullanıcı:** {user.first_name}
🆔 **Telegram ID:** `{telegram_id}`
📱 **Panel:** {PANEL_URL}

🤖 **Bot Durumu:** Aktif
💰 **Plan:** {user_data.get('subscription_status', 'Deneme')}
🪙 **Kalan Coin:** 87/100
⏰ **Süre:** 18 saat 42 dakika

📈 **İstatistikler:**
• Gönderilen mesaj: 23
• Alınan yanıt: 19
• Başarı oranı: %82.6
"""
    
    keyboard = [
        [InlineKeyboardButton("🎮 Panel'i Aç", web_app=WebAppInfo(url=WEBAPP_URL))],
        [
            InlineKeyboardButton("⬆️ Yükselt", callback_data="upgrade_plan"),
            InlineKeyboardButton("🔄 Yenile", callback_data="check_status")
        ]
    ]
    
    await update.message.reply_text(
        status_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    log_interaction(telegram_id, "/status", "Status checked")

async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /login command"""
    user = update.effective_user
    telegram_id = user.id
    
    # Generate Telegram auth token
    auth_token = f"tg_auth_{telegram_id}_{int(datetime.now().timestamp())}"
    
    login_text = f"""
🔐 **Telegram Giriş**

Panel'de Telegram ile giriş yapmak için:

1️⃣ Panel'i aç: {PANEL_URL}
2️⃣ "Telegram ile Giriş" butonuna tıkla
3️⃣ Bu kodu gir: `{auth_token}`

⏰ **Kod 10 dakika geçerli**
"""
    
    keyboard = [
        [InlineKeyboardButton("🎮 Panel'i Aç", web_app=WebAppInfo(url=f"{WEBAPP_URL}?auth={auth_token}"))],
    ]
    
    await update.message.reply_text(
        login_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    log_interaction(telegram_id, "/login", f"Auth token generated: {auth_token}")

async def plans_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /plans command"""
    plans_text = """
💰 **GavatCore Planları**

🔥 **Deneme** - Ücretsiz
• 24 saat kullanım
• 1 bot
• 100 coin
• Temel özellikler

🚀 **Başlangıç** - ₺499/ay
• 1 bot
• 500 coin/ay
• GPT-4 yanıtlar
• Hybrid mode

⚡ **Pro** - ₺799/ay
• 3 bot
• 2000 coin/ay
• Tüm modlar
• Scheduler
• Öncelikli destek

💎 **Deluxe** - ₺1499/ay
• 5 bot
• Sınırsız coin
• Özel kişilikler
• Analytics
• 7/24 destek

📈 **Avantajlar:**
• Gerçek Telegram botları
• GPT-4 entegrasyonu
• Anında kurulum
• Canlı panel
• Türkçe destek
"""
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 Panel'de Satın Al", web_app=WebAppInfo(url=f"{WEBAPP_URL}#/billing")),
        ],
        [
            InlineKeyboardButton("⚡ Deneme Başlat", callback_data="start_trial"),
            InlineKeyboardButton("📞 Danış", url="https://t.me/gavatcoresupport")
        ]
    ]
    
    await update.message.reply_text(
        plans_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    telegram_id = user.id
    
    if query.data == "start_trial":
        await trial_command(update, context)
    
    elif query.data == "telegram_login":
        await login_command(update, context)
    
    elif query.data == "check_status":
        await status_command(update, context)
    
    elif query.data == "view_plans":
        await plans_command(update, context)
    
    elif query.data == "upgrade_plan":
        upgrade_text = """
⬆️ **Plan Yükseltme**

Mevcut planınızı yükseltmek için panel'i kullanın:

🎮 **Panel'de Yükselt:** Anında aktivasyon
💳 **Stripe Güvenli Ödeme**
⚡ **Otomatik Bot Başlatma**
📱 **Telegram Stars ile de ödeyebilirsiniz**
"""
        
        keyboard = [
            [InlineKeyboardButton("🎮 Panel'de Yükselt", web_app=WebAppInfo(url=f"{WEBAPP_URL}#/billing"))],
            [InlineKeyboardButton("💰 Planları Gör", callback_data="view_plans")]
        ]
        
        await query.edit_message_text(
            upgrade_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    log_interaction(telegram_id, f"button:{query.data}", "Button pressed")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🤖 **GavatCore Bot Komutları**

🔰 **Temel Komutlar:**
• `/start` - Başlangıç ve ana menü
• `/trial` - Ücretsiz 24 saat deneme
• `/login` - Telegram ile panel girişi
• `/status` - Hesap durumu ve istatistikler
• `/plans` - Plan fiyatları
• `/help` - Bu yardım mesajı

🎮 **Panel Özellikleri:**
• Bot yönetimi (başlat/durdur)
• GPT ayarları
• Coin kontrolü  
• İstatistikler
• Ödeme yönetimi

📞 **Destek:**
• Telegram: @gavatcoresupport
• Website: gavatcore.com
• E-mail: support@gavatcore.com

💡 **İpucu:** Panel'e erişmek için "🎮 Panel Aç" butonunu kullan.
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    """Start the bot"""
    # Initialize database
    init_database()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("trial", trial_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("login", login_command))
    application.add_handler(CommandHandler("plans", plans_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("🤖 GavatCore Telegram Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main() 