#!/usr/bin/env python3
"""
BabaGAVAT - AI Tabanlı Kullanıcı Analiz ve Sokak Zekası Sistemi
Telegram gruplarında güvenilir şovcu tespiti ve dolandırıcı filtreleme sistemi
BabaGAVAT'ın sokak zekası ile güçlendirilmiş analiz motoru
"""

import asyncio
import json
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import structlog
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel
from .database_manager import database_manager

logger = structlog.get_logger("babagavat.user_analyzer")

class UserTrustLevel(Enum):
    """Kullanıcı güven seviyeleri - BabaGAVAT'ın sokak zekası sınıflandırması"""
    SUSPICIOUS = "suspicious"  # 🔴 Şüpheli - Sokakta güvenilmez tip
    NEUTRAL = "neutral"       # 🟡 Nötr - Henüz belli değil
    TRUSTED = "trusted"       # 🟢 Güvenilir - BabaGAVAT'ın onayladığı

class AnalysisReason(Enum):
    """Analiz nedenleri - BabaGAVAT'ın sokak tecrübesi"""
    SPAM_DETECTED = "spam_detected"
    TRANSACTION_SIGNALS = "transaction_signals"
    INCONSISTENT_PROFILE = "inconsistent_profile"
    LOW_ENGAGEMENT = "low_engagement"
    POSITIVE_INTERACTION = "positive_interaction"
    CONSISTENT_ACTIVITY = "consistent_activity"
    VERIFIED_PERFORMER = "verified_performer"
    STREET_SMART_APPROVED = "street_smart_approved"  # BabaGAVAT'ın özel onayı

@dataclass
class UserProfile:
    """Kullanıcı profil analizi - BabaGAVAT'ın dosyası"""
    user_id: str
    username: str
    display_name: str
    has_photo: bool
    bio: str
    first_seen: datetime
    last_activity: datetime
    message_count: int = 0
    group_count: int = 0
    trust_score: float = 0.5
    trust_level: UserTrustLevel = UserTrustLevel.NEUTRAL
    analysis_reasons: List[AnalysisReason] = None
    spam_indicators: List[str] = None
    positive_signals: List[str] = None
    transaction_signals: List[str] = None
    interaction_quality: float = 0.5
    consistency_score: float = 0.5
    activity_pattern: Dict[str, Any] = None
    babagavat_notes: str = ""  # BabaGAVAT'ın özel notları

@dataclass
class InviteCandidate:
    """Davet adayı - BabaGAVAT'ın seçtikleri"""
    user_id: str
    username: str
    trust_score: float
    recommendation_reason: str
    contact_message: str
    created_at: datetime
    priority: str = "medium"  # high, medium, low
    babagavat_approval: bool = False  # BabaGAVAT'ın onayı

