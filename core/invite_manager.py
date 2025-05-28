#!/usr/bin/env python3
# core/invite_manager.py - Merkezi Davet Yönetim Sistemi
"""
Grup davetlerini ve DM mesajlarını merkezi olarak yöneten sistem.
Çift gönderim, üyelik kontrolü ve spam önleme özelliklerini içerir.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Set
from utils.redis_client import get_state, set_state, check_cooldown, set_cooldown
from utils.log_utils import log_event
from core.analytics_logger import log_analytics

class InviteManager:
    """Merkezi davet yönetim sistemi"""
    
    def __init__(self):
        # Rate limiting ayarları
        self.DM_COOLDOWN_MINUTES = 60  # Aynı kullanıcıya 1 saat
        self.GROUP_INVITE_COOLDOWN_DAYS = 30  # Tekrar davet için 30 gün
        self.DAILY_DM_LIMIT = 50  # Günlük maksimum DM
        self.HOURLY_DM_LIMIT = 10  # Saatlik maksimum DM
        
        # Cache'ler
        self._group_members_cache = {}  # {group_id: Set[user_id]}
        self._cache_ttl = 3600  # 1 saat cache
        self._last_cache_update = {}
    
    async def check_group_membership(self, client, group_id: int, user_id: int) -> bool:
        """Kullanıcının grupta olup olmadığını kontrol et"""
        try:
            # Cache kontrolü
            cache_key = f"group_members:{group_id}"
            now = time.time()
            
            # Cache expired mı?
            if (group_id not in self._group_members_cache or 
                now - self._last_cache_update.get(group_id, 0) > self._cache_ttl):
                
                # Grup üyelerini güncelle
                await self._update_group_members_cache(client, group_id)
            
            # Cache'ten kontrol et
            return user_id in self._group_members_cache.get(group_id, set())
            
        except Exception as e:
            log_event("invite_manager", f"❌ Grup üyelik kontrolü hatası: {e}")
            return False
    
    async def _update_group_members_cache(self, client, group_id: int):
        """Grup üyeleri cache'ini güncelle"""
        try:
            members = set()
            async for user in client.iter_participants(group_id):
                members.add(user.id)
            
            self._group_members_cache[group_id] = members
            self._last_cache_update[group_id] = time.time()
            
            log_event("invite_manager", f"✅ Grup üyeleri güncellendi: {group_id} ({len(members)} üye)")
            
        except Exception as e:
            log_event("invite_manager", f"❌ Grup üyeleri güncelleme hatası: {e}")
    
    async def can_send_dm(self, bot_username: str, user_id: int) -> tuple[bool, str]:
        """DM gönderilip gönderilemeyeceğini kontrol et"""
        
        # 1. Son DM zamanını kontrol et
        last_dm_key = f"last_dm:{bot_username}:{user_id}"
        last_dm = await get_state(last_dm_key, "timestamp")
        
        if last_dm:
            time_since_last = time.time() - float(last_dm)
            cooldown_seconds = self.DM_COOLDOWN_MINUTES * 60
            
            if time_since_last < cooldown_seconds:
                remaining_minutes = (cooldown_seconds - time_since_last) / 60
                return False, f"DM cooldown: {remaining_minutes:.0f} dakika kaldı"
        
        # 2. Günlük limit kontrolü
        daily_key = f"daily_dm_count:{bot_username}:{datetime.now().date()}"
        daily_count = await get_state(daily_key, "count", default=0)
        
        if daily_count >= self.DAILY_DM_LIMIT:
            return False, f"Günlük DM limiti aşıldı: {self.DAILY_DM_LIMIT}"
        
        # 3. Saatlik limit kontrolü
        hourly_key = f"hourly_dm_count:{bot_username}:{datetime.now().hour}"
        hourly_count = await get_state(hourly_key, "count", default=0)
        
        if hourly_count >= self.HOURLY_DM_LIMIT:
            return False, f"Saatlik DM limiti aşıldı: {self.HOURLY_DM_LIMIT}"
        
        return True, "OK"
    
    async def record_dm_sent(self, bot_username: str, user_id: int):
        """DM gönderimini kaydet"""
        # Son DM zamanını kaydet
        last_dm_key = f"last_dm:{bot_username}:{user_id}"
        await set_state(last_dm_key, "timestamp", time.time(), expire_seconds=86400*30)  # 30 gün TTL
        
        # Günlük sayacı artır
        daily_key = f"daily_dm_count:{bot_username}:{datetime.now().date()}"
        daily_count = await get_state(daily_key, "count", default=0)
        await set_state(daily_key, "count", daily_count + 1, expire_seconds=86400)  # 1 gün TTL
        
        # Saatlik sayacı artır
        hourly_key = f"hourly_dm_count:{bot_username}:{datetime.now().hour}"
        hourly_count = await get_state(hourly_key, "count", default=0)
        await set_state(hourly_key, "count", hourly_count + 1, expire_seconds=3600)  # 1 saat TTL
        
        log_event(bot_username, f"📤 DM kaydedildi: {user_id}")
    
    async def can_send_group_invite(self, bot_username: str, user_id: int, group_id: int, client=None) -> tuple[bool, str]:
        """Grup daveti gönderilip gönderilemeyeceğini kontrol et"""
        
        # 1. Kullanıcı zaten grupta mı?
        if client:
            is_member = await self.check_group_membership(client, group_id, user_id)
            if is_member:
                return False, "Kullanıcı zaten grupta"
        
        # 2. Son davet zamanını kontrol et
        invite_key = f"group_invite:{bot_username}:{user_id}:{group_id}"
        last_invite = await get_state(invite_key, "timestamp")
        
        if last_invite:
            time_since_last = time.time() - float(last_invite)
            cooldown_seconds = self.GROUP_INVITE_COOLDOWN_DAYS * 86400
            
            if time_since_last < cooldown_seconds:
                remaining_days = (cooldown_seconds - time_since_last) / 86400
                return False, f"Grup daveti cooldown: {remaining_days:.0f} gün kaldı"
        
        # 3. Kullanıcı daveti reddetti mi?
        rejected_key = f"invite_rejected:{user_id}:{group_id}"
        rejected = await get_state(rejected_key, "rejected", default="false")
        
        if rejected == "true":
            return False, "Kullanıcı daveti daha önce reddetti"
        
        return True, "OK"
    
    async def record_group_invite(self, bot_username: str, user_id: int, group_id: int):
        """Grup davetini kaydet"""
        invite_key = f"group_invite:{bot_username}:{user_id}:{group_id}"
        await set_state(invite_key, "timestamp", time.time(), expire_seconds=86400*90)  # 90 gün TTL
        
        log_event(bot_username, f"📤 Grup daveti kaydedildi: {user_id} -> {group_id}")
    
    async def mark_invite_rejected(self, user_id: int, group_id: int):
        """Kullanıcı daveti reddetti olarak işaretle"""
        rejected_key = f"invite_rejected:{user_id}:{group_id}"
        await set_state(rejected_key, "rejected", "true", expire_seconds=86400*180)  # 6 ay TTL
        
        log_event("invite_manager", f"❌ Davet reddedildi: {user_id} -> {group_id}")
    
    async def get_dm_stats(self, bot_username: str) -> Dict:
        """Bot için DM istatistiklerini getir"""
        daily_key = f"daily_dm_count:{bot_username}:{datetime.now().date()}"
        hourly_key = f"hourly_dm_count:{bot_username}:{datetime.now().hour}"
        
        daily_count = await get_state(daily_key, "count", default=0)
        hourly_count = await get_state(hourly_key, "count", default=0)
        
        return {
            "daily_sent": daily_count,
            "daily_limit": self.DAILY_DM_LIMIT,
            "daily_remaining": max(0, self.DAILY_DM_LIMIT - daily_count),
            "hourly_sent": hourly_count,
            "hourly_limit": self.HOURLY_DM_LIMIT,
            "hourly_remaining": max(0, self.HOURLY_DM_LIMIT - hourly_count)
        }
    
    async def check_duplicate_message(self, bot_username: str, user_id: int, message_hash: str) -> bool:
        """Aynı mesajın daha önce gönderilip gönderilmediğini kontrol et"""
        dup_key = f"msg_dup:{bot_username}:{user_id}:{message_hash}"
        exists = await get_state(dup_key, "sent", default="false")
        
        if exists == "false" or not exists:
            # İlk kez gönderiliyor, kaydet
            await set_state(dup_key, "sent", "true", expire_seconds=3600)  # 1 saat TTL
            return False
        
        return True  # Duplicate mesaj

# Global instance
invite_manager = InviteManager() 