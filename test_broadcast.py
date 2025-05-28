#!/usr/bin/env python3
"""
GavatCore V2 Broadcast Test
"""

import asyncio
import sys
import os
sys.path.append('.')

async def test_broadcast():
    print('🧪 Broadcast test başlatılıyor...')
    
    try:
        from core.mcp_api_system import mcp_api
        from core.social_gaming_engine import social_gaming
        
        # MCP API başlat
        await mcp_api.initialize()
        print('✅ MCP API başlatıldı')
        
        # Social Gaming başlat
        await social_gaming.initialize()
        print('✅ Social Gaming başlatıldı')
        
        # Test kullanıcısı oluştur
        user_id = 'broadcast_test_user'
        result = await mcp_api.add_xp(user_id, 50, 'broadcast_test')
        print(f'✅ Test kullanıcısı: {result}')
        
        # Sosyal etkinlik oluştur (bu broadcast tetikleyecek)
        from core.social_gaming_engine import SocialEvent, EventType
        from datetime import datetime
        
        event = SocialEvent(
            event_id='broadcast_test_event',
            title='Broadcast Test Etkinliği 📢',
            description='Bu bir broadcast test etkinliğidir',
            event_type=EventType.VOICE_PARTY,
            host_character_id='geisha',
            max_participants=10
        )
        
        await social_gaming.create_social_event(event)
        print(f'✅ Test etkinliği oluşturuldu: {event.event_id}')
        
        # Leaderboard güncellemesi tetikle
        await social_gaming.update_leaderboards()
        print('✅ Leaderboard güncellendi')
        
        print('🎉 Broadcast test tamamlandı!')
        
    except Exception as e:
        print(f'❌ Test hatası: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_broadcast()) 