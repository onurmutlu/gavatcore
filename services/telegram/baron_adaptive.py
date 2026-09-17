"""Group discovery and a balanced, feedback-driven message selector.

Raw chat history stays in memory. Persistent learning is per group/template,
not a profile of individual people. Discovery never grants posting permission.
"""
import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOPICS = {
    "introduction": ("tanis", "arkadas", "arayis", "sohbet", "merhaba", "selam"),
    "music": ("muzik", "sarki", "konser", "album", "melodi"),
    "film": ("film", "dizi", "sinema", "izled", "spoiler"),
    "food": ("yemek", "kahve", "cay", "kahvalti", "tatli"),
    "hobby": ("hobi", "kitap", "oyun", "spor", "fotograf"),
    "travel": ("gezi", "tatil", "seyahat", "yolculuk", "deniz"),
    "daily": ("gun", "aksam", "sabah", "hafta", "is", "rutin"),
}


def normalize(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower().replace("ı", "i")) if not unicodedata.combining(c))


def matches(text, terms):
    words = re.findall(r"\w+", normalize(text))
    return any(any(word.startswith(term) if len(term) > 3 else word == term for word in words) for term in terms)


def redact(text):
    text = re.sub(r"https?://\S+|t\.me/\S+|@\w+|[\w.+-]+@[\w.-]+\.[A-Za-z]+", "[bağlantı/hesap]", text)
    text = re.sub(r"\+?\d[\d ()-]{7,}\d", "[numara]", text)
    return text[:350]


def topic_scores(messages):
    scores = {topic: sum(matches(text, terms) for text in messages) for topic, terms in TOPICS.items()}
    return {key: value for key, value in scores.items() if value} or {"general": 1}


def classify_group(title, messages, threshold=0.6):
    unrelated_search = matches(title, ("is", "eleman", "kariyer", "emlak", "kiralik", "satilik", "ticaret"))
    explicit = matches(title, ("arayis", "tanisma", "arkadaslik", "sosyalles"))
    social_title = matches(title, ("sohbet", "muhabbet"))
    social_count = sum(matches(m, TOPICS["introduction"]) for m in messages)
    ratio = social_count / max(len(messages), 1)
    score = min(1.0, (0.7 if explicit else 0.35 if social_title else 0) + min(ratio * 0.6, 0.3))
    if unrelated_search:
        score = 0.0
    return {"candidate": score >= threshold, "score": round(score, 3),
            "reasons": {"explicit_social_title": explicit, "social_title": social_title, "unrelated_search": unrelated_search, "social_message_ratio": round(ratio, 3)},
            "topics": topic_scores(messages), "sample_size": len(messages)}


async def recent_context(client, entity, settings):
    cutoff = time.time() - settings["context_max_age_hours"] * 3600
    texts = []
    async for message in client.iter_messages(entity, limit=settings["context_limit"]):
        date = getattr(message, "date", None)
        if date and date.timestamp() < cutoff:
            continue
        if getattr(message, "out", False) or getattr(message, "action", None):
            continue
        raw = getattr(message, "raw_text", "") or ""
        if raw.strip() and not raw.startswith("/"):
            texts.append(redact(raw))
    return list(reversed(texts))


def load_templates(settings):
    path = (ROOT / settings["templates_file"]).resolve()
    items = json.loads(path.read_text(encoding="utf-8"))["messages"]
    ids = [item["id"] for item in items]
    if not 40 <= len(items) <= 50 or len(ids) != len(set(ids)):
        raise ValueError("JSON seti benzersiz ID'li 40–50 mesaj içermeli")
    for item in items:
        if not item.get("topics") or not isinstance(item["text"], str) or not 1 <= len(item["text"]) <= 600:
            raise ValueError("Şablonun konu etiketi ve 1–600 karakter metni gerekli")
    return items


def validate_settings(settings):
    if not 1 <= settings["context_limit"] <= 100 or not 1 <= settings["context_max_age_hours"] <= 48:
        raise ValueError("Bağlam 1–100 mesaj ve 1–48 saat ile sınırlı olmalı")
    if not 1 <= settings["min_context_messages"] <= settings["context_limit"]:
        raise ValueError("Asgari bağlam sayısı geçersiz")
    if not 0 <= settings["candidate_threshold"] <= 1:
        raise ValueError("Aday eşiği 0–1 arasında olmalı")
    if not 1 <= settings["feedback_window_hours"] <= settings["retention_days"] * 24 or not 1 <= settings["retention_days"] <= 90:
        raise ValueError("Geri bildirim veya saklama süresi geçersiz")
    load_templates(settings)


@dataclass
class Selection:
    source: str
    text: str
    template_id: str = ""
    topic: str = "general"


