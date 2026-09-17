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
import fcntl
import getpass
import glob
import json
import os
import signal
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Direct `python3 launchers/baron_bot_launcher.py` calls should use the
# repository environment where Telethon, structlog and the other dependencies
# are installed. Re-exec before importing third-party packages.
_BOOTSTRAP_ROOT = Path(__file__).resolve().parent.parent
_VENV_PYTHON = _BOOTSTRAP_ROOT / ".venv/bin/python"
if (
    _VENV_PYTHON.exists()
    and Path(sys.executable).resolve() != _VENV_PYTHON.resolve()
    and os.environ.get("BARON_VENV_BOOTSTRAPPED") != "1"
):
    os.environ["BARON_VENV_BOOTSTRAPPED"] = "1"
    os.execv(
        str(_VENV_PYTHON),
        [str(_VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]],
    )

import structlog
from telethon import TelegramClient, events
from telethon.errors import (
    FloodWaitError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)
from telethon.tl.types import User
from telethon.tl.types.auth import (
    SentCodeTypeApp,
    SentCodeTypeCall,
    SentCodeTypeFragmentSms,
    SentCodeTypeSms,
)
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest

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
VERSION = "1.1.0"


def _is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def _prompt(text: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{text}{suffix}: ").strip()
    return value or default


def _prompt_yes_no(text: str, default: bool = True) -> bool:
    hint = "E/h" if default else "e/H"
    answer = input(f"{text} ({hint}): ").strip().lower()
    if not answer:
        return default
    return answer in ("e", "evet", "y", "yes")


def _describe_sent_code(sent: Any) -> str:
    code_type = sent.type
    length = getattr(code_type, "length", 5)
    if isinstance(code_type, SentCodeTypeApp):
        return (
            "📲 Kod SMS'e DEĞİL — Telegram uygulamasına gitti!\n"
            "   1) Telefonda Telegram'ı aç\n"
            "   2) Sohbetler listesinde 'Telegram' servis mesajını bul\n"
            "   3) Oradaki giriş kodunu kullan (genelde 5 hane)\n"
            f"   Kod uzunluğu: {length}"
        )
    if isinstance(code_type, SentCodeTypeSms):
        return (
            f"📩 Kod SMS olarak {sent.phone_code_hash and 'gönderildi' or 'gönderiliyor'}.\n"
            f"   SMS gelmezse birkaç dakika bekle veya 'r' ile yeniden gönder.\n"
            f"   Kod uzunluğu: {length}"
        )
    if isinstance(code_type, SentCodeTypeCall):
        return f"📞 Kod sesli arama ile okunacak. Kod uzunluğu: {length}"
    if isinstance(code_type, SentCodeTypeFragmentSms):
        return f"📩 Kod parçalı SMS ile gönderildi. Kod uzunluğu: {length}"
    return f"🔑 Doğrulama kodu gönderildi. Tip: {type(code_type).__name__}"


def _resolve_onay_kodu(
    cli_value: Optional[str] = None,
    *,
    interactive: bool = False,
    ignore_env: bool = False,
) -> Optional[str]:
    if cli_value:
        return cli_value.strip()
    if ignore_env or interactive:
        return None
    for key in ("TELEGRAM_ONAY_KODU", "ONAY_KODU", "TELEGRAM_LOGIN_CODE"):
        value = os.getenv(key)
        if value and value.strip():
            return value.strip()
    return None


def _resolve_onay_sifresi(
    cli_value: Optional[str] = None,
    *,
    interactive: bool = False,
    ignore_env: bool = False,
) -> Optional[str]:
    if cli_value:
        return cli_value.strip()
    if ignore_env or interactive:
        return None
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


def reset_session_files(session_stem: str) -> list[str]:
    removed: list[str] = []
    for suffix in ("", "-journal", "-wal", "-shm"):
        path = f"{session_stem}.session{suffix}"
        if os.path.exists(path):
            os.remove(path)
            removed.append(path)
    return removed


class BaronBotLauncher:
    def __init__(
        self,
        onay_kodu: Optional[str] = None,
        onay_sifresi: Optional[str] = None,
        dry_run: bool = False,
        no_gpt: bool = False,
        interactive: bool = False,
        ignore_env: bool = False,
        reset_session: bool = False,
    ):
        self.persona = _load_persona()
        self.display_name = self.persona.get("display_name", "Baron")
        self.phone = self.persona.get("phone", DEFAULT_PHONE)
        self.session_stem = _session_stem(self.phone)
        self.onay_kodu = onay_kodu
        self.onay_sifresi = onay_sifresi
        self.dry_run = dry_run
        self.no_gpt = no_gpt
        self.interactive = interactive or _is_interactive()
        self.ignore_env = ignore_env
        self.reset_session = reset_session

        self.client: Optional[TelegramClient] = None
        self.bot_username = self.persona.get("username", BOT_KEY)
        self.is_running = False
        self.started_at: Optional[datetime] = None
        self.me_info: Dict[str, Any] = {}
        self._sent_code_info: Optional[Any] = None
        self._campaign_task = None
        self._campaign_store = None
        self._adaptive_engine = None
        self._live_lock_handle = None

    def _acquire_live_lock(self) -> None:
        lock_path = ROOT / "data/baron_live.lock"
        lock_path.parent.mkdir(exist_ok=True)
        handle = lock_path.open("a+")
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            handle.close()
            raise RuntimeError(
                "Başka bir Baron canlı süreci çalışıyor; önce baron_live.sh stop kullan."
            ) from None
        handle.seek(0)
        handle.truncate()
        handle.write(str(os.getpid()))
        handle.flush()
        self._live_lock_handle = handle

    def _ask_onay_kodu(self) -> str:
        preset = _resolve_onay_kodu(
            self.onay_kodu,
            interactive=self.interactive,
            ignore_env=self.ignore_env,
        )
        if preset:
            print("🔑 Onay kodu argümandan alındı.")
            return preset

        print("\n" + "─" * 52)
        if self._sent_code_info:
            print(_describe_sent_code(self._sent_code_info))
        else:
            print(
                "🔑 Telegram onay kodu gerekli.\n"
                "   Not: Kod çoğu zaman SMS değil, Telegram uygulamasına gelir!"
            )
        print("─" * 52)
        print("   r = kodu yeniden gönder | q = iptal")
        while True:
            kod = input("\n🔑 Onay kodunu girin: ").strip()
            if kod.lower() == "q":
                raise KeyboardInterrupt("Giriş iptal edildi")
            if kod.lower() == "r":
                return "__RESEND__"
            if kod and kod.isdigit():
                return kod
            print("❌ Geçersiz kod. Sadece rakam girin (ör. 12345) veya r/q.")

    def _ask_onay_sifresi(self) -> str:
        preset = _resolve_onay_sifresi(
            self.onay_sifresi,
            interactive=self.interactive,
            ignore_env=self.ignore_env,
        )
        if preset:
            print("🔒 Onay şifresi argümandan alındı.")
            return preset
        print("\n🔐 Bu hesapta 2FA (Cloud Password) aktif.")
        return getpass.getpass("🔒 Telegram onay şifresini girin: ")

    async def _send_login_code(self) -> Any:
        assert self.client is not None
        print(f"\n📨 Doğrulama kodu isteniyor: {self.phone}")
        try:
            sent = await self.client.send_code_request(self.phone)
        except PhoneNumberInvalidError:
            raise RuntimeError(f"Geçersiz telefon numarası: {self.phone}") from None
        except FloodWaitError as exc:
            raise RuntimeError(
                f"Telegram flood limiti — {exc.seconds} saniye bekleyin."
            ) from exc

        self._sent_code_info = sent
        print(_describe_sent_code(sent))
        timeout = getattr(sent.type, "timeout", None)
        if timeout:
            print(f"⏱️  Yeni kod isteme süresi: ~{timeout} saniye")
        return sent

    async def _interactive_authorize(self) -> None:
        assert self.client is not None

        if self.interactive:
            print(f"\n📱 Baron hesabı: {self.phone}")
            if not _prompt_yes_no("Bu numara doğru mu?", default=True):
                self.phone = _prompt("Telefon numarası (+90...)", self.phone)
                self.session_stem = _session_stem(self.phone)

        max_rounds = 5
        for round_no in range(1, max_rounds + 1):
            await self._send_login_code()

            while True:
                code = self._ask_onay_kodu()
                if code == "__RESEND__":
                    print("🔄 Kod yeniden gönderiliyor...")
                    await self._send_login_code()
                    continue

                try:
                    await self.client.sign_in(self.phone, code)
                    print("✅ Onay kodu kabul edildi.")
                    return
                except SessionPasswordNeededError:
                    password = self._ask_onay_sifresi()
                    await self.client.sign_in(password=password)
                    print("✅ 2FA onay şifresi kabul edildi.")
                    return
                except PhoneCodeInvalidError:
                    print(f"❌ Yanlış kod (deneme {round_no}/{max_rounds}).")
                    break
                except PhoneCodeExpiredError:
                    print("❌ Kod süresi doldu, yeni kod gönderiliyor...")
                    break
                except FloodWaitError as exc:
                    print(f"⏳ {exc.seconds} saniye beklemeniz gerekiyor...")
                    await asyncio.sleep(exc.seconds)
                    break

        raise RuntimeError("Giriş başarısız — kod doğrulanamadı.")

    async def connect(self, force_login: bool = False) -> bool:
        os.makedirs("sessions", exist_ok=True)
        if self.no_gpt:
            os.environ["BARON_AI_BLEND"] = "false"

        if self.reset_session:
            removed = reset_session_files(self.session_stem)
            if removed:
                print("🗑️  Eski session silindi:")
                for path in removed:
                    print(f"   - {path}")

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
            session_path = f"{self.session_stem}.session"
            if (
                not force_login
                and os.path.exists(session_path)
                and self.interactive
                and not self.reset_session
            ):
                print("⚠️  Session geçersiz — giriş gerekli.")
                if _prompt_yes_no("Bozuk session silinsin mi? (kod gelmiyorsa Evet)", True):
                    self.reset_session = True
                    # Telethon keeps SQLite open after connect. Close it before deleting
                    # the database, then build a fresh client around the new session.
                    await self.client.disconnect()
                    self.client = None
                    removed = reset_session_files(self.session_stem)
                    if removed:
                        print("🗑️  Eski session silindi:")
                        for path in removed:
                            print(f"   - {path}")
                    self.client = TelegramClient(
                        self.session_stem,
                        TELEGRAM_API_ID,
                        TELEGRAM_API_HASH,
                        device_model=f"{self.display_name} Bot",
                        system_version="GAVATCore v2.1",
                        app_version=f"BaronLauncher/{VERSION}",
                    )
                    await self.client.connect()

            print("🔐 Telegram giriş akışı başlıyor...")
            await self._interactive_authorize()
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
                    await handle_baron_dm(
                        self.client,
                        sender,
                        event.raw_text or "",
                        message_id=event.id,
                    )
                elif event.is_group:
                    if self._adaptive_engine and event.reply_to_msg_id:
                        self._adaptive_engine.feedback(event.chat_id, event.id, event.reply_to_msg_id, event.raw_text or "")
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

    async def _ensure_ai_profile(self, campaign_config: Dict[str, Any]) -> None:
        assert self.client is not None
        about = campaign_config["profile_about"]
        full = await self.client(GetFullUserRequest("me"))
        current = getattr(full.full_user, "about", None) or ""
        if current != about:
            await self.client(UpdateProfileRequest(about=about))
            logger.info("Baron profil açıklaması güncellendi")
        else:
            logger.info("Baron profil açıklaması doğrulandı")

    async def start(self) -> None:
        from services.telegram.baron_campaign import Store, broadcast, load_config

        self._acquire_live_lock()
        campaign_config = load_config()
        cleanup_session_locks()
        session_report = validate_session_file(f"{self.session_stem}.session")
        logger.info("Session kontrol", **session_report)

        if not await self.connect(force_login=False):
            raise RuntimeError("Baron bağlantısı kurulamadı")

        await self._ensure_ai_profile(campaign_config)
        self._campaign_store = Store()
        if campaign_config.get("adaptive", {}).get("enabled"):
            from services.telegram.baron_adaptive import AdaptiveEngine
            self._adaptive_engine = AdaptiveEngine(self._campaign_store, campaign_config["adaptive"])
        await self._setup_handlers()
        await self._init_services()
        from services.telegram.baron_bot_handler import generate_baron_group_post
        async def generate(context, topic):
            if self.no_gpt:
                return None
            return await generate_baron_group_post(context, topic)
        self._campaign_task = asyncio.create_task(
            broadcast(self.client, campaign_config, self._campaign_store, self.dry_run,
                      engine=self._adaptive_engine, generate=generate)
        )

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
        if not await self.connect(force_login=False):
            raise RuntimeError("Baron login başarısız")
        print("✅ Login tamamlandı, session kaydedildi.")
        await self.cleanup()

    async def cleanup(self) -> None:
        self.is_running = False
        if self._campaign_task:
            self._campaign_task.cancel()
            try:
                await self._campaign_task
            except asyncio.CancelledError:
                pass
        if self._campaign_store:
            self._campaign_store.db.close()
            self._campaign_store = None
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram bağlantısı kapatıldı")
        if self._live_lock_handle:
            fcntl.flock(self._live_lock_handle.fileno(), fcntl.LOCK_UN)
            self._live_lock_handle.close()
            self._live_lock_handle = None

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
    common.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Terminalde sorarak giriş yap (env değerlerini yok say)",
    )
    common.add_argument(
        "--ignore-env",
        action="store_true",
        help="TELEGRAM_ONAY_* env değişkenlerini kullanma",
    )
    common.add_argument(
        "--reset-session",
        action="store_true",
        help="Girişten önce eski session dosyasını sil",
    )

    parser = argparse.ArgumentParser(
        prog="baron_bot_launcher",
        description="Baron — GavatCore final tek-kullanıcı bot launcher",
        parents=[common],
    )

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("start", help="Bot'u başlat ve dinle", parents=[common])
    sub.add_parser("login", help="Session yenile (onay kodu/şifre)", parents=[common])
    sub.add_parser("menu", help="Interaktif CLI menüsü", parents=[common])
    sub.add_parser("status", help="Çalışma durumu (JSON)")
    sub.add_parser("stats", help="Handler istatistikleri (JSON)")
    sub.add_parser("info", help="Persona ve session bilgisi")
    sub.add_parser("session-check", help="Session dosyası doğrulama")
    sub.add_parser("cleanup-sessions", help="Session lock dosyalarını temizle")
    sub.add_parser("scan-groups", help="Üye olunan grupları tara; gönderim yapmadan aday raporu oluştur")
    activate = sub.add_parser("activate-candidates", help="Son keşif raporundaki adayları kampanyaya al")
    activate.add_argument("--min-score", type=float, default=None)
    sub.add_parser("campaign-disable", help="Yeni kampanya gönderimlerini kapat")
    sub.add_parser("campaign-report", help="Kampanya ve etkileşim raporunu JSON göster")
    sub.add_parser("campaign-alive", help=argparse.SUPPRESS)
    preview = sub.add_parser("preview-group", help="Göndermeden bağlama uygun mesaj taslağı oluştur")
    preview.add_argument("chat_id", type=int)
    preview.add_argument("--source", choices=("next", "template", "gpt"), default="next")

    test_gpt = sub.add_parser("test-gpt", help="GPT yanıt testi")
    test_gpt.add_argument("message", help="Test mesajı")

    return parser


