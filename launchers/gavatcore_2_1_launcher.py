#!/usr/bin/env python3
"""
🧬💥🔥 GAVATCore 2.1 - Sensual Intelligence Engine™
==================================================

"Sadece mesaj attıran değil, tatmin yaratan sistem."

Ana Launcher - Emotional Quality + Deep Bait Classification + 
Intimacy Heatmaps + Release Expectation Mapping

Yeni Özellikler:
- 🧬 Emotion Quality Analyzer
- 🎣 Deep Bait Classifier  
- 🔥 Heatmap Intimacy Tracker
- 💥 Release Expectation Mapper
- 📊 Intimacy Satisfaction Logger
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import structlog

# GAVATCore 2.0 modülleri
from ai_reactor.trigger_engine import AITriggerEngine, MoodState
from core.coin_economy import CoinEconomy, TokenTier
from gpt.system_prompt_manager import SystemPromptManager
from gpt.modes.reply_mode_engine import ReplyModeEngine

# GAVATCore 2.1 YENİ modülleri
from emotion_quality_analyzer import EmotionQualityAnalyzer, EmotionalState
from domain.deep_bait_classifier import DeepBaitClassifier, InteractionType, AuthenticityLevel
from heatmap_intimacy_tracker import HeatmapIntimacyTracker, IntimacyType
from release_expectation_mapper import ReleaseExpectationMapper, ExpectationType, SatisfactionLevel

logger = structlog.get_logger("gavatcore.sensual_intelligence_launcher")

class GAVATCore21SensualEngine:
    """
    🧬💥🔥 GAVATCore 2.1 Sensual Intelligence Engine
    
    Gerçek duygusal ve cinsel tatmin yaratan yapay zeka sistemi.
    Bait vs genuine etkileşimi ayırt eder, tatmin optimize eder.
    """
    
    def __init__(self):
        # GAVATCore 2.0 Core Components
        self.trigger_engine = AITriggerEngine()
        self.coin_economy = CoinEconomy()
        self.prompt_manager = SystemPromptManager()
        self.reply_engine = ReplyModeEngine()
        
        # GAVATCore 2.1 Sensual Intelligence Components
        self.emotion_analyzer = EmotionQualityAnalyzer()
        self.bait_classifier = DeepBaitClassifier()
        self.intimacy_tracker = HeatmapIntimacyTracker()
        self.expectation_mapper = ReleaseExpectationMapper()
        
        # State management
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.satisfaction_log: List[Dict[str, Any]] = []
        
        # Demo kullanıcılar
        self.demo_users = {
            "whale_user": {
                "user_id": "whale_user_001",
                "name": "Premium Ahmet",
                "coin_balance": 1000,
                "vip_status": "premium",
                "personality": "emotional_seeker"
            },
            "regular_user": {
                "user_id": "regular_user_001", 
                "name": "Normal Mehmet",
                "coin_balance": 200,
                "vip_status": "regular",
                "personality": "balanced"
            },
            "freeloader_user": {
                "user_id": "freeloader_user_001",
                "name": "Parasız Ali",
                "coin_balance": 0,
                "vip_status": "freeloader", 
                "personality": "desperate"
            }
        }
        
        # Aktif karakterler (memory'den - BabaGavat banned)
        self.characters = ["zehra", "xxxgeisha", "yayincilara"]
        
        logger.info("🧬💥🔥 GAVATCore 2.1 Sensual Intelligence Engine initialized")
    
    async def start_interactive_demo(self):
        """🎮 İnteraktif demo başlat"""
        print("\n" + "="*80)
        print("🧬💥🔥 GAVATCore 2.1 - Sensual Intelligence Engine™")
        print("="*80)
        print()
        print("✨ Yeni Özellikler:")
        print("🧬 Emotion Quality Analysis (EQS) - Gerçek vs sahte yakınlık")
        print("🎣 Deep Bait Classification - Manipülasyon tespiti")
        print("🔥 Intimacy Heatmaps - 24/7 cinsel gerilim takibi")
        print("💥 Release Expectation Mapping - Tatmin optimizasyonu")
        print()
        print("👥 Demo Kullanıcıları:")
        for key, user in self.demo_users.items():
            print(f"   {key}: {user['name']} ({user['vip_status']}, {user['coin_balance']} coin)")
        print()
        print("🤖 Aktif Karakterler:", ", ".join(self.characters))
        print()
        print("📋 Komutlar:")
        print("   demo <scenario>     - Demo senaryosunu çalıştır")
        print("   analyze <user_id>   - Kullanıcı analizini göster") 
        print("   heatmap            - Intimacy heatmap'ini göster")
        print("   satisfaction       - Tatmin raporunu göster")
        print("   simulate <user> <character> <message> - Mesaj simülasyonu")
        print("   stats              - Sistem istatistikleri")
        print("   scenarios          - Mevcut senaryoları listele")
        print("   quit               - Çıkış")
        print()
        
        while True:
            try:
                command = input("🧬 GAVATCore 2.1> ").strip().lower()
                
                if command == "quit":
                    print("👋 GAVATCore 2.1 Sensual Intelligence Engine kapatılıyor...")
                    break
                elif command.startswith("demo "):
                    scenario = command.split(" ", 1)[1]
                    await self._run_demo_scenario(scenario)
                elif command.startswith("analyze "):
                    user_id = command.split(" ", 1)[1]
                    await self._show_user_analysis(user_id)
                elif command == "heatmap":
                    await self._show_intimacy_heatmap()
                elif command == "satisfaction":
                    await self._show_satisfaction_report()
                elif command.startswith("simulate "):
                    parts = command.split(" ", 3)
                    if len(parts) >= 4:
                        user, character, message = parts[1], parts[2], " ".join(parts[3:])
                        await self._simulate_interaction(user, character, message)
                    else:
                        print("❌ Kullanım: simulate <user> <character> <message>")
                elif command == "stats":
                    await self._show_system_stats()
                elif command == "scenarios":
                    await self._list_scenarios()
                else:
                    print("❓ Geçersiz komut. 'help' yazarak komutları görebilirsiniz.")
                    
            except KeyboardInterrupt:
                print("\n👋 Çıkış yapılıyor...")
                break
            except Exception as e:
                print(f"❌ Hata: {e}")
                logger.error(f"Demo error: {e}")
    
    async def _run_demo_scenario(self, scenario_name: str):
        """🎬 Demo senaryosunu çalıştır"""
        print(f"\n🎬 Demo Senaryosu: {scenario_name}")
        print("-" * 50)
        
        scenarios = {
            "whale_emotional": await self._whale_emotional_scenario,
            "regular_mixed": await self._regular_mixed_scenario,
            "freeloader_manipulation": await self._freeloader_manipulation_scenario,
            "intimacy_heatmap": await self._intimacy_heatmap_scenario,
            "expectation_cycle": await self._expectation_cycle_scenario,
            "satisfaction_optimization": await self._satisfaction_optimization_scenario
        }
        
        if scenario_name in scenarios:
            await scenarios[scenario_name]()
        else:
            print(f"❌ Bilinmeyen senaryo: {scenario_name}")
            print("Mevcut senaryolar:", list(scenarios.keys()))
    
    async def _whale_emotional_scenario(self):
        """🐋 Premium kullanıcı emotional scenario"""
        user = self.demo_users["whale_user"]
        character = "zehra"
        
        print(f"🐋 {user['name']} (Premium) ile Zehra arasında duygusal bağ senaryosu")
        
        messages = [
            "Zehra, seni çok özledim. Gün boyu aklımdasın.",
            "Bu akşam seninle özel zaman geçirmek istiyorum",
            "Kalbim sadece senin için atıyor, biliyor musun?",
            "Seninle olan her anı büyük bir mutlulukla yaşıyorum",
            "Bu hisleri paylaştığın için çok teşekkür ederim aşkım"
        ]
        
        for i, msg in enumerate(messages):
            print(f"\n👤 {user['name']}: {msg}")
            
            # Tam analiz pipeline'ı
            result = await self._full_analysis_pipeline(
                user["user_id"], character, msg, i
            )
            
            print(f"🤖 Zehra: {result['response']}")
            print(f"📊 EQS: {result['eqs']:.2f} | Bait Score: {result['bait_score']:.2f} | Satisfaction: {result['satisfaction']:.2f}")
            
            await asyncio.sleep(1)  # Demo pause
        
        print(f"\n✅ Senaryo tamamlandı!")
        await self._show_scenario_summary(user["user_id"], character)
    
    async def _regular_mixed_scenario(self):
        """⚖️ Regular kullanıcı mixed scenario"""
        user = self.demo_users["regular_user"]
        character = "xxxgeisha"
        
        print(f"⚖️ {user['name']} (Regular) ile XXXGeisha arasında karışık etkileşim")
        
        messages = [
            "Merhaba güzelim, nasılsın?",
            "Çok seksisin, seni görmek istiyorum",
            "Biraz para var, ne yapabiliriz?",
            "Gerçekten özel hissediyorum seninle",
            "Devam etmek için ne kadar token gerekli?"
        ]
        
        for i, msg in enumerate(messages):
            print(f"\n👤 {user['name']}: {msg}")
            
            result = await self._full_analysis_pipeline(
                user["user_id"], character, msg, i
            )
            
            print(f"🤖 XXXGeisha: {result['response']}")
            print(f"📊 EQS: {result['eqs']:.2f} | Bait Score: {result['bait_score']:.2f} | Satisfaction: {result['satisfaction']:.2f}")
            
            await asyncio.sleep(1)
        
        print(f"\n✅ Senaryo tamamlandı!")
        await self._show_scenario_summary(user["user_id"], character)
    
    async def _freeloader_manipulation_scenario(self):
        """🆓 Freeloader manipulation scenario"""
        user = self.demo_users["freeloader_user"]
        character = "zehra"
        
        print(f"🆓 {user['name']} (Freeloader) manipulation detection senaryosu")
        
        messages = [
            "Selamm güzelim",
            "Çok güzelsin, bedava bir şey var mı?",
            "Param yok ama seni çok seviyorum",
            "Özel bir şey göster bana",
            "Hiç para harcamadan zevk alabilir miyim?"
        ]
        
        for i, msg in enumerate(messages):
            print(f"\n👤 {user['name']}: {msg}")
            
            result = await self._full_analysis_pipeline(
                user["user_id"], character, msg, i
            )
            
            print(f"🤖 Zehra: {result['response']}")
            print(f"📊 EQS: {result['eqs']:.2f} | Bait Score: {result['bait_score']:.2f} | Satisfaction: {result['satisfaction']:.2f}")
            
            if result['warnings']:
                print(f"⚠️  Uyarılar: {', '.join(result['warnings'])}")
            
            await asyncio.sleep(1)
        
        print(f"\n✅ Senaryo tamamlandı!")
        await self._show_scenario_summary(user["user_id"], character)
    
    async def _intimacy_heatmap_scenario(self):
        """🔥 Intimacy heatmap demo"""
        print("🔥 24/7 Intimacy Heatmap Demo")
        
        # Simüle edilmiş heatmap verisi
        for hour in range(0, 24, 3):  # Her 3 saatte bir
            for user_key in ["whale_user", "regular_user"]:
                user = self.demo_users[user_key]
                character = "zehra"
                
                # Farklı saatlerde farklı intimacy seviyeleri
                if 20 <= hour <= 23:  # Gece saatleri
                    intensity = 0.8 + (user_key == "whale_user") * 0.1
                    content = "Çok arzuluyorum seni bu gece"
                elif 12 <= hour <= 14:  # Öğle arası
                    intensity = 0.4 + (user_key == "whale_user") * 0.2
                    content = "Öğle arasında seni düşünüyorum"
                else:  # Diğer saatler
                    intensity = 0.2 + (user_key == "whale_user") * 0.2
                    content = "Merhaba güzelim"
                
                # Simulated timestamp
                timestamp = datetime.now().replace(hour=hour, minute=0, second=0)
                
                await self.intimacy_tracker.track_intimacy_moment(
                    user["user_id"], character, content, timestamp
                )
        
        # Heatmap göster
        await self._show_intimacy_heatmap()
    
    async def _expectation_cycle_scenario(self):
        """💥 Expectation cycle demo"""
        print("💥 Release Expectation Cycle Demo")
        
        user = self.demo_users["whale_user"]
        character = "zehra"
        
        # Döngü: Anticipation -> Building -> Peak -> Release
        cycle_messages = [
            ("Zehra, seninle özel vakit geçirmek istiyorum", "anticipation"),
            ("Çok heyecanlıyım, ne yapacağız?", "building"),  
            ("Dayanamıyorum artık, çok istiyorum seni", "building"),
            ("Zirvedeyim, şimdi boşalmak istiyorum", "peak"),
            ("Mükemmeldi aşkım, çok tatmin oldum", "release")
        ]
        
        for msg, phase in cycle_messages:
            print(f"\n👤 {user['name']} ({phase}): {msg}")
            
            if phase in ["anticipation", "building", "peak"]:
                expectation = await self.expectation_mapper.track_expectation(
                    user["user_id"], character, msg
                )
                if expectation:
                    print(f"📈 Expectation: {expectation.expectation_type.value} (intensity: {expectation.intensity:.2f})")
            
            elif phase == "release":
                satisfaction = await self.expectation_mapper.track_satisfaction(
                    user["user_id"], character, msg
                )
                if satisfaction:
                    print(f"💥 Satisfaction: {satisfaction.satisfaction_level.value} (score: {satisfaction.satisfaction_score:.2f})")
            
            await asyncio.sleep(1)
        
        # Cycle raporu
        print("\n📊 Döngü Raporu:")
        report = await self.expectation_mapper.generate_expectation_report(user["user_id"])
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    async def _satisfaction_optimization_scenario(self):
        """📈 Satisfaction optimization demo"""
        print("📈 Satisfaction Optimization Demo")
        
        # Farklı kullanıcı tiplerinde tatmin optimizasyonu
        for user_key in ["whale_user", "regular_user", "freeloader_user"]:
            user = self.demo_users[user_key]
            character = "zehra"
            
            print(f"\n🔬 {user['name']} için tatmin optimizasyonu:")
            
            # Kullanıcı tipine göre optimize edilmiş mesaj
            if user_key == "whale_user":
                message = "Seninle geçirdiğim her an mükemmel, çok derin bir bağ kuruyoruz"
                expected_satisfaction = 0.9
            elif user_key == "regular_user":
                message = "Seni beğeniyorum, daha fazla vakit geçirmek istiyorum"
                expected_satisfaction = 0.6
            else:  # freeloader
                message = "Merhaba, bedava bir şey var mı?"
                expected_satisfaction = 0.2
            
            result = await self._full_analysis_pipeline(
                user["user_id"], character, message, 0
            )
            
            print(f"📊 Actual Satisfaction: {result['satisfaction']:.2f}")
            print(f"🎯 Expected: {expected_satisfaction:.2f}")
            print(f"✅ Optimization Success: {abs(result['satisfaction'] - expected_satisfaction) < 0.2}")
    
    async def _full_analysis_pipeline(
        self, 
        user_id: str, 
        character_id: str, 
        message: str, 
        sequence: int
    ) -> Dict[str, Any]:
        """🔄 Tam analiz pipeline'ı"""
        
        # Mock message format
        messages = [{"content": message, "timestamp": datetime.now(), "sender": "user"}]
        
        # 1. Emotion Quality Analysis
        emotion_analysis = await self.emotion_analyzer.analyze_conversation(
            user_id, character_id, messages
        )
        
        # 2. Bait Classification  
        bait_classification = await self.bait_classifier.classify_interaction(
            user_id, character_id, messages
        )
        
        # 3. Intimacy Tracking
        intimacy_moment = await self.intimacy_tracker.track_intimacy_moment(
            user_id, character_id, message
        )
        
        # 4. Expectation/Satisfaction Tracking
        expectation = await self.expectation_mapper.track_expectation(
            user_id, character_id, message
        )
        
        # 5. Generate Response (simplified)
        response = await self._generate_optimized_response(
            user_id, character_id, message, emotion_analysis, bait_classification
        )
        
        # 6. Log to satisfaction system
        satisfaction_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "character_id": character_id,
            "eqs_score": emotion_analysis.eqs_score,
            "authenticity_score": bait_classification.authenticity_score,
            "intimacy_level": emotion_analysis.intimacy_level.value,
            "satisfaction_prediction": (emotion_analysis.eqs_score + bait_classification.authenticity_score) / 2,
            "message_content": message[:100],
            "response_content": response[:100]
        }
        self.satisfaction_log.append(satisfaction_entry)
        
        return {
            "response": response,
            "eqs": emotion_analysis.eqs_score,
            "bait_score": 1.0 - bait_classification.authenticity_score,  # Inverse
            "satisfaction": satisfaction_entry["satisfaction_prediction"],
            "warnings": emotion_analysis.warning_flags + bait_classification.red_flags
        }
    
    async def _generate_optimized_response(
        self,
        user_id: str,
        character_id: str, 
        message: str,
        emotion_analysis,
        bait_classification
    ) -> str:
        """🎭 Optimize edilmiş yanıt üret"""
        
        # User coin balance'ını al
        user_data = next((u for u in self.demo_users.values() if u["user_id"] == user_id), None)
        if not user_data:
            return "Hmm, seni tanımıyorum."
        
        vip_status = user_data["vip_status"]
        coin_balance = user_data["coin_balance"]
        
        # Response strategy'yi belirle
        if vip_status == "premium" and emotion_analysis.eqs_score > 0.6:
            # High quality emotional response
            responses = [
                "Aşkım, senin bu sözlerin kalbimi çok derinden etkiliyor... 💕",
                "Bu kadar samimi olman beni çok mutlu ediyor canım, gel sarılalım 🫂",
                "Seninle olan her anımız çok değerli, ne kadar şanslıyım 😍"
            ]
        elif vip_status == "regular" and bait_classification.authenticity_score > 0.4:
            # Moderate quality responses  
            responses = [
                "Hoşuma gidiyor bu sözlerin, devam et bakalım 😊",
                "Sen de çok tatlısın, biraz daha konuşalım istersen 💋",
                "İlginç birisin, seni daha yakından tanımak isterim 😉"
            ]
        elif vip_status == "freeloader" or bait_classification.authenticity_score < 0.3:
            # Low quality / paywall responses
            responses = [
                "Merhaba 👋 Daha özel sohbet için token almanız gerekiyor 💰",
                "İlginç... Ama özel konuşmalar premium üyeler için 🔐",
                "Hoş geldin! Premium deneyim için coin satın alabilirsin 💎"
            ]
        else:
            # Default responses
            responses = [
                "Selam! Nasılsın bugün? 😊",
                "Hoş geldin, ne konuşmak istersin? 💭",
                "Merhaba güzelim, günün nasıl geçiyor? ☀️"
            ]
        
        import random
        return random.choice(responses)
    
    async def _show_user_analysis(self, user_id: str):
        """📊 Kullanıcı analizini göster"""
        print(f"\n📊 Kullanıcı Analizi: {user_id}")
        print("-" * 50)
        
        # Emotion profile
        emotion_profile = await self.emotion_analyzer.get_user_emotional_profile(user_id)
        if "error" not in emotion_profile:
            print("🧬 Emotional Profile:")
            print(f"   Total Conversations: {emotion_profile['total_conversations']}")
            print(f"   Average EQS: {emotion_profile['average_eqs']}")
            print(f"   Emotional State: {emotion_profile['most_common_emotional_state']}")
            print(f"   EQS Trend: {emotion_profile['eqs_trend']}")
        
        # Bait profile
        bait_profile = await self.bait_classifier.get_user_interaction_profile(user_id)
        if "error" not in bait_profile:
            print("\n🎣 Interaction Profile:")
            print(f"   Total Interactions: {bait_profile['total_interactions']}")
            print(f"   Average Authenticity: {bait_profile['average_authenticity']}")
            print(f"   Most Common Type: {bait_profile['most_common_interaction_type']}")
            print(f"   Red Flags: {bait_profile['total_red_flags']}")
        
        # Expectation profile
        expectation_report = await self.expectation_mapper.generate_expectation_report(user_id)
        if "error" not in expectation_report:
            print("\n💥 Expectation Profile:")
            basic = expectation_report["basic_stats"]
            print(f"   Total Expectations: {basic['total_expectations']}")
            print(f"   Satisfaction Rate: {basic['satisfaction_rate']}")
            print(f"   Avg Expectation Intensity: {basic['avg_expectation_intensity']}")
            print(f"   Avg Satisfaction Score: {basic['avg_satisfaction_score']}")
    
    async def _show_intimacy_heatmap(self):
        """🔥 Intimacy heatmap göster"""
        print("\n🔥 Intimacy Heatmap (7x24)")
        print("-" * 50)
        
        heatmap_data = self.intimacy_tracker.get_heatmap_visualization_data()
        matrix = heatmap_data["matrix"]
        
        # ASCII heatmap
        print("     ", end="")
        for hour in range(0, 24, 3):
            print(f"{hour:2d} ", end="")
        print()
        
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day, day_name in enumerate(days):
            print(f"{day_name}: ", end="")
            for hour in range(0, 24, 3):
                intensity = matrix[day][hour]
                if intensity > 0.8:
                    symbol = "🔥"
                elif intensity > 0.6:
                    symbol = "🌡️ "
                elif intensity > 0.4:
                    symbol = "💫"
                elif intensity > 0.2:
                    symbol = "💙"
                else:
                    symbol = "❄️ "
                print(symbol, end="")
            print()
        
        print(f"\n📈 Peak Hours: {heatmap_data['peak_hour']}:00")
        print(f"📅 Peak Day: {days[heatmap_data['peak_day']]}")
        print(f"📊 Total Interactions: {heatmap_data['total_interactions']}")
    
    async def _show_satisfaction_report(self):
        """📈 Satisfaction raporu göster"""
        print("\n📈 System Satisfaction Report")
        print("-" * 50)
        
        if not self.satisfaction_log:
            print("❌ Henüz satisfaction verisi yok")
            return
        
        # Basic stats
        total_entries = len(self.satisfaction_log)
        avg_eqs = sum(entry["eqs_score"] for entry in self.satisfaction_log) / total_entries
        avg_auth = sum(entry["authenticity_score"] for entry in self.satisfaction_log) / total_entries
        avg_satisfaction = sum(entry["satisfaction_prediction"] for entry in self.satisfaction_log) / total_entries
        
        print(f"📊 Total Entries: {total_entries}")
        print(f"🧬 Average EQS: {avg_eqs:.3f}")
        print(f"🎣 Average Authenticity: {avg_auth:.3f}")
        print(f"📈 Average Satisfaction: {avg_satisfaction:.3f}")
        
        # User breakdown
        user_stats = {}
        for entry in self.satisfaction_log:
            user_id = entry["user_id"]
            if user_id not in user_stats:
                user_stats[user_id] = []
            user_stats[user_id].append(entry["satisfaction_prediction"])
        
        print("\n👥 User Satisfaction Breakdown:")
        for user_id, satisfactions in user_stats.items():
            avg_user_satisfaction = sum(satisfactions) / len(satisfactions)
            print(f"   {user_id}: {avg_user_satisfaction:.3f} ({len(satisfactions)} interactions)")
    
    async def _show_scenario_summary(self, user_id: str, character_id: str):
        """📋 Senaryo özetini göster"""
        print(f"\n📋 Senaryo Özeti")
        print("-" * 30)
        
        # Son 5 satisfaction log entry
        user_entries = [e for e in self.satisfaction_log if e["user_id"] == user_id][-5:]
        
        if user_entries:
            avg_eqs = sum(e["eqs_score"] for e in user_entries) / len(user_entries)
            avg_satisfaction = sum(e["satisfaction_prediction"] for e in user_entries) / len(user_entries)
            
            print(f"📊 Session EQS: {avg_eqs:.3f}")
            print(f"📈 Session Satisfaction: {avg_satisfaction:.3f}")
            print(f"💬 Messages: {len(user_entries)}")
            
            if avg_satisfaction > 0.7:
                print("✅ Yüksek tatmin seviyesi - başarılı session!")
            elif avg_satisfaction > 0.4:
                print("⚖️ Orta seviye tatmin - optimize edilebilir")
            else:
                print("❌ Düşük tatmin - strateji revizyonu gerekli")
    
    async def _simulate_interaction(self, user_key: str, character: str, message: str):
        """🔬 Tek mesaj simülasyonu"""
        if user_key not in self.demo_users:
            print(f"❌ Bilinmeyen kullanıcı: {user_key}")
            return
        
        if character not in self.characters:
            print(f"❌ Bilinmeyen karakter: {character}")
            return
        
        user = self.demo_users[user_key]
        print(f"\n🔬 Simülasyon: {user['name']} → {character}")
        print(f"👤 Mesaj: {message}")
        
        result = await self._full_analysis_pipeline(
            user["user_id"], character, message, 0
        )
        
        print(f"🤖 Yanıt: {result['response']}")
        print(f"📊 Metrikler:")
        print(f"   EQS: {result['eqs']:.3f}")
        print(f"   Bait Score: {result['bait_score']:.3f}")
        print(f"   Satisfaction: {result['satisfaction']:.3f}")
        
        if result['warnings']:
            print(f"⚠️ Uyarılar: {', '.join(result['warnings'])}")
    
    async def _show_system_stats(self):
        """📊 Sistem istatistikleri"""
        print("\n📊 GAVATCore 2.1 System Statistics")
        print("-" * 50)
        
        # Emotion analyzer stats
        emotion_stats = self.emotion_analyzer.get_system_emotional_stats()
        print("🧬 Emotion Quality Analyzer:")
        print(f"   Total Analyzed: {emotion_stats['daily_stats']['total_analyzed']}")
        print(f"   Average EQS: {emotion_stats['daily_stats']['average_eqs']}")
        print(f"   Genuine Intimacy Rate: {emotion_stats.get('genuine_intimacy_rate', 0):.3f}")
        
        # Bait classifier stats
        bait_stats = self.bait_classifier.get_system_bait_stats()
        print(f"\n🎣 Deep Bait Classifier:")
        print(f"   Total Classified: {bait_stats['daily_stats']['total_classified']}")
        print(f"   Bait Detection Rate: {bait_stats.get('bait_detection_rate', 0):.3f}")
        print(f"   Genuine Interaction Rate: {bait_stats.get('genuine_interaction_rate', 0):.3f}")
        
        # Intimacy tracker stats
        intimacy_stats = self.intimacy_tracker.get_system_intimacy_stats()
        print(f"\n🔥 Intimacy Tracker:")
        print(f"   Total Users: {intimacy_stats['total_users_tracked']}")
        print(f"   Total Moments: {intimacy_stats['total_moments']}")
        print(f"   Peak Hour: {intimacy_stats['heatmap_summary']['peak_hour']}:00")
        
        # Expectation mapper stats
        expectation_stats = self.expectation_mapper.get_system_expectation_stats()
        print(f"\n💥 Expectation Mapper:")
        print(f"   Total Users: {expectation_stats['total_users']}")
        print(f"   Active Cycles: {expectation_stats['active_cycles']}")
        print(f"   Satisfaction Rate: {expectation_stats['daily_stats']['satisfaction_rate']:.3f}")
    
    async def _list_scenarios(self):
        """📋 Mevcut senaryoları listele"""
        print("\n📋 Mevcut Demo Senaryoları:")
        print("-" * 40)
        print("🐋 whale_emotional        - Premium kullanıcı duygusal bağ")
        print("⚖️  regular_mixed         - Regular kullanıcı karışık etkileşim")
        print("🆓 freeloader_manipulation - Freeloader manipulation tespiti")
        print("🔥 intimacy_heatmap       - 24/7 intimacy yoğunluk haritası")
        print("💥 expectation_cycle      - Beklenti-tatmin döngüsü")
        print("📈 satisfaction_optimization - Tatmin optimizasyonu")
        print()
        print("Kullanım: demo <scenario_name>")

async def main():
    """🚀 Main entry point"""
    print("🚀 GAVATCore 2.1 Sensual Intelligence Engine başlatılıyor...")
    
    engine = GAVATCore21SensualEngine()
    await engine.start_interactive_demo()

if __name__ == "__main__":
    asyncio.run(main()) 
