#!/usr/bin/env python3
"""
Baron Bot Launcher — GavatCore Final Single-User CLI
====================================================

Tek kullanıcı (Baron / +905325566496) için tüm launcher özelliklerini birleştirir:
- Persona + session yönetimi
- Onay kodu / 2FA onay şifresi
- Character Engine + GPT + AI blending
- DM ve grup mention handler
- Session doğrulama ve lock temizliği
- Analytics, graceful shutdown, structlog

Kullanım:
    python launchers/baron_bot_launcher.py start
    python launchers/baron_bot_launcher.py login --onay-kodu 12345
    python launchers/baron_bot_launcher.py status
    python launchers/baron_bot_launcher.py session-check
    python launchers/baron_bot_launcher.py cleanup-sessions
    python launchers/baron_bot_launcher.py test-gpt "Merhaba Baron"
    python launchers/baron_bot_launcher.py stats
    python launchers/baron_bot_launcher.py info
"""

from __future__ import annotations

import argparse
import asyncio
import glob
import json
import os
import signal
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from telethon.tl.types import User

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
from services.telegram.baron_bot_handler import (
    get_baron_stats,
    handle_baron_dm,
    handle_baron_group_message,
    test_baron_gpt,
)

logger = structlog.get_logger("baron_bot_launcher")

PERSONA_FILE = "data/personas/baron.json"
DEFAULT_PHONE = "+905325566496"
BOT_KEY = "baron"
VERSION = "1.0.0"


def _resolve_onay_kodu(cli_value: Optional[str] = None) -> Optional[str]:
    if cli_value:
        return cli_value.strip()
    for key in ("TELEGRAM_ONAY_KODU", "ONAY_KODU", "TELEGRAM_LOGIN_CODE"):
        value = os.getenv(key)
        if value and value.strip():
            return value.strip()
    return None


def _resolve_onay_sifresi(cli_value: Optional[str] = None) -> Optional[str]:
    if cli_value:
        return cli_value.strip()
    for key in ("TELEGRAM_ONAY_SIFRESI", "ONAY_SIFRESI", "TELEGRAM_2FA_PASSWORD"):
        value = os.getenv(key)
        if value and value.strip():
            return value.strip()
    return None


