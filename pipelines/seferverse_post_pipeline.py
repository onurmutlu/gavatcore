#!/usr/bin/env python3
"""
🚀 SEFERVERSE POST PIPELINE v1.0
Otomatik content üretimi ve yayın sistemi
"""

import asyncio
import time
import schedule
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import random

class SeferVersePostPipeline:
    """SeferVerse otomatik post üretim ve yayın sistemi"""
    
    def __init__(self):
        self.posts_generated_today = 0
        self.target_posts_per_day = 12
        self.post_interval_hours = 2  # Her 2 saatte bir post
        self.content_templates = self._load_content_templates()
        self.generated_posts = []
        
    def _load_content_templates(self) -> List[Dict]:
        """Content template'lerini yükle"""
        return [
            {
                "type": "motivation",
                "template": "🔥 {topic} üzerine düşünce: {content}\n\n#SeferVerse #Motivasyon #Başarı",
                "topics": ["Başarı", "Hedefler", "Gelişim", "Kararlılık", "Özgüven"]
            },
            {
                "type": "tech",
                "template": "💻 Tech Talk: {topic}\n\n{content}\n\n#SeferVerse #Technology #Innovation",
                "topics": ["AI", "Blockchain", "Mobile Development", "Web3", "Startup"]
            },
            {
                "type": "lifestyle", 
                "template": "✨ Lifestyle: {topic}\n\n{content}\n\n#SeferVerse #Lifestyle #Quality",
                "topics": ["Productivity", "Wellness", "Travel", "Culture", "Food"]
            },
            {
                "type": "business",
                "template": "📈 Business Insight: {topic}\n\n{content}\n\n#SeferVerse #Business #Growth",
                "topics": ["Entrepreneurship", "Marketing", "Strategy", "Leadership", "Innovation"]
            }
        ]
    
    def generate_post_content(self) -> Dict:
        """Tek bir post içeriği üret"""
        template = random.choice(self.content_templates)
        topic = random.choice(template["topics"])
        
        # Content üretimi - buraya AI entegrasyonu eklenebilir
        content_variations = [
            f"{topic} konusunda bugün öğrendiğim en önemli şey: Sürekli gelişim, başarının anahtarıdır.",
            f"{topic} alanında uzmanlaşmak isteyenler için: Pratik, sabır ve tutku gerekli.",
            f"{topic} hakkında düşündükçe, bu alanın ne kadar heyecan verici olduğunu anlıyorum.",
            f"{topic} ile ilgili deneyimlerimi paylaşırken, community'nin gücünü bir kez daha görüyorum.",
            f"{topic} konusunda yapılan yenilikler, geleceğe olan bakış açımı değiştiriyor."
        ]
        
        content = random.choice(content_variations)
        
        post = {
            "id": f"sfv_{int(time.time())}",
            "type": template["type"],
            "topic": topic,
            "content": template["template"].format(topic=topic, content=content),
            "timestamp": datetime.now().isoformat(),
            "status": "generated",
            "engagement_target": random.randint(50, 200),
            "hashtags": ["#SeferVerse", f"#{template['type'].title()}", f"#{topic.replace(' ', '')}"]
        }
        
        return post
    
    def generate_daily_posts(self) -> List[Dict]:
        """Günlük 12 post üret"""
        daily_posts = []
        
        for i in range(self.target_posts_per_day):
            post = self.generate_post_content()
            
            # Post zamanlaması (2 saat aralıklarla)
            base_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
            post_time = base_time + timedelta(hours=i * self.post_interval_hours)
            post["scheduled_time"] = post_time.isoformat()
            post["post_number"] = i + 1
            
            daily_posts.append(post)
        
        return daily_posts
    
    def save_posts_to_file(self, posts: List[Dict], filename: str = None):
        """Postları dosyaya kaydet"""
        if filename is None:
            filename = f"seferverse_posts_{datetime.now().strftime('%Y%m%d')}.json"
        
        data = {
            "generated_at": datetime.now().isoformat(),
            "total_posts": len(posts),
            "posts": posts
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {len(posts)} post {filename} dosyasına kaydedildi")
        return filename
    
    def schedule_posts(self):
        """Postları zamanla"""
        daily_posts = self.generate_daily_posts()
        
        for post in daily_posts:
            scheduled_time = datetime.fromisoformat(post["scheduled_time"])
            schedule_time = scheduled_time.strftime("%H:%M")
            
            schedule.every().day.at(schedule_time).do(self.publish_post, post)
            print(f"📅 Post #{post['post_number']} zamanlandı: {schedule_time}")
        
        self.save_posts_to_file(daily_posts)
        return daily_posts
    
    def publish_post(self, post: Dict):
        """Postu yayınla (Telegram, Twitter, etc.)"""
        try:
            print(f"🚀 Post yayınlanıyor: #{post['post_number']}")
            print(f"📄 İçerik: {post['content'][:100]}...")
            
            # Burada Telegram API, Twitter API etc. entegrasyonu olacak
            # Şimdilik console'a yazdır
            
            post["status"] = "published"
            post["published_at"] = datetime.now().isoformat()
            
            # Analytics için kaydet
            self._log_post_analytics(post)
            
            print(f"✅ Post #{post['post_number']} başarıyla yayınlandı!")
            
        except Exception as e:
            print(f"❌ Post yayınlama hatası: {e}")
            post["status"] = "failed"
            post["error"] = str(e)
    
    def _log_post_analytics(self, post: Dict):
        """Post analytics kaydet"""
        analytics = {
            "post_id": post["id"],
            "published_at": post.get("published_at"),
            "type": post["type"],
            "topic": post["topic"],
            "engagement_target": post["engagement_target"],
            "hashtags": post["hashtags"]
        }
        
        # Analytics dosyasına ekle
        analytics_file = f"seferverse_analytics_{datetime.now().strftime('%Y%m')}.json"
        
        try:
            with open(analytics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"analytics": []}
        
        data["analytics"].append(analytics)
        
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def run_scheduler(self):
        """Scheduler'ı çalıştır"""
        print("🚀 SeferVerse Post Pipeline başlatıldı!")
        print(f"📊 Hedef: Günde {self.target_posts_per_day} post")
        print(f"⏰ Aralık: {self.post_interval_hours} saat")
        print("=" * 50)
        
        # İlk günün postlarını oluştur ve zamanla
        self.schedule_posts()
        
        # Scheduler loop
        while True:
            schedule.run_pending()
            time.sleep(60)  # Her dakika kontrol et
    
    def generate_immediate_posts(self, count: int = 12):
        """Hemen test için postlar üret"""
        print(f"🔥 {count} adet SeferVerse post üretiliyor...")
        
        posts = []
        for i in range(count):
            post = self.generate_post_content()
            post["post_number"] = i + 1
            posts.append(post)
            print(f"✅ Post #{i+1}: {post['topic']} - {post['type']}")
        
        filename = self.save_posts_to_file(posts)
        
        print(f"\n🎯 Özet:")
        print(f"📝 Toplam post: {len(posts)}")
        print(f"📂 Dosya: {filename}")
        print(f"🏷️ Kategoriler: {list(set([p['type'] for p in posts]))}")
        
        return posts

def main():
    """Ana fonksiyon"""
    pipeline = SeferVersePostPipeline()
    
    print("🚀 SEFERVERSE POST PIPELINE")
    print("=" * 40)
    print("1. Hemen 12 post üret (test)")
    print("2. Scheduler başlat (otomatik)")
    print("3. Çıkış")
    
    choice = input("\nSeçim (1-3): ").strip()
    
    if choice == "1":
        pipeline.generate_immediate_posts(12)
    elif choice == "2":
        pipeline.run_scheduler()
    else:
        print("👋 Hoşça kal!")

if __name__ == "__main__":
    main() 