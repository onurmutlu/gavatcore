#!/usr/bin/env python3
"""
🔐 Telegram Authentication Setup for Yağmur Bot
===============================================

This script handles the initial Telegram authentication process
for the Yağmur bot using phone number +447832134241 and creates
a proper session file.

Features:
- Interactive phone number authentication
- SMS/Call code verification
- 2FA password support if enabled
- Session file creation and validation
- Error handling and retry logic
"""

import asyncio
import os
import sys

from telethon import TelegramClient, events
from telethon.errors import (
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)

from config import TELEGRAM_API_HASH, TELEGRAM_API_ID


class TelegramAuthenticator:
    def __init__(self):
        self.phone = "+447832134241"  # Yağmur bot phone number
        self.session_name = "sessions/_447832134241"
        self.client = None

    async def authenticate(self):
        """Complete Telegram authentication process"""
        print("🔐 Telegram Authentication Setup for Yağmur Bot")
        print("=" * 50)
        print(f"📱 Phone Number: {self.phone}")
        print(f"💾 Session File: {self.session_name}.session")
        print("=" * 50)

        # Create Telegram client
        self.client = TelegramClient(
            self.session_name,
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH,
            device_model="Yağmur Bot",
            system_version="GAVATCore v2.0",
            app_version="1.0.0",
        )

        try:
            print("🔄 Connecting to Telegram...")
            await self.client.connect()

            # Check if already authenticated
            if await self.client.is_user_authorized():
                print("✅ Already authenticated!")
                me = await self.client.get_me()
                print(f"🎯 Logged in as: @{me.username} ({me.first_name})")
                return True

            print("📞 Starting phone authentication...")

            # Send authentication code
            try:
                await self.client.send_code_request(self.phone)
                print(f"📨 Authentication code sent to {self.phone}")
                print("📱 Check your Telegram app or SMS for the verification code")
            except PhoneNumberInvalidError:
                print(f"❌ Invalid phone number: {self.phone}")
                return False
            except Exception as e:
                print(f"❌ Error sending code: {e}")
                return False

            # Get verification code from user
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    code = input(
                        f"\n🔢 Enter verification code (attempt {attempt + 1}/{max_attempts}): "
                    ).strip()

                    if not code:
                        print("❌ Code cannot be empty!")
                        continue

                    print("🔄 Verifying code...")
                    await self.client.sign_in(self.phone, code)
                    break

                except PhoneCodeInvalidError:
                    print(f"❌ Invalid code! {max_attempts - attempt - 1} attempts remaining.")
                    if attempt == max_attempts - 1:
                        print("❌ Too many failed attempts. Please try again later.")
                        return False
                except SessionPasswordNeededError:
                    print("🔐 2FA is enabled. Please enter your password.")
                    password = input("🔑 Enter 2FA password: ").strip()
                    try:
                        await self.client.sign_in(password=password)
                        break
                    except Exception as e:
                        print(f"❌ 2FA authentication failed: {e}")
                        return False
                except Exception as e:
                    print(f"❌ Unexpected error: {e}")
                    return False

            # Verify authentication
            if await self.client.is_user_authorized():
                me = await self.client.get_me()
                print(f"\n✅ Authentication successful!")
                print(f"👤 Username: @{me.username}")
                print(f"📝 Name: {me.first_name} {me.last_name or ''}")
                print(f"🆔 User ID: {me.id}")
                print(f"📞 Phone: {me.phone}")

                # Verify session file creation
                session_file = f"{self.session_name}.session"
                if os.path.exists(session_file):
                    size = os.path.getsize(session_file)
                    print(f"💾 Session file created: {session_file} ({size} bytes)")
                else:
                    print("⚠️ Session file not found!")

                return True
            else:
                print("❌ Authentication failed!")
                return False

        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
        finally:
            if self.client:
                await self.client.disconnect()

    async def test_session(self):
        """Test the created session file"""
        print("\n🧪 Testing session file...")

        test_client = TelegramClient(self.session_name, TELEGRAM_API_ID, TELEGRAM_API_HASH)

        try:
            await test_client.connect()

            if await test_client.is_user_authorized():
                me = await test_client.get_me()
                print(f"✅ Session test successful!")
                print(f"👤 Connected as: @{me.username}")

                # Get dialog count for additional verification
                dialog_count = 0
                async for dialog in test_client.iter_dialogs(limit=10):
                    dialog_count += 1

                print(f"💬 Can access {dialog_count} dialogs")
                return True
            else:
                print("❌ Session test failed - not authorized")
                return False

        except Exception as e:
            print(f"❌ Session test error: {e}")
            return False
        finally:
            await test_client.disconnect()


async def main():
    """Main authentication flow"""
    print("🚀 Starting Telegram Authentication Setup...")

    # Check if API credentials are configured
    try:
        print(f"🔑 API ID: {TELEGRAM_API_ID}")
        print(
            f"🔑 API Hash: {'*' * (len(str(TELEGRAM_API_HASH)) - 4) + str(TELEGRAM_API_HASH)[-4:]}"
        )
    except:
        print("❌ Telegram API credentials not found!")
        print("   Please configure TELEGRAM_API_ID and TELEGRAM_API_HASH in your config")
        return False

    # Create sessions directory if it doesn't exist
    os.makedirs("sessions", exist_ok=True)

    # Start authentication
    authenticator = TelegramAuthenticator()

    success = await authenticator.authenticate()

    if success:
        print("\n🎉 Authentication completed successfully!")

        # Test the session
        test_success = await authenticator.test_session()

        if test_success:
            print("\n✅ Session file is working properly!")
            print("🎯 You can now start the Yağmur bot system!")
            return True
        else:
            print("\n⚠️ Session created but test failed. Please try authentication again.")
            return False
    else:
        print("\n❌ Authentication failed!")
        print("💡 Please check your phone number and try again.")
        return False


if __name__ == "__main__":
    print("🔐 Telegram Authentication Setup for Yağmur Bot")
    print("=" * 60)

    try:
        result = asyncio.run(main())

        if result:
            print("\n🎯 Next steps:")
            print("1. Run: python3 -m services.telegram.bot_manager.bot_system")
            print("2. Or use: python3 services/telegram/bot_manager/bot_system.py")
            print("3. Check dashboard at: http://localhost:9095")
        else:
            print("\n💡 Authentication setup incomplete.")
            print("   Please run this script again and follow the prompts.")

    except KeyboardInterrupt:
        print("\n⏹️ Authentication cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
