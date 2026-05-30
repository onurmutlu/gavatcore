from infrastructure.config.logger import get_logger

#!/usr/bin/env python3
"""
SEFERVERSE AI PIPELINE v2.0 - GPT-4 Powered
===========================================

Otomatik AI content generation ve scheduling sistemi.
Günde 12 post, 4 kategori, akıllı zamanlama.

Özellikler:
- GPT-4 ile quality content
- Smart scheduling (peak hours)
- Analytics tracking  
- Multi-platform sharing
- Auto hashtag generation
- Engagement optimization
"""

import asyncio
import json
import os
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List
import structlog

# AI Generator import
from core.ai_content_generator import ai_content_generator

logger = structlog.get_logger("seferverse_ai_pipeline")

class SeferVerseAIPipeline:
    """SeferVerse AI Pipeline - Akıllı içerik üretim sistemi"""
    
    def __init__(self):
        self.is_running = False
        self.daily_posts_target = 12
        self.content_distribution = {
            "motivation": 4,  # En popüler
            "lifestyle": 3,
            "tech": 3, 
            "business": 2
        }
        
        # Peak hours for posting (Turkish time)
        self.peak_hours = [9, 12, 15, 18, 20, 22]
        
        # Storage paths
        self.generated_content_dir = "data/seferverse_content"
        self.analytics_dir = "data/analytics"
        
        # Ensure directories exist
        os.makedirs(self.generated_content_dir, exist_ok=True)
        os.makedirs(self.analytics_dir, exist_ok=True)
        
        self.daily_stats = {
            "posts_generated": 0,
            "posts_published": 0,
            "engagement_total": 0,
            "categories": {},
            "start_time": None
        }
    
    async def initialize(self):
        """Pipeline'ı başlat"""
        try:
            logger.info("🚀 SeferVerse AI Pipeline başlatılıyor...")
            
            # AI Content Generator'ı başlat
            await ai_content_generator.initialize()
            
            # Schedule jobs
            self._setup_scheduling()
            
            self.is_running = True
            logger.info("✅ SeferVerse AI Pipeline hazır!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline başlatma hatası: {e}")
            return False
    
    def _setup_scheduling(self):
        """Daily scheduling setup"""
        # Peak hours'da post scheduling
        for hour in self.peak_hours:
            schedule.every().day.at(f"{hour:02d}:00").do(self._scheduled_post_generation)
        
        # Daily analytics
        schedule.every().day.at("23:30").do(self._daily_analytics_report)
        
        # Weekly batch generation
        schedule.every().sunday.at("00:00").do(self._weekly_content_batch)
        
        logger.info(f"📅 Zamanlama kuruldu: {len(self.peak_hours)} daily slots")
    
    async def generate_daily_content(self) -> Dict:
        """Günlük içerik package'ı üret"""
        try:
            start_time = datetime.now()
            self.daily_stats["start_time"] = start_time.isoformat()
            
            logger.info(f"🎯 Günlük içerik üretimi başlıyor: {self.daily_posts_target} post")
            
            # Batch content generation
            posts = await ai_content_generator.generate_batch_content(
                count=self.daily_posts_target,
                distribution=self.content_distribution
            )
            
            if not posts:
                logger.error("❌ İçerik üretilemedi!")
                return None
            
            # Timing optimization
            scheduled_posts = self._optimize_posting_schedule(posts)
            
            # Save to files
            daily_package = {
                "date": start_time.strftime("%Y-%m-%d"),
                "total_posts": len(posts),
                "categories": self._analyze_categories(posts),
                "scheduled_posts": scheduled_posts,
                "generated_at": start_time.isoformat(),
                "estimated_engagement": self._calculate_total_engagement(posts),
                "posts": posts
            }
            
            # Save daily package
            filename = f"{self.generated_content_dir}/daily_{start_time.strftime('%Y%m%d')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(daily_package, f, ensure_ascii=False, indent=2)
            
            # Update stats
            self.daily_stats["posts_generated"] = len(posts)
            self.daily_stats["categories"] = self._analyze_categories(posts)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"""
✅ GÜNLÜK İÇERİK PACKAGE HAZIR!

📊 İstatistikler:
   🎯 Üretilen: {len(posts)} post
   ⏱️ Süre: {duration:.1f} saniye
   📈 Engagement tahmini: {daily_package['estimated_engagement']:.1f}%
   📁 Dosya: {filename}

📅 Kategori Dağılımı:
{self._format_category_stats(self.daily_stats['categories'])}
            """)
            
            return daily_package
            
        except Exception as e:
            logger.error(f"❌ Günlük içerik üretim hatası: {e}")
            return None
    
    def _optimize_posting_schedule(self, posts: List[Dict]) -> List[Dict]:
        """Postları peak hours'a optimize ederek dağıt"""
        scheduled = []
        
        # Posts'u engagement score'a göre sırala
        sorted_posts = sorted(posts, 
                            key=lambda x: x.get('engagement_prediction', {}).get('score', 0), 
                            reverse=True)
        
        # Peak hours'a en iyi postları yerleştir
        for i, post in enumerate(sorted_posts):
            if i < len(self.peak_hours):
                hour = self.peak_hours[i]
                post_time = datetime.now().replace(hour=hour, minute=0, second=0)
            else:
                # Remaining posts'u off-peak hours'a dağıt
                off_peak = [h for h in range(8, 24) if h not in self.peak_hours]
                hour = off_peak[i % len(off_peak)]
                post_time = datetime.now().replace(hour=hour, minute=30, second=0)
            
            scheduled_post = {
                **post,
                "scheduled_time": post_time.isoformat(),
                "priority": "peak" if i < len(self.peak_hours) else "normal",
                "slot_index": i
            }
            
            scheduled.append(scheduled_post)
        
        return scheduled
    
    def _analyze_categories(self, posts: List[Dict]) -> Dict:
        """Post kategori analizi"""
        categories = {}
        for post in posts:
            cat = post.get('category', 'unknown')
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        return categories
    
    def _calculate_total_engagement(self, posts: List[Dict]) -> float:
        """Toplam engagement tahmini"""
        total_score = sum(post.get('engagement_prediction', {}).get('score', 0) for post in posts)
        return total_score / len(posts) if posts else 0
    
    def _format_category_stats(self, categories: Dict) -> str:
        """Kategori istatistiklerini formatla"""
        lines = []
        for cat, count in categories.items():
            lines.append(f"   • {cat.title()}: {count} post")
        return "\n".join(lines)
    
    async def publish_scheduled_posts(self):
        """Zamanlanmış postları yayınla"""
        try:
            # Bugünün dosyasını oku
            today = datetime.now().strftime("%Y%m%d")
            filename = f"{self.generated_content_dir}/daily_{today}.json"
            
            if not os.path.exists(filename):
                logger.warning(f"⚠️ Bugünün içerik dosyası bulunamadı: {filename}")
                return
            
            with open(filename, 'r', encoding='utf-8') as f:
                daily_package = json.load(f)
            
            current_time = datetime.now()
            published_count = 0
            
            for post in daily_package.get('scheduled_posts', []):
                scheduled_time = datetime.fromisoformat(post['scheduled_time'])
                
                # Zamanı gelmiş postları yayınla
                if scheduled_time <= current_time:
                    success = await self._publish_post(post)
                    if success:
                        published_count += 1
                        post['published'] = True
                        post['published_at'] = current_time.isoformat()
            
            # Güncellenmis package'ı kaydet
            if published_count > 0:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(daily_package, f, ensure_ascii=False, indent=2)
                
                self.daily_stats["posts_published"] += published_count
                logger.info(f"📤 {published_count} post yayınlandı")
            
        except Exception as e:
            logger.error(f"❌ Post yayınlama hatası: {e}")
    
    async def _publish_post(self, post: Dict) -> bool:
        """Tek post yayınla (implement platform-specific logic)"""
        try:
            # Telegram channel'a gönder
            success_telegram = await self._post_to_telegram(post)
            
            # Instagram'a gönder (future implementation)
            # success_instagram = await self._post_to_instagram(post)
            
            # Analytics kaydet
            await self._log_post_analytics(post, success_telegram)
            
            return success_telegram
            
        except Exception as e:
            logger.error(f"❌ Post publish error: {e}")
            return False
    
    async def _post_to_telegram(self, post: Dict) -> bool:
        """Telegram channel'a post gönder"""
        try:
            # Bu kısım telegram bot entegrasyonu ile implement edilecek
            # Şimdilik simulation
            
            content = post['content']
            hashtags = " ".join(post.get('hashtags', []))
            full_message = f"{content}\n\n{hashtags}"
            
            logger.info(f"📤 Telegram post simulated: {post['id']}")
            logger.debug(f"Content preview: {content[:100]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Telegram post error: {e}")
            return False
    
    async def _log_post_analytics(self, post: Dict, success: bool):
        """Post analytics kaydet"""
        try:
            analytics_data = {
                "post_id": post['id'],
                "published_at": datetime.now().isoformat(),
                "success": success,
                "category": post.get('category'),
                "engagement_prediction": post.get('engagement_prediction'),
                "word_count": post.get('metadata', {}).get('word_count', 0),
                "hashtags_count": len(post.get('hashtags', [])),
                "platform": "telegram"
            }
            
            # Daily analytics file
            date_str = datetime.now().strftime("%Y%m%d")
            analytics_file = f"{self.analytics_dir}/daily_analytics_{date_str}.json"
            
            # Load existing analytics
            if os.path.exists(analytics_file):
                with open(analytics_file, 'r', encoding='utf-8') as f:
                    daily_analytics = json.load(f)
            else:
                daily_analytics = {"posts": []}
            
            # Add new post
            daily_analytics["posts"].append(analytics_data)
            
            # Save updated analytics
            with open(analytics_file, 'w', encoding='utf-8') as f:
                json.dump(daily_analytics, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"❌ Analytics logging error: {e}")
    
    def _scheduled_post_generation(self):
        """Scheduled job for post generation"""
        asyncio.run(self.publish_scheduled_posts())
    
    def _daily_analytics_report(self):
        """Daily analytics raporu"""
        try:
            today = datetime.now().strftime("%Y%m%d")
            analytics_file = f"{self.analytics_dir}/daily_analytics_{today}.json"
            
            if os.path.exists(analytics_file):
                with open(analytics_file, 'r', encoding='utf-8') as f:
                    analytics = json.load(f)
                
                total_posts = len(analytics.get('posts', []))
                successful_posts = sum(1 for p in analytics['posts'] if p.get('success'))
                
                logger.info(f"""
📊 GÜNLÜK ANALYTİCS RAPORU ({today})

✅ Başarılı: {successful_posts}/{total_posts}
📈 Başarı oranı: {(successful_posts/total_posts)*100:.1f}%
                """)
                
        except Exception as e:
            logger.error(f"❌ Analytics report error: {e}")
    
    def _weekly_content_batch(self):
        """Weekly batch content generation"""
        asyncio.run(self._generate_weekly_batch())
    
    async def _generate_weekly_batch(self):
        """Haftalık batch content üret"""
        try:
            logger.info("📅 Haftalık batch content üretimi başlıyor...")
            
            # 7 günlük content package
            weekly_posts = []
            for day in range(7):
                daily_posts = await ai_content_generator.generate_batch_content(
                    count=self.daily_posts_target,
                    distribution=self.content_distribution
                )
                
                if daily_posts:
                    weekly_posts.extend(daily_posts)
                
                # Rate limiting
                await asyncio.sleep(2)
            
            # Save weekly package
            week_start = datetime.now()
            filename = f"{self.generated_content_dir}/weekly_{week_start.strftime('%Y%W')}.json"
            
            weekly_package = {
                "week_start": week_start.isoformat(),
                "total_posts": len(weekly_posts),
                "daily_target": self.daily_posts_target,
                "posts": weekly_posts
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(weekly_package, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Haftalık batch hazır: {len(weekly_posts)} post - {filename}")
            
        except Exception as e:
            logger.error(f"❌ Weekly batch error: {e}")
    
    async def run_pipeline(self):
        """Ana pipeline loop"""
        try:
            await self.initialize()
            
            logger.info("🚀 SeferVerse AI Pipeline çalışıyor...")
            
            # İlk günlük content üret
            await self.generate_daily_content()
            
            # Scheduling loop
            while self.is_running:
                schedule.run_pending()
                await asyncio.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("⏹️ Pipeline durduruldu")
        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
        finally:
            self.is_running = False


# Test & Demo functions
async def test_ai_pipeline():
    """AI Pipeline test fonksiyonu"""
    pipeline = SeferVerseAIPipeline()
    
    # Single post test
    print("🧪 Test: Single post generation")
    single_post = await ai_content_generator.generate_seferverse_post(
        category="motivation",
        theme="başarı"
    )
    
    if single_post:
        print(f"✅ Test post generated: {single_post['id']}")
        print(f"📝 Content preview: {single_post['content'][:100]}...")
        print(f"📊 Engagement: {single_post['engagement_prediction']['score']}")
    
    # Daily content test
    print("\n🧪 Test: Daily content package")
    daily_package = await pipeline.generate_daily_content()
    
    if daily_package:
        print(f"✅ Daily package: {daily_package['total_posts']} posts")
        print(f"📈 Avg engagement: {daily_package['estimated_engagement']:.1f}")


async def demo_ai_generation():
    """AI Generation demo"""
    print("""
🤖 SEFERVERSE AI DEMO
====================
GPT-4 ile otomatik içerik üretimi
""")
    
    # AI generator'ı başlat
    await ai_content_generator.initialize()
    
    categories = ["motivation", "tech", "lifestyle", "business"]
    
    for category in categories:
        print(f"\n🎯 Kategori: {category.upper()}")
        post = await ai_content_generator.generate_seferverse_post(category=category)
        
        if post:
            print(f"📝 İçerik: {post['content'][:150]}...")
            print(f"🏷️ Hashtags: {', '.join(post['hashtags'][:5])}")
            print(f"📊 Engagement: {post['engagement_prediction']['score']}/100")
        
        await asyncio.sleep(1)
    
    print("\n✅ Demo tamamlandı!")


# Singleton instance
seferverse_ai_pipeline = SeferVerseAIPipeline()


if __name__ == "__main__":
    # Demo çalıştır
    asyncio.run(demo_ai_generation()) 