class AdaptiveEngine:
    def __init__(self, store, settings):
        self.store, self.settings = store, settings
        self.templates = load_templates(settings)
        store.db.executescript("""
            CREATE TABLE IF NOT EXISTS adaptive_counts(chat INTEGER PRIMARY KEY, template INTEGER DEFAULT 0, gpt INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS adaptive_posts(
                chat INTEGER, message INTEGER, source TEXT, template_id TEXT, topic TEXT,
                fingerprint TEXT, sent REAL, replies INTEGER DEFAULT 0, negative INTEGER DEFAULT 0,
                PRIMARY KEY(chat,message));
            CREATE TABLE IF NOT EXISTS adaptive_feedback(chat INTEGER, message INTEGER, post INTEGER,
                PRIMARY KEY(chat,message));
        """)

    def prune(self):
        with self.store.db:
            self.store.db.execute("DELETE FROM adaptive_posts WHERE sent<?", (time.time() - self.settings["retention_days"] * 86400,))
            self.store.db.execute("DELETE FROM adaptive_feedback WHERE NOT EXISTS (SELECT 1 FROM adaptive_posts p WHERE p.chat=adaptive_feedback.chat AND p.message=adaptive_feedback.post)")

    def next_source(self, chat):
        row = self.store.db.execute("SELECT * FROM adaptive_counts WHERE chat=?", (chat,)).fetchone()
        totals = self.store.db.execute(
            "SELECT COALESCE(SUM(template),0) template, COALESCE(SUM(gpt),0) gpt "
            "FROM adaptive_counts"
        ).fetchone()
        if abs(totals["template"] - totals["gpt"]) > 1:
            return "template" if totals["template"] < totals["gpt"] else "gpt"
        if not row:
            return "template" if totals["template"] <= totals["gpt"] else "gpt"
        return "template" if not row or row["template"] <= row["gpt"] else "gpt"

    async def choose(self, chat, context, generate):
        self.prune()
        if len(context) < self.settings["min_context_messages"]:
            return None
        topics = topic_scores(context)
        topic = max(topics, key=topics.get)
        source = self.next_source(chat)
        recent = self.store.db.execute("SELECT fingerprint,template_id FROM adaptive_posts WHERE chat=? ORDER BY sent DESC LIMIT 12", (chat,)).fetchall()
        if source == "gpt":
            text = await generate(context, topic)
            if not isinstance(text, str) or not text.strip() or len(text) > 600:
                return None
            text = text.strip()
            if re.search(r"https?://|t\.me/|@\w+", text):
                return None
            fingerprint = hashlib.sha256(normalize(text).encode()).hexdigest()
            if fingerprint in {row["fingerprint"] for row in recent}:
                return None
            return Selection("gpt", text, topic=topic)
        excluded = {row["template_id"] for row in recent}
        candidates = [t for t in self.templates if t["id"] not in excluded]
        stats = self.store.db.execute("SELECT template_id,COUNT(*) n,SUM(MIN(replies,3)-2*MIN(negative,3)) reward FROM adaptive_posts WHERE chat=? AND source='template' GROUP BY template_id", (chat,)).fetchall()
        stats = {row["template_id"]: row for row in stats}
        total = sum(row["n"] for row in stats.values())
        def score(item):
            row = stats.get(item["id"])
            n = row["n"] if row else 0
            reward = row["reward"] / n if n else 0
            relevance = 4 if topic in item["topics"] else 1 if "general" in item["topics"] else 0
            return relevance + reward + math.sqrt(2 * math.log(total + 2) / (n + 1))
        chosen = max(candidates, key=score)
        return Selection("template", chosen["text"], chosen["id"], topic)

    def record_sent(self, chat, message, selection):
        fingerprint = hashlib.sha256(normalize(selection.text).encode()).hexdigest()
        with self.store.db:
            inserted = self.store.db.execute("INSERT OR IGNORE INTO adaptive_posts(chat,message,source,template_id,topic,fingerprint,sent) VALUES(?,?,?,?,?,?,?)",
                                            (chat, message, selection.source, selection.template_id, selection.topic, fingerprint, time.time())).rowcount
            if inserted:
                self.store.db.execute("INSERT OR IGNORE INTO adaptive_counts(chat) VALUES(?)", (chat,))
                column = "template" if selection.source == "template" else "gpt"
                self.store.db.execute(f"UPDATE adaptive_counts SET {column}={column}+1 WHERE chat=?", (chat,))

    def feedback(self, chat, message, reply_to, text):
        row = self.store.db.execute("SELECT sent FROM adaptive_posts WHERE chat=? AND message=?", (chat, reply_to)).fetchone()
        if not row or row["sent"] < time.time() - self.settings["feedback_window_hours"] * 3600:
            return
        negative = int(matches(text, ("spam", "reklam", "rahatsiz", "sus", "dur")))
        with self.store.db:
            inserted = self.store.db.execute("INSERT OR IGNORE INTO adaptive_feedback VALUES(?,?,?)", (chat, message, reply_to)).rowcount
            if inserted:
                self.store.db.execute("UPDATE adaptive_posts SET replies=replies+?,negative=negative+? WHERE chat=? AND message=?", (1-negative, negative, chat, reply_to))


async def scan_groups(client, settings, progress=None):
    """Inspect joined groups only, without joining or sending anything."""
    from telethon.errors import FloodWaitError
    groups = []
    async for dialog in client.iter_dialogs():
        if not dialog.is_group:
            continue
        try:
            context = await recent_context(client, dialog.entity, settings)
        except FloodWaitError as exc:
            # Checkpoint complete groups and report the rate limit; don't silently skip.
            return {"complete": False, "retry_after_seconds": exc.seconds, "groups": groups}
        except Exception as exc:
            groups.append({"id": dialog.id, "title": dialog.title, "error": type(exc).__name__, "candidate": False})
            continue
        entity = dialog.entity
        groups.append({
            "id": dialog.id,
            "title": dialog.title,
            **classify_group(dialog.title, context, settings["candidate_threshold"]),
            "baron_is_creator": bool(getattr(entity, "creator", False)),
            "baron_is_admin": bool(
                getattr(entity, "creator", False) or getattr(entity, "admin_rights", None)
            ),
            # Discovery and admin status are evidence for review, but neither silently
            # opts a community into automated posting.
            "permission_confirmed": False,
        })
        if progress:
            progress(len(groups))
        await asyncio.sleep(0.5)
    return {"complete": not any("error" in g for g in groups), "scanned_at": datetime.now(timezone.utc).isoformat(), "groups": groups}
