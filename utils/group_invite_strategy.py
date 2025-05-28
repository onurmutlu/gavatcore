#!/usr/bin/env python3
"""
@arayisvips Grup Üye Artırma Stratejisi
Bu modül genel tanıtım grubumuz için etkili üye kazanma stratejileri uygular.
"""

import asyncio
import random
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple
from utils.log_utils import log_event
from telethon.errors import ChatWriteForbiddenError, UserPrivacyRestrictedError, FloodWaitError
from core.analytics_logger import log_analytics
from core.invite_manager import invite_manager

class GroupInviteStrategy:
    def __init__(self):
        self.target_group = "@arayisonlyvips"
        self.target_group_id = None  # Runtime'da set edilecek
        self.invite_stats = {
            "total_invites": 0,
            "successful_invites": 0,
            "failed_invites": 0,
            "privacy_blocks": 0,
            "flood_waits": 0
        }
        
        # Davet mesaj şablonları - çeşitli yaklaşımlar
        self.invite_templates = {
            "casual": [
                "🌟 Merhaba! Yeni bir sohbet grubumuz var, katılmak ister misin? @arayisonlyvips",
                "💬 Selam! Eğlenceli sohbet grubumuz @arayisonlyvips'e davetlisin! Gel tanışalım 😊",
                "🎉 Hey! @arayisonlyvips grubumuzda güzel sohbetler dönüyor, sen de gel! 💕",
                "✨ Merhaba canım! @arayisonlyvips'te güzel bir topluluk oluşturduk, katıl bize! 🌸"
            ],
            "vip_focused": [
                "💎 VIP içeriklerimden haberdar olmak istersen @arayisonlyvips grubuna katıl! 🔥",
                "🎭 Show'larım ve özel içeriklerim hakkında @arayisonlyvips'te duyuru yapıyorum! 💋",
                "⭐ Premium deneyimler için @arayisonlyvips grubumuzda buluşalım! 😘",
                "🌟 Özel içeriklerim ve VIP fırsatlarım için @arayisonlyvips'e gel! 💎"
            ],
            "community": [
                "👥 @arayisonlyvips'te harika bir topluluk var! Sen de aramıza katıl 🤗",
                "🏠 @arayisonlyvips grubumuz sıcak bir aile gibi, sen de gel! 💕",
                "🌈 @arayisonlyvips'te her türden insan var, çok eğlenceli! Katıl bize 😊",
                "💫 @arayisonlyvips grubunda güzel dostluklar kuruyoruz, sen de gel! ✨"
            ],
            "exclusive": [
                "🔐 Sadece özel kişileri davet ettiğim @arayisonlyvips grubuna hoş geldin! 💎",
                "🎯 Seçkin üyelerim için @arayisonlyvips grubunu kurdum, katıl! ⭐",
                "👑 @arayisonlyvips'e sadece kaliteli insanları alıyorum, sen de gel! 💋",
                "🌟 Özel davetiyem: @arayisonlyvips grubuna katıl, pişman olmayacaksın! 🔥"
            ]
        }
        
        # Takip mesajları - davet sonrası
        self.followup_messages = [
            "🎉 @arayisonlyvips grubuna hoş geldin! Kendini tanıt bakalım 😊",
            "💕 @arayisonlyvips'e katıldığın için teşekkürler! Nasılsın? 🌸",
            "✨ @arayisonlyvips grubumuzda seni görmek güzel! Sohbet edelim 💬",
            "🌟 @arayisonlyvips'te yenisin! Grubumuz hakkında soru varsa sor 😘"
        ]
        
        # Hedef kitle kategorileri
        self.target_audiences = {
            "potential_customers": {
                "keywords": ["vip", "show", "özel", "premium", "exclusive"],
                "template_category": "vip_focused",
                "priority": "high"
            },
            "social_users": {
                "keywords": ["sohbet", "chat", "arkadaş", "tanış", "dostluk"],
                "template_category": "community", 
                "priority": "medium"
            },
            "curious_users": {
                "keywords": ["merak", "ilginç", "nasıl", "ne", "kim"],
                "template_category": "casual",
                "priority": "medium"
            },
            "vip_seekers": {
                "keywords": ["para", "ücret", "fiyat", "satın", "al"],
                "template_category": "exclusive",
                "priority": "high"
            }
        }

    async def initialize_group(self, client):
        """Hedef grubu initialize et"""
        try:
            group_entity = await client.get_entity(self.target_group)
            self.target_group_id = group_entity.id
            log_event("group_invite", f"✅ Hedef grup initialize edildi: {self.target_group} (ID: {self.target_group_id})")
            return True
        except Exception as e:
            log_event("group_invite", f"❌ Hedef grup initialize hatası: {e}")
            return False

    def categorize_user(self, user_message: str) -> str:
        """Kullanıcıyı mesajına göre kategorize et"""
        message_lower = user_message.lower()
        
        # Her kategori için keyword match kontrolü
        for category, info in self.target_audiences.items():
            for keyword in info["keywords"]:
                if keyword in message_lower:
                    return category
        
        # Default kategori
        return "social_users"

    def get_invite_message(self, category: str = "casual") -> str:
        """Kategoriye göre davet mesajı seç"""
        template_category = self.target_audiences.get(category, {}).get("template_category", "casual")
        templates = self.invite_templates.get(template_category, self.invite_templates["casual"])
        return random.choice(templates)

    async def send_group_invite(self, client, user_id: int, username: str, user_message: str = "", bot_username: str = None) -> bool:
        """Kullanıcıya grup daveti gönder"""
        try:
            # Bot username'i al
            if not bot_username:
                try:
                    me = await client.get_me()
                    bot_username = me.username or f"bot_{me.id}"
                except:
                    bot_username = "unknown_bot"
            
            # Merkezi davet yöneticisinden kontrol
            if self.target_group_id:
                can_invite, reason = await invite_manager.can_send_group_invite(
                    bot_username, user_id, self.target_group_id, client
                )
                
                if not can_invite:
                    log_event("group_invite", f"🚫 Davet engellendi: {username} ({user_id}) - {reason}")
                    return False
            
            # Kullanıcıyı kategorize et
            category = self.categorize_user(user_message) if user_message else "casual"
            
            # Uygun davet mesajını seç
            invite_message = self.get_invite_message(category)
            
            # Davet mesajını gönder
            await client.send_message(user_id, invite_message)
            
            # İstatistikleri güncelle
            self.invite_stats["total_invites"] += 1
            self.invite_stats["successful_invites"] += 1
            
            # Merkezi kayıt
            if self.target_group_id:
                await invite_manager.record_group_invite(bot_username, user_id, self.target_group_id)
            
            log_event("group_invite", f"📤 Grup daveti gönderildi: {username} ({user_id}) - Kategori: {category}")
            log_analytics("group_invite", "invite_sent", {
                "user_id": user_id,
                "username": username,
                "category": category,
                "message": invite_message
            })
            
            return True
            
        except UserPrivacyRestrictedError:
            self.invite_stats["privacy_blocks"] += 1
            log_event("group_invite", f"🚫 Kullanıcı gizlilik engeli: {username} ({user_id})")
            return False
            
        except FloodWaitError as e:
            self.invite_stats["flood_waits"] += 1
            log_event("group_invite", f"⏰ Flood wait: {e.seconds}s - {username} ({user_id})")
            await asyncio.sleep(e.seconds)
            return False
            
        except Exception as e:
            self.invite_stats["failed_invites"] += 1
            log_event("group_invite", f"❌ Davet gönderim hatası: {username} ({user_id}) - {e}")
            return False

    async def send_followup_message(self, client, user_id: int, username: str, delay: int = 300):
        """Davet sonrası takip mesajı gönder"""
        try:
            await asyncio.sleep(delay)  # 5 dakika bekle
            
            followup = random.choice(self.followup_messages)
            await client.send_message(user_id, followup)
            
            log_event("group_invite", f"💬 Takip mesajı gönderildi: {username} ({user_id})")
            log_analytics("group_invite", "followup_sent", {
                "user_id": user_id,
                "username": username,
                "message": followup
            })
            
        except Exception as e:
            log_event("group_invite", f"❌ Takip mesajı hatası: {username} ({user_id}) - {e}")

    async def invite_from_dm_conversation(self, client, user_id: int, username: str, conversation_context: str, bot_username: str = None):
        """DM konuşmasından grup daveti"""
        # Konuşma bağlamına göre davet gönder
        success = await self.send_group_invite(client, user_id, username, conversation_context, bot_username)
        
        if success:
            # Başarılı davet sonrası takip mesajı planla
            asyncio.create_task(self.send_followup_message(client, user_id, username))
            
        return success

    async def mass_invite_from_groups(self, client, username: str, max_invites: int = 50):
        """Mevcut gruplardan toplu davet"""
        invited_count = 0
        
        try:
            # Mevcut grupları al
            dialogs = await client.get_dialogs()
            group_dialogs = [d for d in dialogs if d.is_group and d.id != self.target_group_id]
            
            log_event("group_invite", f"🔍 {len(group_dialogs)} grup bulundu, toplu davet başlıyor...")
            
            for dialog in group_dialogs:
                if invited_count >= max_invites:
                    break
                    
                try:
                    # Grup üyelerini al (son 100 mesaj)
                    messages = await client.get_messages(dialog.id, limit=100)
                    
                    # Aktif kullanıcıları topla
                    active_users = set()
                    for msg in messages:
                        if msg.sender_id and msg.sender_id != (await client.get_me()).id:
                            active_users.add(msg.sender_id)
                    
                    # Her gruptan maksimum 5 kişi davet et
                    group_invite_count = 0
                    for user_id in list(active_users)[:5]:
                        if invited_count >= max_invites or group_invite_count >= 5:
                            break
                            
                        try:
                            user = await client.get_entity(user_id)
                            user_name = user.username or user.first_name or f"user_{user_id}"
                            
                            # Davet gönder
                            success = await self.send_group_invite(client, user_id, user_name)
                            if success:
                                invited_count += 1
                                group_invite_count += 1
                                
                                # Rate limiting
                                await asyncio.sleep(random.uniform(10, 20))
                                
                        except Exception as e:
                            log_event("group_invite", f"⚠️ Kullanıcı davet hatası: {user_id} - {e}")
                            continue
                    
                    log_event("group_invite", f"📊 [{dialog.name}] grubundan {group_invite_count} davet gönderildi")
                    
                    # Gruplar arası bekleme
                    await asyncio.sleep(random.uniform(30, 60))
                    
                except Exception as e:
                    log_event("group_invite", f"⚠️ Grup işleme hatası [{dialog.name}]: {e}")
                    continue
            
            log_event("group_invite", f"✅ Toplu davet tamamlandı: {invited_count} davet gönderildi")
            
        except Exception as e:
            log_event("group_invite", f"❌ Toplu davet hatası: {e}")
        
        return invited_count

    async def smart_invite_strategy(self, client, username: str):
        """Akıllı davet stratejisi - farklı yöntemleri kombine eder"""
        log_event("group_invite", f"🧠 {username} için akıllı davet stratejisi başlatılıyor...")
        
        # Hedef grubu initialize et
        if not await self.initialize_group(client):
            return
        
        # Strateji 1: Mevcut gruplardan toplu davet (günde 1 kez)
        await self.mass_invite_from_groups(client, username, max_invites=30)
        
        # Strateji 2: DM konuşmalarında otomatik davet (sürekli aktif)
        # Bu DM handler'da implement edilecek
        
        # İstatistikleri logla
        log_event("group_invite", f"📊 Davet istatistikleri: {self.invite_stats}")
        log_analytics("group_invite", "strategy_completed", {
            "username": username,
            "stats": self.invite_stats
        })

    def get_stats(self) -> dict:
        """Davet istatistiklerini döndür"""
        return self.invite_stats.copy()

    def reset_stats(self):
        """İstatistikleri sıfırla"""
        self.invite_stats = {
            "total_invites": 0,
            "successful_invites": 0,
            "failed_invites": 0,
            "privacy_blocks": 0,
            "flood_waits": 0
        }

# Global instance
group_invite_strategy = GroupInviteStrategy()

async def start_group_invite_campaign(client, username: str):
    """Grup davet kampanyasını başlat"""
    log_event("group_invite", f"🚀 {username} için grup davet kampanyası başlatılıyor...")
    
    # Akıllı davet stratejisini çalıştır
    await group_invite_strategy.smart_invite_strategy(client, username)
    
    # Günlük tekrar için scheduler
    async def daily_invite_loop():
        while True:
            try:
                # 24 saat bekle
                await asyncio.sleep(86400)
                
                # Günlük davet kampanyası
                await group_invite_strategy.mass_invite_from_groups(client, username, max_invites=20)
                
                log_event("group_invite", f"🔄 {username} günlük davet kampanyası tamamlandı")
                
            except Exception as e:
                log_event("group_invite", f"❌ Günlük davet döngüsü hatası: {e}")
                await asyncio.sleep(3600)  # 1 saat bekle ve tekrar dene
    
    # Background task olarak başlat
    asyncio.create_task(daily_invite_loop())
    
    log_event("group_invite", f"✅ {username} grup davet sistemi aktif!") 