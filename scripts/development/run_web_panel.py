#!/usr/bin/env python3
"""Run the panel with an isolated local SQLite database, never live sessions.

Build first: npm --prefix gavatcore-api/frontend run build
Run: .venv/bin/python scripts/development/run_web_panel.py
"""
import argparse
import asyncio
import os
from pathlib import Path
import secrets
import sys

ROOT = Path(__file__).resolve().parents[2]


def configure(data_dir: Path):
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "sessions").mkdir(exist_ok=True)
    # Explicitly ignore repository .env and live credentials in local preview.
    os.environ.update({
        "GAVATCORE_ENV_FILE": "", "ENVIRONMENT": "development", "DEBUG": "false",
        "DATABASE_URL": f"sqlite+aiosqlite:///{data_dir / 'panel.sqlite3'}",
        "SESSION_STORAGE_PATH": str(data_dir / "sessions"), "PANEL_LOCAL_PREVIEW": "true",
        "JWT_SECRET_KEY": secrets.token_urlsafe(48), "SECRET_KEY": secrets.token_urlsafe(48),
        "TELEGRAM_BOT_TOKEN": "", "TELEGRAM_API_ID": "", "TELEGRAM_API_HASH": "",
        "OPENAI_API_KEY": "", "STRIPE_SECRET_KEY": "sk_test_local_preview_disabled",
    })
    sys.path[:0] = [str(ROOT), str(ROOT / "gavatcore-api")]


async def seed():
    from sqlalchemy import select
    from app.database.connection import create_tables, async_session_factory, engine
    from app.models.user import User
    from app.models.bot_instance import BotInstance
    from app.services.auth_service import AuthService
    await create_tables()
    async with async_session_factory() as db:
        user = await db.scalar(select(User).where(User.username == "panel_local"))
        if user is None:
            user = User(username="panel_local", first_name="Yerel çalışma alanı",
                        password_hash=AuthService().hash_password("local-panel-only"))
            db.add(user)
            await db.flush()
            for name, persona in [("Lara · Yerel", "yayincilara"), ("Geisha · Yerel", "xxxgeisha"), ("Baba · Yerel", "gawatbaba")]:
                db.add(BotInstance(user_id=user.id, bot_name=name, personality=persona,
                                   session_status="pending", reply_mode="manual",
                                   config='{"local_preview": true}'))
            await db.commit()
    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=18082)
    parser.add_argument("--data-dir", type=Path, default=ROOT / ".local" / "web-panel")
    args = parser.parse_args()
    if not (ROOT / "gavatcore-api/frontend/dist/index.html").is_file():
        parser.error("Run npm --prefix gavatcore-api/frontend run build first")
    configure(args.data_dir.resolve())
    asyncio.run(seed())
    import uvicorn
    print(f"Panel: http://127.0.0.1:{args.port}/panel/\nLocal preview: panel_local / local-panel-only", flush=True)
    uvicorn.run("app.main:app", host="127.0.0.1", port=args.port)