async def _run_interactive_menu(launcher: BaronBotLauncher) -> int:
    _print_banner()
    while True:
        print(
            """
📋 Baron CLI Menüsü
──────────────────
  1) Bot'u başlat
  2) Giriş yap (onay kodu / şifre)
  3) Session sil + yeniden giriş
  4) Session bilgisi
  5) GPT test
  0) Çıkış
"""
        )
        choice = input("👉 Seçiminiz: ").strip()
        if choice == "0":
            return 0
        if choice == "1":
            try:
                await launcher.start()
            except KeyboardInterrupt:
                print("\n⏹️ Durduruldu")
            finally:
                await launcher.cleanup()
            return 0
        if choice == "2":
            launcher.reset_session = False
            await launcher.login()
            return 0
        if choice == "3":
            launcher.reset_session = True
            await launcher.login()
            return 0
        if choice == "4":
            report = validate_session_file(f"{launcher.session_stem}.session")
            print(json.dumps(report, ensure_ascii=False, indent=2))
        elif choice == "5":
            msg = _prompt("Test mesajı", "Merhaba Baron")
            result = await test_baron_gpt(msg)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("❌ Geçersiz seçim")


async def _async_main(args: argparse.Namespace) -> int:
    interactive = getattr(args, "interactive", False) or _is_interactive()
    ignore_env = getattr(args, "ignore_env", False) or getattr(args, "interactive", False)
    launcher = BaronBotLauncher(
        onay_kodu=getattr(args, "onay_kodu", None),
        onay_sifresi=getattr(args, "onay_sifresi", None),
        dry_run=getattr(args, "dry_run", False),
        no_gpt=getattr(args, "no_gpt", False),
        interactive=interactive,
        ignore_env=ignore_env,
        reset_session=getattr(args, "reset_session", False),
    )

    command = args.command
    if command is None and interactive:
        return await _run_interactive_menu(launcher)
    if command is None:
        command = "help"

    if command == "help":
        _print_banner()
        print(
            """Komutlar:
  start              Bot'u başlat
  login              Onay kodu/şifre ile session oluştur
  menu               Interaktif menü (terminal)
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

İpucu — kod gelmiyorsa:
  python3 launchers/baron_bot_launcher.py login --reset-session -i
  Kod SMS değil; Telegram uygulamasındaki 'Telegram' mesajına bak.
"""
        )
        return 0

    if command == "menu":
        return await _run_interactive_menu(launcher)

    if command == "cleanup-sessions":
        count = cleanup_session_locks()
        print(json.dumps({"removed_lock_files": count}, ensure_ascii=False, indent=2))
        return 0

    if command == "session-check":
        report = validate_session_file(f"{launcher.session_stem}.session")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    if command in ("activate-candidates", "campaign-disable", "campaign-report", "campaign-alive"):
        from services.telegram.baron_adaptive import AdaptiveEngine
        from services.telegram.baron_campaign import CONFIG, Store, campaign_report, load_config

        config = load_config()
        if command == "activate-candidates":
            report_path = ROOT / "reports/baron_group_discovery.json"
            if not report_path.exists():
                print("Keşif raporu yok. Önce scan-groups çalıştır.")
                return 1
            discovery = json.loads(report_path.read_text(encoding="utf-8"))
            if not discovery.get("complete"):
                print("Keşif raporu tamamlanmamış; kampanya açılmadı.")
                return 1
            threshold = args.min_score if args.min_score is not None else config["adaptive"]["candidate_threshold"]
            if not 0 <= threshold <= 1:
                print("min-score 0–1 arasında olmalı.")
                return 1
            groups = [
                {
                    "id": item["id"],
                    "title": item["title"],
                    "detection_score": item["score"],
                    "permission_confirmed": True,
                }
                for item in discovery["groups"]
                if item.get("candidate") and item.get("score", 0) >= threshold
            ]
            if not groups:
                print("Eşiği geçen aday grup yok; kampanya açılmadı.")
                return 1
            config["broadcast"]["groups"] = groups
            config["broadcast"]["enabled"] = True
            temp_path = CONFIG.with_suffix(".json.tmp")
            temp_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            os.replace(temp_path, CONFIG)
            print(json.dumps({"enabled": True, "groups": len(groups), "min_score": threshold}, ensure_ascii=False, indent=2))
            return 0
        if command == "campaign-disable":
            config["broadcast"]["enabled"] = False
            temp_path = CONFIG.with_suffix(".json.tmp")
            temp_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            os.replace(temp_path, CONFIG)
            print(json.dumps({"enabled": False}, ensure_ascii=False))
            return 0
        store = Store()
        try:
            AdaptiveEngine(store, config["adaptive"])
            report = campaign_report(config, store)
            if command == "campaign-alive":
                return 0 if report["active"] else 1
            print(json.dumps(report, ensure_ascii=False, indent=2))
        finally:
            store.db.close()
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

    if command in ("scan-groups", "preview-group"):
        from services.telegram.baron_campaign import Store, load_config
        from services.telegram.baron_adaptive import AdaptiveEngine, recent_context, scan_groups
        from services.telegram.baron_bot_handler import generate_baron_group_post
        settings = load_config()["adaptive"]
        # A read-only command must not request a login code or install message handlers.
        client = TelegramClient(launcher.session_stem, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                print("Mevcut Baron oturumu yetkili değil. Önce login komutuyla giriş yap.")
                return 1
            if command == "scan-groups":
                report = await scan_groups(client, settings, lambda n: print(f"Taranan grup: {n}", flush=True))
                report_path = ROOT / "reports/baron_group_discovery.json"
                report_path.parent.mkdir(exist_ok=True)
                report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(json.dumps({"report": str(report_path), "complete": report["complete"], "groups": len(report["groups"]), "candidates": sum(g["candidate"] for g in report["groups"])}, ensure_ascii=False))
                return 0 if report["complete"] else 1
            store = Store()
            # Preview uses a private DB copy so counters, feedback, and retention stay unchanged.
            preview_store = Store(":memory:")
            try:
                store.db.backup(preview_store.db)
                engine = AdaptiveEngine(preview_store, settings)
                if args.source != "next":
                    with preview_store.db:
                        preview_store.db.execute("INSERT OR REPLACE INTO adaptive_counts VALUES(?,?,?)", (args.chat_id, int(args.source == "gpt"), 0))
                entity = await client.get_entity(args.chat_id)
                if not (getattr(entity, "megagroup", False) or entity.__class__.__name__ == "Chat"):
                    raise ValueError("Önizleme hedefi grup olmalı")
                context = await recent_context(client, entity, settings)
                selection = await engine.choose(args.chat_id, context, generate_baron_group_post)
                print(json.dumps(vars(selection) if selection else {"skipped": True, "reason": "Bağlam veya GPT çıktısı uygun değil"}, ensure_ascii=False, indent=2))
            finally:
                store.db.close()
                preview_store.db.close()
            return 0
        finally:
            await client.disconnect()

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
