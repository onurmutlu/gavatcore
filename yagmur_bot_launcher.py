#!/usr/bin/env python3
import asyncio
import json
import os
import random
import time
from collections import deque
from datetime import datetime, timedelta

from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from telethon.tl.types import Channel, Chat, User

from config import TELEGRAM_API_HASH, TELEGRAM_API_ID


class YagmurConservativeLauncher:
    def __init__(self):
        self.client = None
        self.last_message_time = {}
        self.message_count_hour = 0
        self.hour_start = datetime.now()
        self.engaging_messages = []
        self.reply_messages = []
        # Anti-spam ayarları - AGRESIF MOD
        self.max_messages_per_hour = 80  # Saatte en fazla mesaj (agresif)
        self.min_interval_seconds_per_chat = 60  # Aynı gruba min 1 dk (agresif)
        self.max_interval_seconds_per_chat = 300  # Aynı gruba max 5 dk (agresif)
        # Dinamik aktivite takibi
        self.recent_activity = {}  # chat_id -> {'ppm': float, 'count': int, 'window_min': int}
        # Kısa süreli tekrar engelleme (dedup)
        self.sent_chat_history = {}  # chat_id -> deque[(normalized_text, ts)]
        self.sent_global_history = deque(maxlen=200)  # (normalized_text, ts)
        # Yazma izni olmayan gruplar
        self.blacklisted_chats = set()  # Yazma izni olmayan chat_id'ler

        # YENİ OPTIMIZASYON SİSTEMLERİ
        # Grup segmentasyonu ve analiz
        self.group_analytics = (
            {}
        )  # chat_id -> {'type': str, 'activity_score': float, 'response_rate': float}
        self.user_profiles = {}  # user_id -> {'preferences': list, 'interaction_count': int}
        self.message_performance = (
            {}
        )  # message_template -> {'success_rate': float, 'response_count': int}

        # Akıllı timing sistemi
        self.optimal_timing = {}  # chat_id -> {'best_hours': list, 'last_peak': datetime}
        self.timezone_offsets = {}  # chat_id -> timezone offset

        # Çoklu mesaj stratejisi
        self.concurrent_messages = 3  # Aynı anda gönderilecek max mesaj sayısı
        self.message_queue = []  # Bekleyen mesajlar

        # Etkileşim takip
        self.interaction_tracker = (
            {}
        )  # chat_id -> {'replies': int, 'reactions': int, 'forwards': int}
        self.trending_topics = []  # Güncel trending konular
        self.emoji_usage = {}  # Emoji kullanım istatistikleri

        # Bandit öğrenmesi (epsilon-greedy)
        self.bandit_epsilon = 0.2
        self.bandit_stats = {
            "OPEN": {},  # key -> {'wins': int, 'trials': int}
            "HOOK": {},
            "CTA": {},
            "TEMPLATE": {},
        }

        # Bekleyen etkileşim penceresi (3 dk)
        self.pending_engagement = {}  # chat_id -> {'ts': float, 'message_key': str}

        # Olay loglama
        self.events_log_path = os.path.join("logs", "yagmur_events.jsonl")
        try:
            os.makedirs("logs", exist_ok=True)
        except Exception:
            pass

        # Anti-ban PID kontrolü
        self.wait_scale = 1.0  # compute_next_wait ile çarpılacak katsayı (0.7 - 2.5 arası)
        self.pid_kp = 0.25
        self.pid_ki = 0.02
        self.pid_kd = 0.12
        self.pid_integral = 0.0
        self.pid_last_error = 0.0
        self.flood_events_recent = deque(maxlen=100)  # timestamp listesi
        self.target_flood_per_15min = 0  # hedef flood 0

    async def load_persona_messages(self):
        """Persona dosyasından mesajları yükle"""
        try:
            with open("data/personas/yagmur.json", "r", encoding="utf-8") as f:
                persona = json.load(f)
            self.engaging_messages = persona.get("engaging_messages", [])
            self.reply_messages = persona.get("reply_messages", [])
            # Store phone for later use in start()
            self.persona_phone = persona.get("phone", "+447832134241")
            print(f"✅ {len(self.engaging_messages)} engaging mesaj yüklendi")
        except Exception as e:
            print(f"❌ Persona mesajları yüklenemedi: {e}")
            self.persona_phone = "+447832134241"  # fallback

    async def check_group_permissions(self):
        """Grup yazma izinlerini kontrol et ve blacklist oluştur"""
        print("🔍 Grup yazma izinleri kontrol ediliyor...")
        blacklisted_count = 0
        total_groups = 0

        try:
            async for dialog in self.client.iter_dialogs():
                if dialog.is_group or dialog.is_channel:
                    chat = dialog.entity
                    chat_id = getattr(chat, "id", None)
                    if chat_id is None:
                        continue

                    total_groups += 1
                    chat_title = getattr(chat, "title", f"Chat {chat_id}")

                    try:
                        # Test mesajı göndermeye çalış (silinecek)
                        test_message = "🔍"
                        await self.client.send_message(chat, test_message)
                        # Test mesajını sil
                        async for message in self.client.iter_messages(chat, limit=1):
                            if message.text == test_message and message.out:
                                await message.delete()
                                break
                        print(f"✅ Yazma izni var: {chat_title}")
                    except Exception as e:
                        error_msg = str(e).lower()
                        if "can't write" in error_msg or "write in this chat" in error_msg:
                            self.blacklisted_chats.add(chat_id)
                            blacklisted_count += 1
                            print(f"🚫 Yazma izni yok: {chat_title}")
                        else:
                            print(f"⚠️ Kontrol hatası: {chat_title} - {e}")

        except Exception as e:
            print(f"❌ Grup izin kontrolü hatası: {e}")

        print(
            f"📊 Grup izin kontrolü tamamlandı: {total_groups} grup, {blacklisted_count} blacklist"
        )
        print(f"🚫 Blacklist'te {len(self.blacklisted_chats)} grup var")

    async def analyze_group_activity_patterns(self):
        """Grup aktivite patternlerini analiz et ve optimal timing belirle"""
        print("📈 Grup aktivite patternleri analiz ediliyor...")

        for chat_id in self.group_analytics:
            if chat_id in self.blacklisted_chats:
                continue

            try:
                # Son 24 saatteki mesaj dağılımını analiz et
                hourly_activity = {}
                now = datetime.now()

                async for message in self.client.iter_messages(chat_id, limit=500):
                    if message.date < now - timedelta(hours=24):
                        break
                    hour = message.date.hour
                    hourly_activity[hour] = hourly_activity.get(hour, 0) + 1

                # En aktif saatleri bul
                if hourly_activity:
                    best_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[
                        :3
                    ]
                    self.optimal_timing[chat_id] = {
                        "best_hours": [h[0] for h in best_hours],
                        "last_peak": now,
                        "activity_score": max(hourly_activity.values()) / 24,
                    }
                    print(f"🎯 {chat_id}: En aktif saatler {[h[0] for h in best_hours]}")

            except Exception as e:
                print(f"⚠️ Grup analiz hatası {chat_id}: {e}")

    def is_optimal_time_to_send(self, chat_id):
        """Bu grup için optimal zaman mı kontrol et"""
        if chat_id not in self.optimal_timing:
            return True  # Bilgi yoksa gönder

        current_hour = datetime.now().hour
        best_hours = self.optimal_timing[chat_id]["best_hours"]

        # En iyi saatlerden birinde miyiz?
        if current_hour in best_hours:
            return True

        # Son peak'ten 2 saat geçmişse de gönder
        last_peak = self.optimal_timing[chat_id]["last_peak"]
        if (datetime.now() - last_peak).total_seconds() > 7200:  # 2 saat
            return True

        return False

    async def segment_groups(self):
        """Grupları tip ve aktiviteye göre segmentlere ayır"""
        print("🏷️ Grup segmentasyonu yapılıyor...")

        async for dialog in self.client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                chat = dialog.entity
                chat_id = getattr(chat, "id", None)
                if not chat_id or chat_id in self.blacklisted_chats:
                    continue

                chat_title = getattr(chat, "title", "").lower()

                # Grup tipini belirle
                group_type = "general"
                if any(
                    keyword in chat_title
                    for keyword in ["arayış", "dating", "flört", "tanışma", "sevgili"]
                ):
                    group_type = "dating"
                elif any(
                    keyword in chat_title for keyword in ["sohbet", "chat", "konuşma", "muhabbet"]
                ):
                    group_type = "chat"
                elif any(keyword in chat_title for keyword in ["kadın", "erkek", "bay", "bayan"]):
                    group_type = "gender_specific"
                elif any(keyword in chat_title for keyword in ["şehir", "il", "bölge", "mahalle"]):
                    group_type = "location_based"

                # Aktivite skorunu hesapla
                activity_score = 0.0
                try:
                    ppm = await self.estimate_group_activity(chat, window_minutes=60)
                    activity_score = min(ppm / 5.0, 1.0)  # 0-1 arası normalize et
                except:
                    activity_score = 0.5  # Varsayılan

                # Grup analizini kaydet
                self.group_analytics[chat_id] = {
                    "type": group_type,
                    "activity_score": activity_score,
                    "response_rate": 0.0,  # Başlangıçta 0
                    "title": chat_title,
                }

                print(f"📊 {chat_title[:30]}: {group_type} (aktivite: {activity_score:.2f})")

    def get_group_priority(self, chat_id):
        """Grup önceliğini hesapla"""
        if chat_id not in self.group_analytics:
            return 0.5

        analytics = self.group_analytics[chat_id]
        activity_score = analytics["activity_score"]
        response_rate = analytics["response_rate"]

        # Aktivite ve yanıt oranına göre öncelik hesapla
        priority = (activity_score * 0.7) + (response_rate * 0.3)
        return min(priority, 1.0)

    def can_send_message(self, chat_id, dynamic_min_override: int = None):
        """Mesaj gönderme sınırını kontrol et"""
        now = datetime.now()

        # Saatlik limit kontrolü (max 15 mesaj/saat)
        if (now - self.hour_start).total_seconds() > 3600:
            self.message_count_hour = 0
            self.hour_start = now

        if self.message_count_hour >= self.max_messages_per_hour:
            return False

        # Chat bazlı limit (dinamik taban aralık)
        if chat_id in self.last_message_time:
            time_diff = (now - self.last_message_time[chat_id]).total_seconds()
            min_gap = (
                dynamic_min_override
                if dynamic_min_override is not None
                else self.min_interval_seconds_per_chat
            )
            if time_diff < min_gap:
                return False

        return True

    def update_message_count(self, chat_id):
        """Mesaj sayacını güncelle"""
        self.last_message_time[chat_id] = datetime.now()
        self.message_count_hour += 1

    async def send_engaging_message(self, chat):
        """Gruba engaging mesaj gönder"""
        chat_id = getattr(chat, "id", None)
        # Dinamik alt aralık: yüksek aktivitede 120s'e kadar düşür
        dynamic_min = None
        activity = self.recent_activity.get(chat_id)
        if activity:
            ppm = activity.get("ppm", 0)
            if ppm >= 3.0:
                dynamic_min = 60
            elif ppm >= 2.0:
                dynamic_min = 90
            elif ppm >= 1.0:
                dynamic_min = 120
        if not self.can_send_message(chat_id, dynamic_min_override=dynamic_min):
            return

        # Dedup kontrollü mesaj üretimi
        attempts = 0
        message = self.generate_engaging_message(chat)
        while self._is_duplicate(chat.id, message) and attempts < 5:
            attempts += 1
            message = self.generate_engaging_message(chat)
        if self._is_duplicate(chat.id, message):
            # Zorunlu farklılaştırma
            message = message + " " + random.choice(["✨", "💕", "💫", "🔥"])

        try:
            await self.client.send_message(chat, message)
            self.update_message_count(chat_id)
            self._record_sent(chat_id, message)

            # Mesaj performansını takip et
            self.track_message_performance(message, chat_id)

            print(f"📢 Gruba mesaj gönderildi: {chat.title}")
        except FloodWaitError as e:
            print(f"⏳ FloodWait: {e.seconds} saniye bekleniyor...")
            await asyncio.sleep(e.seconds)
            # Flood olayını PID için kaydet
            self.flood_events_recent.append(time.time())
            # PID hata sinyali: flood sayısı hedefin üstünde -> wait_scale artır
            self._pid_adjust_wait_scale()
        except Exception as e:
            error_msg = str(e).lower()
            if "can't write" in error_msg or "write in this chat" in error_msg:
                # Yazma izni olmayan grubu blacklist'e ekle
                self.blacklisted_chats.add(chat_id)
                print(f"🚫 Grup blacklist'e eklendi (yazma izni yok): {chat.title}")
            else:
                print(f"❌ Mesaj gönderilemedi: {e}")

    def track_message_performance(self, message, chat_id):
        """Mesaj performansını takip et"""
        message_key = message[:20]  # İlk 20 karakteri key olarak kullan

        if message_key not in self.message_performance:
            self.message_performance[message_key] = {
                "success_rate": 0.0,
                "response_count": 0,
                "total_sent": 0,
            }

        self.message_performance[message_key]["total_sent"] += 1
        # Bekleyen etkileşim izleme (3 dk pencerede cevap gelirse win say)
        self.pending_engagement[chat_id] = {"ts": time.time(), "message_key": message_key}

        # Olay logu
        self._log_event(
            {"type": "sent", "chat_id": chat_id, "message_key": message_key, "ts": time.time()}
        )

    def _update_bandit(self, bandit_bucket: str, key: str, win: bool):
        bucket = self.bandit_stats.setdefault(bandit_bucket, {})
        stat = bucket.setdefault(key, {"wins": 0, "trials": 0})
        stat["trials"] += 1
        if win:
            stat["wins"] += 1

    def _choose_bandit(self, bandit_bucket: str, candidates: list) -> str:
        # epsilon-greedy seçim
        if not candidates:
            return ""
        if random.random() < self.bandit_epsilon:
            return random.choice(candidates)
        bucket = self.bandit_stats.setdefault(bandit_bucket, {})
        # Empirik başarı oranına göre en iyi
        best_key = candidates[0]
        best_rate = -1.0
        for key in candidates:
            stat = bucket.get(key, {"wins": 0, "trials": 0})
            rate = (stat["wins"] / stat["trials"]) if stat["trials"] > 0 else 0.0
            if rate > best_rate:
                best_rate = rate
                best_key = key
        return best_key

    def _log_event(self, payload: dict) -> None:
        try:
            with open(self.events_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception:
            pass

    async def send_multiple_messages(self, target_chats):
        """Birden fazla gruba aynı anda mesaj gönder"""
        if not target_chats:
            return

        # En fazla concurrent_messages kadar mesaj gönder
        selected_chats = target_chats[: self.concurrent_messages]

        # Paralel mesaj gönderme
        tasks = []
        for chat in selected_chats:
            task = asyncio.create_task(self.send_engaging_message(chat))
            tasks.append(task)

        # Tüm mesajları bekle
        await asyncio.gather(*tasks, return_exceptions=True)

    def _pid_adjust_wait_scale(self):
        """Flood olaylarına göre bekleme katsayısını PID ile ayarla"""
        now_ts = time.time()
        # Son 15 dk içindeki flood sayısı
        window = 900
        recent = [t for t in self.flood_events_recent if now_ts - t <= window]
        self.flood_events_recent.clear()
        self.flood_events_recent.extend(recent)
        error = len(recent) - self.target_flood_per_15min
        self.pid_integral += error
        derivative = error - self.pid_last_error
        adjust = (
            (self.pid_kp * error) + (self.pid_ki * self.pid_integral) + (self.pid_kd * derivative)
        )
        self.pid_last_error = error
        # Ölçeği güncelle ve sınırla
        self.wait_scale = max(0.7, min(2.5, self.wait_scale + adjust * 0.1))
        self._log_event(
            {"type": "pid_update", "error": error, "wait_scale": self.wait_scale, "ts": now_ts}
        )

    def _normalize_text(self, text: str) -> str:
        return (text or "").strip().lower()

    def _is_duplicate(self, chat_id: int, text: str) -> bool:
        now = time.time()
        norm = self._normalize_text(text)
        # Global 5 dk içinde tekrar engelle
        for tnorm, ts in list(self.sent_global_history):
            if now - ts <= 300 and tnorm == norm:
                return True
        # Chat bazlı 30 dk içinde tekrar engelle
        dq = self.sent_chat_history.get(chat_id)
        if dq:
            for tnorm, ts in list(dq):
                if now - ts <= 1800 and tnorm == norm:
                    return True
        return False

    def _record_sent(self, chat_id: int, text: str) -> None:
        now = time.time()
        norm = self._normalize_text(text)
        self.sent_global_history.append((norm, now))
        dq = self.sent_chat_history.get(chat_id)
        if dq is None:
            dq = deque(maxlen=200)
            self.sent_chat_history[chat_id] = dq
        dq.append((norm, now))

    def generate_engaging_message(self, chat) -> str:
        """Persona + şablonlardan çeşitli engaging mesaj üretir - OPTIMIZE EDİLMİŞ + BANDIT."""
        chat_id = getattr(chat, "id", None)
        base_pool = list(self.engaging_messages) if self.engaging_messages else []

        # Grup tipine göre özelleştirilmiş mesajlar
        group_type = self.group_analytics.get(chat_id, {}).get("type", "general")

        # Güncel trending konular
        trending_topics = [
            "bu akşam ne yapıyorsun?",
            "hangi şehirdesin?",
            "yaş kaç?",
            "hangi müziği seviyorsun?",
            "favori yemeğin ne?",
            "hobilerin neler?",
        ]

        # Grup tipine göre özelleştirilmiş içerik
        if group_type == "dating":
            openings = ["Selam canım 😘", "Hey güzelim 💋", "Merhaba tatlım 💖", "Hii sevgilim 🔥"]
            hooks = [
                "tanışmak isteyen var mı?",
                "sohbet edelim mi?",
                "görüşmek isteyen?",
                "randevu veren var mı?",
            ]
            ctas = ["dm'ye gel ♥", "yazsana güzelim", "buradaysan +1", "hızlı dönerim 💞"]
        elif group_type == "general":
            openings = ["Selam 😘", "Hey 💋", "Merhaba 💖", "Hii 🔥", "Canslarım 💫"]
            hooks = ["müsait olan var mı?", "kimler aktif?", "sohbet edelim mi?", "ses atayım mı?"]
            ctas = ["dm'ye gel ♥", "yazsana", "buradaysan +1", "yakın olan var mı?"]
        else:
            openings = ["Selam 😘", "Hey 💋", "Merhaba 💖", "Hii 🔥"]
            hooks = ["müsait olan var mı?", "kimler aktif?", "sohbet edelim mi?"]
            ctas = ["dm'ye gel ♥", "yazsana", "buradaysan +1"]

        # Trending emojiler (bandit ile seçilecek)
        popular_emojis = ["💋", "🔥", "✨", "💕", "😍", "😈", "😉", "💞", "💫", "🥰", "😘", "🤗"]

        # Mesaj şablonları
        templates = [
            "{open} {hook} {cta} {emoji}",
            "{open}! {hook} {emoji}",
            "{hook} {cta}",
            "{open} {cta} {emoji}",
            "{trending} {emoji}",
            "{open} {trending} {cta} {emoji}",
        ]

        # Bandit ile OPEN/HOOK/CTA/TEMPLATE seçimleri
        chosen_open = self._choose_bandit("OPEN", openings)
        if not chosen_open:
            chosen_open = random.choice(openings)
        chosen_hook = self._choose_bandit("HOOK", hooks) or random.choice(hooks)
        chosen_cta = self._choose_bandit("CTA", ctas) or random.choice(ctas)
        chosen_template = self._choose_bandit("TEMPLATE", templates) or random.choice(templates)
        chosen_trending = random.choice(trending_topics)
        chosen_emoji = random.choice(popular_emojis)

        generated = chosen_template.format(
            open=chosen_open,
            hook=chosen_hook,
            cta=chosen_cta,
            emoji=chosen_emoji,
            trending=chosen_trending,
        )

        # Persona mesajları ile karıştır
        if base_pool and random.random() < 0.4:  # %40 persona, %60 optimize edilmiş/bandit
            return random.choice(base_pool)

        return generated

    async def estimate_group_activity(self, chat, window_minutes: int = 15) -> float:
        """Son window_minutes içinde dakikadaki mesaj sayısı (ppm) tahmini."""
        try:
            since = datetime.now() - timedelta(minutes=window_minutes)
            count = 0
            me = await self.client.get_me()
            async for m in self.client.iter_messages(chat, limit=200):
                if m.date < since:
                    break
                if m.out:
                    continue  # kendi mesajlarımızı sayma
                count += 1
            ppm = count / float(window_minutes)
            self.recent_activity[getattr(chat, "id", None)] = {
                "ppm": ppm,
                "count": count,
                "window_min": window_minutes,
            }
            return ppm
        except Exception:
            return 0.0

    def compute_next_wait(self) -> int:
        """Son ölçülen en yüksek aktiviteye göre bekleme süresi belirle - AGRESIF MOD."""
        top_ppm = 0.0
        for v in self.recent_activity.values():
            top_ppm = max(top_ppm, v.get("ppm", 0.0))
        if top_ppm >= 3.0:
            base = random.randint(30, 60)  # çok hızlı akış - AGRESIF
        elif top_ppm >= 2.0:
            base = random.randint(45, 90)  # hızlı akış - AGRESIF
        elif top_ppm >= 1.0:
            base = random.randint(60, 120)  # orta akış - AGRESIF
        else:
            base = random.randint(90, 180)  # normal/ düşük akış - AGRESIF
        # PID ölçekleme uygula
        scaled = int(base * self.wait_scale)
        return max(20, min(600, scaled))

    async def start(self):
        print("💓 Yağmur Bot (AGRESIF MODE) başlatılıyor...")
        print("🔥 AGRESIF MODE: Yüksek frekans, düşük aralık")
        print("🚫 DM yanıtları devre dışı")
        print("📢 Sadece grup mesajları aktif")

        # Persona mesajlarını yükle
        await self.load_persona_messages()

        # Persona dosyasından telefon al (load_persona_messages'da yüklendi)
        phone = getattr(self, "persona_phone", "+447832134241")
        clean_phone = phone.replace("+", "")
        session_path = f"sessions/_{clean_phone}"

        print(f"📱 Telefon: {phone}")
        print(f"💾 Session: {session_path}")

        self.client = TelegramClient(
            session_path,
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH,
            device_model="Yağmur Bot",
            system_version="GAVATCore v2.0",
        )

        await self.client.start()
        me = await self.client.get_me()
        print(f"✅ Yağmur aktif: @{me.username} (ID: {me.id})")
        print(
            f"⏰ Saatlik üst limit: {self.max_messages_per_hour}, taban aralık: {int(self.min_interval_seconds_per_chat/60)} dk"
        )

        # Grup yazma izinlerini kontrol et
        await self.check_group_permissions()

        # Grup analizlerini başlat
        await self.analyze_group_activity_patterns()

        # Grup segmentasyonunu başlat
        await self.segment_groups()

        @self.client.on(events.NewMessage(incoming=True))
        async def handler(event):
            try:
                # DM'leri tamamen yoksay
                if event.is_private:
                    try:
                        sender = await event.get_sender()
                        if sender and not getattr(sender, "bot", False):
                            print(f"🚫 DM yoksayıldı: {sender.first_name}")
                    except Exception as e:
                        print(f"⚠️ DM sender hatası: {e}")
                    return

                # Sadece gruplarda çalış
                if event.is_group or event.is_channel:
                    chat = await event.get_chat()
                    sender_name = "Unknown"
                    try:
                        sender = await event.get_sender()
                        # Bot mesajlarını yoksay
                        if sender and getattr(sender, "bot", False):
                            return

                        if isinstance(sender, User):
                            sender_name = sender.first_name or sender.username or "User"
                        elif isinstance(sender, (Chat, Channel)):
                            sender_name = getattr(sender, "title", None) or "Channel"
                    except Exception as e:
                        print(f"⚠️ Sender bilgisi alınamadı: {e}")
                        sender_name = "Unknown"
                    print(f"👥 Grup mesajı: {getattr(chat, 'title', 'Grup')} - {sender_name}")
                    # Reply devre dışı (spam riskini azaltmak için)

                    # Etkileşim (yanıt) tespiti: bot mesajından sonra gelen inbound kabul
                    chat_id = getattr(chat, "id", None)
                    pend = self.pending_engagement.get(chat_id)
                    if pend and (time.time() - pend["ts"] <= 180):  # 3 dk pencere
                        key = pend["message_key"]
                        perf = self.message_performance.get(key)
                        if perf:
                            perf["response_count"] += 1
                            # Basit başarı: 1 yanıt = win
                            perf["success_rate"] = perf["response_count"] / max(
                                1, perf["total_sent"]
                            )
                        # Bandit güncellemeleri (pozitif ödül)
                        # crude parse: template/open/hook/cta anahtarlarını çıkar
                        # Not: generate sırasında seçilenler string olarak gömülü; kabaca çıkarım yapıyoruz
                        try:
                            # Örnek anahtarlar: ilk kelimelerden tahmin
                            if "dm'ye gel" in event.raw_text.lower():
                                self._update_bandit("CTA", "dm'ye gel ♥", True)
                            if "kimler aktif" in event.raw_text.lower():
                                self._update_bandit("HOOK", "kimler aktif?", True)
                        except Exception:
                            pass
                        # pencereyi kapat
                        self.pending_engagement.pop(chat_id, None)
            except Exception as e:
                print(f"⚠️ Handler genel hatası: {e}")

        # Periyodik engaging mesajlar (dinamik frekans; her döngüde tek hedef)
        async def periodic_engagement():
            while True:
                try:
                    # Önce uygun hedef grupları ve aktiviteyi ölç
                    eligible_chats = []
                    priority_chats = []  # max aralığı aşanlar öncelikli
                    self.recent_activity.clear()
                    async for dialog in self.client.iter_dialogs():
                        if dialog.is_group or dialog.is_channel:
                            chat = dialog.entity
                            chat_id = getattr(chat, "id", None)
                            if chat_id is None:
                                continue
                            # Blacklist kontrolü
                            if chat_id in self.blacklisted_chats:
                                continue
                            # Aktiviteyi ölç (15 dk pencerede)
                            ppm = await self.estimate_group_activity(chat, window_minutes=15)
                            # Dinamik min aralığı belirle
                            dynamic_min = 120 if ppm >= 1.0 else self.min_interval_seconds_per_chat
                            if self.can_send_message(chat_id, dynamic_min_override=dynamic_min):
                                eligible_chats.append((chat, ppm))
                                last_ts = self.last_message_time.get(chat_id)
                                if last_ts:
                                    elapsed = (datetime.now() - last_ts).total_seconds()
                                    if elapsed >= self.max_interval_seconds_per_chat:
                                        priority_chats.append((chat, ppm))
                                else:
                                    priority_chats.append((chat, ppm))

                    # Çoklu mesaj stratejisi - birden fazla gruba aynı anda mesaj gönder
                    if eligible_chats and self.message_count_hour < self.max_messages_per_hour:
                        pool = priority_chats if priority_chats else eligible_chats
                        # ppm'e göre sıralayıp en iyilerini seç
                        pool.sort(key=lambda x: x[1], reverse=True)

                        # Optimal timing kontrolü ile filtrele
                        optimal_chats = []
                        for chat, ppm in pool:
                            chat_id = getattr(chat, "id", None)
                            if self.is_optimal_time_to_send(chat_id):
                                optimal_chats.append(chat)

                        if optimal_chats:
                            # En fazla 3 gruba aynı anda mesaj gönder
                            selected_chats = optimal_chats[: self.concurrent_messages]
                            await self.send_multiple_messages(selected_chats)
                        else:
                            # Optimal zaman yoksa tek mesaj gönder
                            candidates = (
                                [c[0] for c in pool[:5]] if len(pool) > 5 else [c[0] for c in pool]
                            )
                            target = random.choice(candidates)
                            await self.send_engaging_message(target)

                    # Bir sonraki bekleme süresini dinamik belirle
                    wait_time = self.compute_next_wait()
                    await asyncio.sleep(wait_time)

                except Exception as e:
                    print(f"❌ Periodic engagement hatası: {e}")
                    await asyncio.sleep(300)  # 5 dakika bekle

        # Periodic engagement'ı başlat
        asyncio.create_task(periodic_engagement())

        print("💓 Yağmur AGRESIF MODE hazır!")
        print("🔥 Yüksek frekans ile çalışıyor")
        await self.client.run_until_disconnected()


if __name__ == "__main__":
    launcher = YagmurConservativeLauncher()
    asyncio.run(launcher.start())