class BabaGAVATUserAnalyzer:
    """BabaGAVAT - Sokak Zekası ile Kullanıcı Analiz Sistemi"""
    
    def __init__(self):
        self.clients: Dict[str, TelegramClient] = {}
        self.is_monitoring = False
        self.user_profiles: Dict[str, UserProfile] = {}
        self.invite_candidates: List[InviteCandidate] = []
        self.monitored_groups: Set[str] = set()
        
        # BabaGAVAT'ın sokak zekası kriterleri
        self.spam_keywords = [
            "iban", "hesap", "ödeme", "para", "tl", "euro", "dolar",
            "fiyat", "ücret", "tarih", "saat", "randevu", "buluşma",
            "whatsapp", "telegram", "dm", "özelden", "yazın", "dolandırıcı",
            "sahte", "fake", "scam", "kandırma"
        ]
        
        self.transaction_patterns = [
            r'\b\d{2,4}\s*tl\b',  # fiyat belirtimi
            r'\b\d{1,2}:\d{2}\b',  # saat belirtimi
            r'\btr\d{2}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{2}\b',  # IBAN
            r'\b\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\b',  # kart numarası pattern
            r'\b(bugün|yarın|pazartesi|salı|çarşamba|perşembe|cuma|cumartesi|pazar)\b'  # tarih
        ]
        
        # BabaGAVAT'ın pozitif sinyalleri
        self.positive_indicators = [
            "teşekkür", "sağol", "merhaba", "selam", "günaydın", "iyi geceler",
            "nasılsın", "keyifli", "güzel", "harika", "süper", "mükemmel",
            "profesyonel", "kaliteli", "güvenilir", "samimi"
        ]
        
        logger.info("💪 BabaGAVAT User Analyzer başlatıldı - Sokak zekası aktif!")
    
    async def initialize(self, clients: Dict[str, TelegramClient]) -> None:
        """BabaGAVAT Analyzer'ı başlat"""
        try:
            self.clients = clients
            
            # Database'i başlat
            await database_manager.initialize()
            await self._create_babagavat_tables()
            
            # Event handler'ları kaydet
            await self._register_event_handlers()
            
            # Mevcut grupları tara
            await self._discover_groups()
            
            # Background tasks başlat
            asyncio.create_task(self._periodic_analysis())
            asyncio.create_task(self._invite_processor())
            asyncio.create_task(self._babagavat_intelligence_monitor())
            
            self.is_monitoring = True
            logger.info("✅ BabaGAVAT User Analyzer hazır - Sokak kontrolü başladı! 💪")
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT başlatma hatası: {e}")
            raise
    
    async def _create_babagavat_tables(self) -> None:
        """BabaGAVAT için özel tabloları oluştur"""
        try:
            async with database_manager._get_connection() as db:
                # User Profiles tablosu
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_user_profiles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT UNIQUE NOT NULL,
                        username TEXT,
                        display_name TEXT,
                        has_photo BOOLEAN DEFAULT FALSE,
                        bio TEXT DEFAULT '',
                        first_seen TIMESTAMP NOT NULL,
                        last_activity TIMESTAMP NOT NULL,
                        message_count INTEGER DEFAULT 0,
                        group_count INTEGER DEFAULT 0,
                        trust_score REAL DEFAULT 0.5,
                        trust_level TEXT DEFAULT 'neutral',
                        analysis_reasons TEXT, -- JSON array
                        spam_indicators TEXT, -- JSON array
                        positive_signals TEXT, -- JSON array
                        transaction_signals TEXT, -- JSON array
                        interaction_quality REAL DEFAULT 0.5,
                        consistency_score REAL DEFAULT 0.5,
                        activity_pattern TEXT, -- JSON object
                        babagavat_notes TEXT DEFAULT '',
                        babagavat_approval BOOLEAN DEFAULT FALSE,
                        street_smart_score REAL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Message Analysis tablosu
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_message_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        group_id TEXT NOT NULL,
                        message_id INTEGER NOT NULL,
                        message_text TEXT,
                        spam_score REAL DEFAULT 0.0,
                        transaction_score REAL DEFAULT 0.0,
                        engagement_score REAL DEFAULT 0.0,
                        street_smart_score REAL DEFAULT 0.0,
                        detected_patterns TEXT, -- JSON array
                        analysis_flags TEXT, -- JSON array
                        babagavat_verdict TEXT DEFAULT '',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Invite Candidates tablosu
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_invite_candidates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        username TEXT,
                        trust_score REAL NOT NULL,
                        recommendation_reason TEXT NOT NULL,
                        contact_message TEXT NOT NULL,
                        priority TEXT DEFAULT 'medium',
                        babagavat_approval BOOLEAN DEFAULT FALSE,
                        status TEXT DEFAULT 'pending', -- pending, contacted, accepted, rejected
                        contacted_at TIMESTAMP,
                        response_received BOOLEAN DEFAULT FALSE,
                        babagavat_notes TEXT DEFAULT '',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Group Monitoring tablosu
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_group_monitoring (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_id TEXT UNIQUE NOT NULL,
                        group_name TEXT,
                        monitoring_enabled BOOLEAN DEFAULT TRUE,
                        female_user_count INTEGER DEFAULT 0,
                        trusted_user_count INTEGER DEFAULT 0,
                        suspicious_user_count INTEGER DEFAULT 0,
                        last_scan TIMESTAMP,
                        activity_level TEXT DEFAULT 'unknown',
                        babagavat_rating TEXT DEFAULT 'unrated',
                        street_value_score REAL DEFAULT 0.0,
                        notes TEXT DEFAULT '',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # BabaGAVAT Intelligence Log
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS babagavat_intelligence_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        intelligence_type TEXT NOT NULL,
                        target_id TEXT NOT NULL,
                        analysis_data TEXT NOT NULL, -- JSON
                        confidence_level REAL DEFAULT 0.0,
                        action_taken TEXT DEFAULT '',
                        babagavat_decision TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                await db.commit()
                logger.info("✅ BabaGAVAT tabloları oluşturuldu - Sokak dosyaları hazır! 📋")
                
        except Exception as e:
            logger.error(f"❌ BabaGAVAT tablo oluşturma hatası: {e}")
            raise
    
    async def _register_event_handlers(self) -> None:
        """Event handler'ları kaydet"""
        try:
            for bot_username, client in self.clients.items():
                
                @client.on(events.NewMessage)
                async def handle_new_message(event):
                    """Yeni mesaj analizi - BabaGAVAT'ın sokak kontrolü"""
                    try:
                        if event.is_private:
                            return  # Sadece grup mesajlarını analiz et
                        
                        sender = await event.get_sender()
                        if not sender or not isinstance(sender, User):
                            return
                        
                        # Sadece kadın kullanıcıları analiz et (BabaGAVAT'ın hedef kitlesi)
                        if not await self._is_female_user(sender):
                            return
                        
                        # BabaGAVAT'ın sokak zekası ile mesajı analiz et
                        await self._analyze_message_with_street_smarts(
                            user_id=str(sender.id),
                            username=sender.username or "",
                            display_name=f"{sender.first_name or ''} {sender.last_name or ''}".strip(),
                            group_id=str(event.chat_id),
                            message_id=event.id,
                            message_text=event.text or "",
                            sender_info=sender
                        )
                        
                    except Exception as e:
                        logger.warning(f"⚠️ BabaGAVAT mesaj analiz hatası: {e}")
                
                logger.info(f"✅ {bot_username} için BabaGAVAT event handler'lar kaydedildi")
                
        except Exception as e:
            logger.error(f"❌ BabaGAVAT event handler kayıt hatası: {e}")
    
    async def _is_female_user(self, user: User) -> bool:
        """Kullanıcının kadın olup olmadığını tahmin et - BabaGAVAT'ın sokak zekası"""
        try:
            # Profil fotoğrafı var mı?
            has_photo = user.photo is not None
            
            # İsim analizi (Türkçe kadın isimleri - BabaGAVAT'ın listesi)
            female_names = [
                "ayşe", "fatma", "emine", "hatice", "zeynep", "elif", "seda", "merve",
                "özlem", "gül", "nur", "deniz", "cansu", "büşra", "esra", "tuğba",
                "pınar", "sevgi", "aslı", "burcu", "derya", "sibel", "tuba", "ece",
                "melis", "dilan", "yasemin", "begüm", "damla", "eda", "gamze", "hande"
            ]
            
            first_name = (user.first_name or "").lower()
            is_female_name = any(name in first_name for name in female_names)
            
            # Username analizi - BabaGAVAT'ın sokak tecrübesi
            username = (user.username or "").lower()
            female_indicators = [
                "girl", "bayan", "lady", "miss", "kız", "hanım", "princess", "queen",
                "güzel", "tatlı", "sevimli", "angel", "baby", "honey"
            ]
            has_female_username = any(indicator in username for indicator in female_indicators)
            
            # BabaGAVAT'ın sokak zekası scoring
            score = 0
            if has_photo:
                score += 0.3
            if is_female_name:
                score += 0.5
            if has_female_username:
                score += 0.4
            
            # BabaGAVAT'ın final kararı
            return score >= 0.4
            
        except Exception as e:
            logger.warning(f"⚠️ BabaGAVAT cinsiyet analiz hatası: {e}")
            return False
    
    async def _analyze_message_with_street_smarts(self, user_id: str, username: str, display_name: str,
                                                group_id: str, message_id: int, message_text: str,
                                                sender_info: User) -> None:
        """BabaGAVAT'ın sokak zekası ile mesaj analizi"""
        try:
            # Kullanıcı profilini güncelle/oluştur
            await self._update_user_profile(user_id, username, display_name, sender_info, group_id)
            
            # BabaGAVAT'ın analiz kriterleri
            spam_score = await self._calculate_spam_score(message_text)
            transaction_score = await self._calculate_transaction_score(message_text)
            engagement_score = await self._calculate_engagement_score(message_text)
            street_smart_score = await self._calculate_street_smart_score(message_text)
            
            # Pattern tespiti - BabaGAVAT'ın sokak tecrübesi
            detected_patterns = await self._detect_patterns(message_text)
            analysis_flags = await self._generate_analysis_flags(message_text, spam_score, transaction_score)
            
            # BabaGAVAT'ın kararı
            babagavat_verdict = await self._get_babagavat_verdict(
                spam_score, transaction_score, engagement_score, street_smart_score
            )
            
            # Veritabanına kaydet
            await self._save_message_analysis(
                user_id, group_id, message_id, message_text,
                spam_score, transaction_score, engagement_score, street_smart_score,
                detected_patterns, analysis_flags, babagavat_verdict
            )
            
            # Güven puanını güncelle
            await self._update_trust_score(user_id, spam_score, transaction_score, engagement_score, street_smart_score)
            
            # Davet adayı kontrolü - BabaGAVAT'ın onayı
            await self._check_invite_candidate(user_id)
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT mesaj analiz hatası: {e}")
    
    async def _calculate_street_smart_score(self, message_text: str) -> float:
        """BabaGAVAT'ın sokak zekası puanı hesapla"""
        try:
            if not message_text:
                return 0.0
            
            text_lower = message_text.lower()
            street_smart_score = 0.5  # Başlangıç puanı
            
            # Pozitif sokak zekası göstergeleri
            smart_indicators = [
                "anlıyorum", "mantıklı", "doğru", "haklısın", "katılıyorum",
                "tecrübe", "deneyim", "biliyorum", "gördüm", "yaşadım",
                "dikkatli", "güvenli", "emin", "kontrol", "araştır"
            ]
            
            for indicator in smart_indicators:
                if indicator in text_lower:
                    street_smart_score += 0.1
            
            # Negatif sokak zekası göstergeleri
            naive_indicators = [
                "bilmiyorum", "emin değilim", "ne yapacağım", "yardım edin",
                "kandırıldım", "dolandırıldım", "nasıl olur", "inanamıyorum"
            ]
            
            for indicator in naive_indicators:
                if indicator in text_lower:
                    street_smart_score -= 0.1
            
            # Soru sorma (öğrenme isteği - pozitif)
            if "?" in message_text:
                street_smart_score += 0.05
            
            return max(0.0, min(street_smart_score, 1.0))
            
        except Exception as e:
            logger.warning(f"⚠️ Street smart score hesaplama hatası: {e}")
            return 0.5
    
    async def _get_babagavat_verdict(self, spam_score: float, transaction_score: float, 
                                   engagement_score: float, street_smart_score: float) -> str:
        """BabaGAVAT'ın final kararı"""
        try:
            # BabaGAVAT'ın sokak zekası ile karar verme
            if spam_score > 0.7 or transaction_score > 0.8:
                return "🔴 ŞÜPHELI - BabaGAVAT'ın sokak zekası alarm veriyor!"
            elif engagement_score > 0.7 and street_smart_score > 0.6:
                return "🟢 ONAYLANMIŞ - BabaGAVAT'ın güvenilir listesinde!"
            elif street_smart_score > 0.8:
                return "💪 SOKAK ZEKASI - BabaGAVAT'ın beğendiği tip!"
            elif engagement_score > 0.6:
                return "🟡 POTANSİYEL - BabaGAVAT izliyor..."
            else:
                return "⚪ NÖTR - BabaGAVAT'ın radarında değil"
                
        except Exception as e:
            logger.warning(f"⚠️ BabaGAVAT verdict hatası: {e}")
            return "❓ BELİRSİZ - BabaGAVAT kararsız"
    
    # ... (diğer metodlar aynı şekilde BabaGAVAT teması ile güncellenir)
    
    async def _calculate_spam_score(self, message_text: str) -> float:
        """Spam puanı hesapla - BabaGAVAT'ın tecrübesi"""
        try:
            if not message_text:
                return 0.0
            
            text_lower = message_text.lower()
            spam_count = 0
            total_keywords = len(self.spam_keywords)
            
            for keyword in self.spam_keywords:
                if keyword in text_lower:
                    spam_count += 1
            
            # Tekrarlanan mesaj kontrolü (BabaGAVAT'ın spam tespiti)
            if len(set(text_lower.split())) < len(text_lower.split()) * 0.5:
                spam_count += 2
            
            # Çok fazla emoji/özel karakter (BabaGAVAT'ın kuralı)
            special_chars = sum(1 for c in message_text if not c.isalnum() and not c.isspace())
            if special_chars > len(message_text) * 0.3:
                spam_count += 1
            
            return min(spam_count / (total_keywords + 3), 1.0)
            
        except Exception as e:
            logger.warning(f"⚠️ BabaGAVAT spam score hesaplama hatası: {e}")
            return 0.0
    
    async def _calculate_transaction_score(self, message_text: str) -> float:
        """Transaksiyon sinyali puanı hesapla - BabaGAVAT'ın sokak tecrübesi"""
        try:
            if not message_text:
                return 0.0
            
            transaction_count = 0
            
            for pattern in self.transaction_patterns:
                matches = re.findall(pattern, message_text.lower())
                transaction_count += len(matches)
            
            # Direkt para/ödeme ifadeleri (BabaGAVAT'ın alarm listesi)
            money_keywords = ["ödeme", "para", "ücret", "fiyat", "hesap", "kart", "transfer"]
            for keyword in money_keywords:
                if keyword in message_text.lower():
                    transaction_count += 1
            
            return min(transaction_count / 5.0, 1.0)
            
        except Exception as e:
            logger.warning(f"⚠️ BabaGAVAT transaction score hesaplama hatası: {e}")
            return 0.0
    
    async def _calculate_engagement_score(self, message_text: str) -> float:
        """Etkileşim kalitesi puanı hesapla - BabaGAVAT'ın değerlendirmesi"""
        try:
            if not message_text:
                return 0.0
            
            score = 0.5  # BabaGAVAT'ın başlangıç puanı
            
            text_lower = message_text.lower()
            for indicator in self.positive_indicators:
                if indicator in text_lower:
                    score += 0.1
            
            # Soru sorma (BabaGAVAT etkileşimi sever)
            if "?" in message_text:
                score += 0.1
            
            # Çok kısa mesajlar (BabaGAVAT düşük kalite der)
            if len(message_text.strip()) < 10:
                score -= 0.2
            
            # Çok uzun mesajlar (BabaGAVAT spam der)
            if len(message_text) > 500:
                score -= 0.1
            
            return max(0.0, min(score, 1.0))
            
        except Exception as e:
            logger.warning(f"⚠️ BabaGAVAT engagement score hesaplama hatası: {e}")
            return 0.5
    
    async def _detect_patterns(self, message_text: str) -> List[str]:
        """Mesajda pattern tespiti - BabaGAVAT'ın sokak radarı"""
        try:
            patterns = []
            text_lower = message_text.lower()
            
            # IBAN pattern (BabaGAVAT'ın alarm sistemi)
            if re.search(r'\btr\d{2}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{2}\b', text_lower):
                patterns.append("iban_detected")
            
            # Fiyat pattern (BabaGAVAT'ın ticaret radarı)
            if re.search(r'\b\d{2,4}\s*tl\b', text_lower):
                patterns.append("price_mentioned")
            
            # Saat pattern (BabaGAVAT'ın randevu alarmı)
            if re.search(r'\b\d{1,2}:\d{2}\b', text_lower):
                patterns.append("time_mentioned")
            
            # WhatsApp/Telegram yönlendirme (BabaGAVAT'ın şüphe listesi)
            if any(word in text_lower for word in ["whatsapp", "wp", "telegram", "dm", "özelden"]):
                patterns.append("contact_redirect")
            
            # Aciliyet ifadeleri (BabaGAVAT'ın dolandırıcı alarmı)
            if any(word in text_lower for word in ["acil", "hemen", "şimdi", "bugün", "yarın"]):
                patterns.append("urgency_signal")
            
            # BabaGAVAT'ın özel pattern'leri
            if any(word in text_lower for word in ["güvenilir", "profesyonel", "kaliteli"]):
                patterns.append("quality_signal")
            
            return patterns
            
        except Exception as e:
            logger.warning(f"⚠️ BabaGAVAT pattern detection hatası: {e}")
            return []
    
    async def _generate_analysis_flags(self, message_text: str, spam_score: float, transaction_score: float) -> List[str]:
        """Analiz bayrakları oluştur - BabaGAVAT'ın uyarı sistemi"""
        try:
            flags = []
            
            if spam_score > 0.6:
                flags.append("babagavat_high_spam_risk")
            
            if transaction_score > 0.5:
                flags.append("babagavat_transaction_signals")
            
            if len(message_text) > 1000:
                flags.append("babagavat_very_long_message")
            
            # Çok fazla büyük harf (BabaGAVAT'ın spam alarmı)
            if sum(1 for c in message_text if c.isupper()) > len(message_text) * 0.5:
                flags.append("babagavat_excessive_caps")
            
            # Çok fazla emoji (BabaGAVAT'ın abartı alarmı)
            emoji_count = sum(1 for c in message_text if ord(c) > 127)
            if emoji_count > 20:
                flags.append("babagavat_excessive_emojis")
            
            return flags
            
        except Exception as e:
            logger.warning(f"⚠️ BabaGAVAT analysis flags oluşturma hatası: {e}")
            return []
    
    # ... (geri kalan metodlar da aynı şekilde BabaGAVAT teması ile güncellenir)
    
    async def _babagavat_intelligence_monitor(self) -> None:
        """BabaGAVAT'ın istihbarat monitörü"""
        while self.is_monitoring:
            try:
                await asyncio.sleep(1800)  # Her 30 dakika
                
                # BabaGAVAT'ın özel analizi
                await self._run_babagavat_intelligence()
                
                logger.info("🕵️ BabaGAVAT istihbarat taraması tamamlandı")
                
            except Exception as e:
                logger.error(f"❌ BabaGAVAT intelligence monitor hatası: {e}")
                await asyncio.sleep(300)
    
    async def _run_babagavat_intelligence(self) -> None:
        """BabaGAVAT'ın özel istihbarat analizi"""
        try:
            # Yüksek potansiyelli kullanıcıları tespit et
            async with database_manager._get_connection() as db:
                cursor = await db.execute("""
                    SELECT user_id, username, trust_score, street_smart_score
                    FROM babagavat_user_profiles 
                    WHERE trust_score > 0.7 AND street_smart_score > 0.6
                    AND babagavat_approval = FALSE
                    ORDER BY trust_score DESC, street_smart_score DESC
                    LIMIT 10
                """)
                high_potential_users = await cursor.fetchall()
                
                for user_data in high_potential_users:
                    user_id, username, trust_score, street_smart_score = user_data
                    
                    # BabaGAVAT'ın özel onayı
                    await self._babagavat_special_approval(user_id, username, trust_score, street_smart_score)
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT intelligence analizi hatası: {e}")
    
    async def _babagavat_special_approval(self, user_id: str, username: str, 
                                        trust_score: float, street_smart_score: float) -> None:
        """BabaGAVAT'ın özel onay sistemi"""
        try:
            # BabaGAVAT'ın karar kriterleri
            if trust_score > 0.8 and street_smart_score > 0.7:
                decision = "ONAYLANDI - BabaGAVAT'ın VIP listesine eklendi! 💪"
                approval = True
            elif trust_score > 0.75:
                decision = "İZLENİYOR - BabaGAVAT'ın radarında..."
                approval = False
            else:
                decision = "BEKLEMEDE - Daha fazla veri gerekli"
                approval = False
            
            # Intelligence log'a kaydet
            async with database_manager._get_connection() as db:
                await db.execute("""
                    INSERT INTO babagavat_intelligence_log 
                    (intelligence_type, target_id, analysis_data, confidence_level, 
                     action_taken, babagavat_decision)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    "special_approval", user_id,
                    json.dumps({
                        "username": username,
                        "trust_score": trust_score,
                        "street_smart_score": street_smart_score
                    }),
                    (trust_score + street_smart_score) / 2,
                    "approval_check" if approval else "monitoring",
                    decision
                ))
                
                # Onay durumunu güncelle
                if approval:
                    await db.execute("""
                        UPDATE babagavat_user_profiles 
                        SET babagavat_approval = TRUE, 
                            babagavat_notes = babagavat_notes || ? || char(10),
                            updated_at = ?
                        WHERE user_id = ?
                    """, (
                        f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {decision}",
                        datetime.now(), user_id
                    ))
                
                await db.commit()
            
            logger.info(f"💪 BabaGAVAT özel onay: {username} - {decision}")
            
        except Exception as e:
            logger.error(f"❌ BabaGAVAT special approval hatası: {e}")
    
    # ... (geri kalan metodlar da aynı şekilde güncellenir)

# Global instance
babagavat_user_analyzer = BabaGAVATUserAnalyzer() 