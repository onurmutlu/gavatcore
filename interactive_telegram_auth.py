#!/usr/bin/env python3
"""
🔐 Interactive Telegram Authentication for Yağmur Bot
====================================================

This script provides an interactive authentication flow that will
wait for your input to complete the Telegram authentication process.
"""

import asyncio
import os
import sys

from telethon import TelegramClient
from telethon.errors import (
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)

from config import TELEGRAM_API_HASH, TELEGRAM_API_ID


async def authenticate_yagmur_bot():
    """Interactive authentication for Yağmur bot"""
    phone = "+447832134241"
    session_name = "sessions/_447832134241"

    print("🔐 Interactive Telegram Authentication")
    print("=" * 50)
    print(f"📱 Phone: {phone}")
    print(f"💾 Session: {session_name}.session")
    print("=" * 50)

    # Create client
    client = TelegramClient(
        session_name,
        TELEGRAM_API_ID,
        TELEGRAM_API_HASH,
        device_model="Yağmur Bot",
        system_version="GAVATCore v2.0",
    )

    try:
        print("🔄 Connecting to Telegram...")
        await client.connect()

        # Check if already authenticated
        if await client.is_user_authorized():
            print("✅ Already authenticated!")
            me = await client.get_me()
            print(f"👤 Logged in as: @{me.username} ({me.first_name})")
            return True

        print(f"📞 Sending authentication code to {phone}...")

        # This will prompt you in the terminal
        await client.start(phone)

        # Verify authentication
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"\n✅ Authentication successful!")
            print(f"👤 Username: @{me.username}")
            print(f"📝 Name: {me.first_name} {me.last_name or ''}")
            print(f"🆔 User ID: {me.id}")

            # Check session file
            session_file = f"{session_name}.session"
            if os.path.exists(session_file):
                size = os.path.getsize(session_file)
                print(f"💾 Session file: {session_file} ({size} bytes)")

            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await client.disconnect()

    return False


if __name__ == "__main__":
    print("🚀 Starting Interactive Telegram Authentication...")
    print("📋 Follow the prompts to authenticate your phone number.")
    print("📱 You'll be asked to enter the verification code from Telegram.")
    print()

    try:
        success = asyncio.run(authenticate_yagmur_bot())

        if success:
            print("\n🎉 Authentication completed successfully!")
            print("🎯 Next steps:")
            print("1. Run: python3 -m services.telegram.bot_manager.bot_system")
            print("2. Check dashboard at: http://localhost:9095")
            print("3. Monitor API at: http://localhost:5050")
        else:
            print("\n❌ Authentication failed!")
            print("💡 Please try again and make sure you have access to the phone.")

    except KeyboardInterrupt:
        print("\n⏹️ Authentication cancelled")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