def _load_persona() -> Dict[str, Any]:
    if os.path.exists(PERSONA_FILE):
        with open(PERSONA_FILE, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return {
        "username": BOT_KEY,
        "display_name": "Baron",
        "phone": DEFAULT_PHONE,
        "reply_mode": "hybrid",
    }


def _session_stem(phone: str) -> str:
    clean = phone.replace("+", "").replace(" ", "").replace("-", "")
    return f"sessions/_{clean}"


def cleanup_session_locks() -> int:
    patterns = [
        "sessions/*.session-journal",
        "sessions/*.session-wal",
        "sessions/*.session-shm",
    ]
    removed = 0
    for pattern in patterns:
        for lock_file in glob.glob(pattern):
            try:
                os.remove(lock_file)
                removed += 1
                logger.info("Session lock temizlendi", file=lock_file)
            except OSError:
                pass
    return removed


def validate_session_file(session_path: str) -> Dict[str, Any]:
    result = {
        "path": session_path,
        "exists": os.path.exists(session_path),
        "size_kb": 0.0,
        "valid_sqlite": False,
        "authorized_hint": "unknown",
    }
    if not result["exists"]:
        return result

    result["size_kb"] = round(os.path.getsize(session_path) / 1024, 1)
    try:
        conn = sqlite3.connect(session_path, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions';"
        )
        result["valid_sqlite"] = cursor.fetchone() is not None
        conn.close()
    except sqlite3.Error as exc:
        result["error"] = str(exc)

    if result["size_kb"] < 10:
        result["authorized_hint"] = "probably_empty"
    elif result["valid_sqlite"]:
        result["authorized_hint"] = "structure_ok"
    return result


class BaronBotLauncher:
    def __init__(
        self,
        onay_kodu: Optional[str] = None,
        onay_sifresi: Optional[str] = None,
        dry_run: bool = False,
        no_gpt: bool = False,
    ):
        self.persona = _load_persona()
        self.display_name = self.persona.get("display_name", "Baron")
        self.phone = self.persona.get("phone", DEFAULT_PHONE)
        self.session_stem = _session_stem(self.phone)
        self.onay_kodu = onay_kodu
        self.onay_sifresi = onay_sifresi
        self.dry_run = dry_run
        self.no_gpt = no_gpt

        self.client: Optional[TelegramClient] = None
        self.bot_username = self.persona.get("username", BOT_KEY)
        self.is_running = False
        self.started_at: Optional[datetime] = None
        self.me_info: Dict[str, Any] = {}

    def _code_callback(self) -> str:
        kod = _resolve_onay_kodu(self.onay_kodu)
        if kod:
            print("🔑 Onay kodu ortam/argümandan alındı.")
            return kod
        return input("🔑 Telegram onay kodunu girin: ").strip()

    def _password_callback(self) -> str:
        sifre = _resolve_onay_sifresi(self.onay_sifresi)
        if sifre:
            print("🔒 Onay şifresi ortam/argümandan alındı.")
            return sifre
        import getpass

        return getpass.getpass("🔒 Telegram onay şifresini girin (2FA): ")

    async def connect(self, force_login: bool = False) -> bool:
        os.makedirs("sessions", exist_ok=True)
        if self.no_gpt:
            os.environ["BARON_AI_BLEND"] = "false"

        self.client = TelegramClient(
            self.session_stem,
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH,
            device_model=f"{self.display_name} Bot",
            system_version="GAVATCore v2.1",
            app_version=f"BaronLauncher/{VERSION}",
        )

        await self.client.connect()

        if force_login or not await self.client.is_user_authorized():
            print("⚠️ Session geçersiz — onay kodu/şifre ile giriş yapılıyor...")
            onay_sifresi = _resolve_onay_sifresi(self.onay_sifresi)
            await self.client.start(
                phone=self.phone,
                code_callback=self._code_callback,
                password=onay_sifresi if onay_sifresi else self._password_callback,
            )
        else:
            print("✅ Mevcut session ile giriş yapıldı.")

        me = await self.client.get_me()
        self.bot_username = me.username or self.bot_username
        self.me_info = {
            "id": me.id,
            "username": me.username,
            "first_name": me.first_name,
            "last_name": me.last_name,
            "phone": self.phone,
        }
        self.started_at = datetime.now()
        print(
            f"✅ {self.display_name} aktif: @{self.bot_username or '—'} "
            f"(ID: {me.id})"
        )
        return True

    async def _setup_handlers(self) -> None:
        assert self.client is not None

        @self.client.on(events.NewMessage(incoming=True))
        async def message_handler(event):
            try:
                me = await self.client.get_me()
                if event.sender_id == me.id:
                    return

                sender = await event.get_sender()
                if not sender or getattr(sender, "bot", False):
                    return

                if self.dry_run:
                    preview = (event.raw_text or "")[:60]
                    logger.info(
                        "DRY-RUN mesaj",
                        chat=event.chat_id,
                        sender=getattr(sender, "first_name", "?"),
                        text=preview,
                    )
                    return

                if event.is_private and isinstance(sender, User):
                    await handle_baron_dm(self.client, sender, event.raw_text or "")
                elif event.is_group:
                    await handle_baron_group_message(
                        self.client, event, self.bot_username
                    )
            except FloodWaitError as exc:
                logger.warning("FloodWait", seconds=exc.seconds)
                await asyncio.sleep(exc.seconds)
            except Exception as exc:
                logger.error("Handler hatası", error=str(exc))

        logger.info("Event handler'lar kuruldu")

    async def _init_services(self) -> None:
        try:
            from core.database_manager import database_manager

            await database_manager.initialize()
            logger.info("Database manager hazır")
        except Exception as exc:
            logger.warning("Database manager atlandı", error=str(exc))

    async def start(self) -> None:
        cleanup_session_locks()
        session_report = validate_session_file(f"{self.session_stem}.session")
        logger.info("Session kontrol", **session_report)

        if not await self.connect(force_login=False):
            raise RuntimeError("Baron bağlantısı kurulamadı")

        await self._setup_handlers()
        await self._init_services()

        stats = get_baron_stats()
        print("\n📊 Baron başlangıç özeti")
        print(f"   Reply mode : {stats['reply_mode']}")
        print(f"   GPT        : {'aktif' if stats['gpt_available'] else 'kapalı'}")
        print(f"   Dry-run    : {self.dry_run}")
        print(f"   Session    : {session_report['path']} ({session_report['size_kb']} KB)")

        self.is_running = True
        print(f"\n🔥 {self.display_name} dinlemede — Ctrl+C ile durdur.\n")
        await self.client.run_until_disconnected()

    async def login(self) -> None:
        cleanup_session_locks()
        if not await self.connect(force_login=True):
            raise RuntimeError("Baron login başarısız")
        print("✅ Login tamamlandı, session kaydedildi.")
        await self.cleanup()

    async def cleanup(self) -> None:
        self.is_running = False
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram bağlantısı kapatıldı")

    def status_dict(self) -> Dict[str, Any]:
        uptime = None
        if self.started_at:
            uptime = int((datetime.now() - self.started_at).total_seconds())
        return {
            "bot": BOT_KEY,
            "display_name": self.display_name,
            "version": VERSION,
            "running": self.is_running,
            "phone": self.phone,
            "session": f"{self.session_stem}.session",
            "username": self.bot_username,
            "uptime_seconds": uptime,
            "me": self.me_info,
            "handler_stats": get_baron_stats(),
            "flags": {
                "dry_run": self.dry_run,
                "no_gpt": self.no_gpt,
                "gpt_blend": os.getenv("BARON_AI_BLEND", "true"),
            },
        }


def _print_banner() -> None:
    print(
        f"""
👑══════════════════════════════════════════════════════👑
   BARON BOT LAUNCHER v{VERSION}
   GavatCore — Tek Kullanıcı Final CLI
👑══════════════════════════════════════════════════════👑
"""
    )


def _build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--onay-kodu", dest="onay_kodu", help="Telegram SMS onay kodu")
    common.add_argument(
        "--onay-sifre",
        dest="onay_sifresi",
        help="Telegram 2FA onay şifresi",
    )
    common.add_argument(
        "--dry-run",
        action="store_true",
        help="Mesajları işleme, sadece logla",
    )
    common.add_argument(
        "--no-gpt",
        action="store_true",
        help="GPT ve AI blending devre dışı",
    )

    parser = argparse.ArgumentParser(
        prog="baron_bot_launcher",
        description="Baron — GavatCore final tek-kullanıcı bot launcher",
        parents=[common],
    )

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("start", help="Bot'u başlat ve dinle", parents=[common])
    sub.add_parser("login", help="Session yenile (onay kodu/şifre)", parents=[common])
    sub.add_parser("status", help="Çalışma durumu (JSON)")
    sub.add_parser("stats", help="Handler istatistikleri (JSON)")
    sub.add_parser("info", help="Persona ve session bilgisi")
    sub.add_parser("session-check", help="Session dosyası doğrulama")
    sub.add_parser("cleanup-sessions", help="Session lock dosyalarını temizle")

    test_gpt = sub.add_parser("test-gpt", help="GPT yanıt testi")
    test_gpt.add_argument("message", help="Test mesajı")

    return parser


async def _async_main(args: argparse.Namespace) -> int:
    launcher = BaronBotLauncher(
        onay_kodu=getattr(args, "onay_kodu", None),
        onay_sifresi=getattr(args, "onay_sifresi", None),
        dry_run=getattr(args, "dry_run", False),
        no_gpt=getattr(args, "no_gpt", False),
    )

    command = args.command or "help"

    if command == "help":
        _print_banner()
        print(
            """Komutlar:
  start              Bot'u başlat
  login              Onay kodu/şifre ile session oluştur
  status             Durum (JSON)
  stats              Handler istatistikleri
  info               Persona + session özeti
  session-check      Session dosyası kontrolü
  cleanup-sessions   Lock dosyalarını temizle
  test-gpt <mesaj>   GPT yanıt testi

Ortam değişkenleri:
  TELEGRAM_ONAY_KODU / TELEGRAM_ONAY_SIFRESI
  OPENAI_API_KEY (GPT için)
  BARON_AI_BLEND=true|false
"""
        )
        return 0

    if command == "cleanup-sessions":
        count = cleanup_session_locks()
        print(json.dumps({"removed_lock_files": count}, ensure_ascii=False, indent=2))
        return 0

    if command == "session-check":
        report = validate_session_file(f"{launcher.session_stem}.session")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if command == "info":
        persona = _load_persona()
        report = validate_session_file(f"{launcher.session_stem}.session")
        print(
            json.dumps(
                {
                    "persona_file": PERSONA_FILE,
                    "persona": persona,
                    "session": report,
                    "character_config": "character_engine/character_config/baron.json",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if command == "stats":
        print(json.dumps(get_baron_stats(), ensure_ascii=False, indent=2))
        return 0

    if command == "status":
        print(json.dumps(launcher.status_dict(), ensure_ascii=False, indent=2))
        return 0

    if command == "test-gpt":
        result = await test_baron_gpt(args.message)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if command == "login":
        _print_banner()
        await launcher.login()
        return 0

    if command == "start":
        _print_banner()

        def _signal_handler(sig, frame):
            logger.info("Shutdown sinyali", signal=sig)
            asyncio.create_task(launcher.cleanup())

        signal.signal(signal.SIGINT, _signal_handler)
        signal.signal(signal.SIGTERM, _signal_handler)

        try:
            await launcher.start()
        except KeyboardInterrupt:
            print("\n⏹️ Durduruldu")
        finally:
            await launcher.cleanup()
        return 0

    print(f"Bilinmeyen komut: {command}")
    return 1


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    raise SystemExit(asyncio.run(_async_main(args)))


if __name__ == "__main__":
    main()
