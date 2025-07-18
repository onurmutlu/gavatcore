"""
Character Analytics Dashboard Module

Bu modül, karakter loglarını analiz ederek istatistel özet çıkarır.
Her karakter için mesaj, satış ve etkileşim metrikleri üretir.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
from core.metrics_collector import MetricsCollector
from core.error_tracker import ErrorTracker
from core.analytics_logger import log_analytics
import asyncio

class CharacterAnalyticsDashboard:
    def __init__(self, log_dir: str = "logs/characters") -> None:
        """
        Analytics dashboard'ı başlat.
        
        Args:
            log_dir: Karakter log dosyalarının bulunduğu dizin
        """
        self.log_dir = Path(log_dir)
        self.metrics = MetricsCollector()
        self.error_tracker = ErrorTracker()
    
    def _read_character_logs(self, character_id: str) -> List[Dict[str, Any]]:
        """Karakter log dosyasını oku ve parse et."""
        log_file = self.log_dir / f"{character_id}_events.jsonl"
        if not log_file.exists():
            return []
        
        events = []
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        events.append(event)
                    except json.JSONDecodeError:
                        continue  # Bozuk JSON satırını atla
        except Exception as e:
            print(f"Hata: {character_id} logları okunamadı - {str(e)}")
            return []
            
        return events
    
    def summarize_character_stats(self, character_id: str) -> Dict[str, Any]:
        """
        Karakter için özet istatistikler üret.
        
        Args:
            character_id: İstatistikleri çıkarılacak karakter ID'si
            
        Returns:
            Karakterin mesaj, satış ve etkileşim istatistikleri
        """
        events = self._read_character_logs(character_id)
        if not events:
            return {}
            
        # Temel sayaçlar
        message_count = 0
        sale_count = 0
        total_revenue = 0
        services = Counter()
        
        # Eventleri işle
        for event in events:
            event_type = event.get("event_type", "")
            metadata = event.get("metadata", {})
            
            if event_type == "message_sent":
                message_count += 1
            elif event_type == "vip_sale":
                sale_count += 1
                total_revenue += metadata.get("amount", 0)
                services[metadata.get("service", "bilinmeyen")] += 1
        
        # En çok satılan hizmeti bul
        top_service = services.most_common(1)[0][0] if services else "yok"
        
        # İlgi skorunu hesapla
        engagement_score = (
            message_count * 0.6 + 
            sale_count * 1.5 + 
            total_revenue * 0.1
        )
        
        return {
            "character_id": character_id,
            "message_count": message_count,
            "sale_count": sale_count,
            "total_revenue": total_revenue,
            "top_service": top_service,
            "engagement_score": round(engagement_score, 2),
            "service_breakdown": dict(services),
            "last_updated": datetime.now().isoformat()
        }
    
    def summarize_all_characters(self) -> Dict[str, Dict[str, Any]]:
        """
        Tüm karakterler için özet istatistikler üret.
        
        Returns:
            Karakter ID'lerine göre istatistik özetleri
        """
        all_stats = {}
        
        # Log dizinindeki tüm JSONL dosyalarını tara
        for log_file in self.log_dir.glob("*_events.jsonl"):
            character_id = log_file.stem.replace("_events", "")
            stats = self.summarize_character_stats(character_id)
            if stats:  # Boş olmayan istatistikleri ekle
                all_stats[character_id] = stats
                
        return all_stats
    
    def get_recent_sales(self, 
                        character_id: str, 
                        limit: int = 5) -> List[Dict[str, Any]]:
        """
        Karakterin son satışlarını getir.
        
        Args:
            character_id: Satışları listelenecek karakter ID'si
            limit: Kaç satış getirileceği
            
        Returns:
            Son satışların listesi (yeniden eskiye)
        """
        events = self._read_character_logs(character_id)
        
        # Sadece satış eventlerini filtrele ve sırala
        sales = [
            {
                "timestamp": event["timestamp"],
                "service": event["metadata"].get("service", "bilinmeyen"),
                "amount": event["metadata"].get("amount", 0),
                "user_id": event["metadata"].get("user_id")
            }
            for event in events
            if event.get("event_type") == "vip_sale"
        ]
        
        # Timestamp'e göre sırala (yeniden eskiye)
        sales.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return sales[:limit]
    
    def export_summary_to_json(self, path: str) -> None:
        """
        Tüm karakter istatistiklerini JSON dosyasına kaydet.
        
        Args:
            path: Kaydedilecek JSON dosyasının yolu
        """
        try:
            stats = self.summarize_all_characters()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            print(f"✅ İstatistikler kaydedildi: {path}")
        except Exception as e:
            print(f"❌ JSON export hatası: {str(e)}")

    async def get_dashboard_data(self, time_range: str = "24h") -> dict:
        try:
            # Zaman aralığını hesapla
            end_time = datetime.now()
            if time_range == "24h":
                start_time = end_time - timedelta(hours=24)
            elif time_range == "7d":
                start_time = end_time - timedelta(days=7)
            elif time_range == "30d":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(hours=24)
            
            # Metrikleri topla
            metrics_data = await self.metrics.collect_metrics(start_time, end_time)
            
            # Hataları topla
            error_data = await self.error_tracker.get_errors(start_time, end_time)
            
            # Dashboard verisi oluştur
            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "time_range": time_range,
                "metrics": metrics_data,
                "errors": error_data,
                "summary": {
                    "total_requests": metrics_data.get("total_requests", 0),
                    "error_rate": metrics_data.get("error_rate", 0),
                    "avg_response_time": metrics_data.get("avg_response_time", 0),
                    "active_users": metrics_data.get("active_users", 0)
                }
            }
            
            # Analitik logla
            await log_analytics(
                event_type="dashboard_view",
                data={
                    "time_range": time_range,
                    "summary": dashboard_data["summary"]
                }
            )
            
            return dashboard_data
            
        except Exception as e:
            await log_analytics(
                event_type="dashboard_error",
                data={"error": str(e)}
            )
            raise

# Singleton instance
analytics_dashboard = CharacterAnalyticsDashboard()

# Kolay kullanım için yardımcı fonksiyonlar
def get_dashboard(log_dir: str = "logs/characters") -> CharacterAnalyticsDashboard:
    """Global dashboard instance'ı döndür."""
    return CharacterAnalyticsDashboard(log_dir)

def summarize_character_stats(character_id: str) -> Dict[str, Any]:
    """Karakter istatistiklerini getir."""
    return get_dashboard().summarize_character_stats(character_id)

def summarize_all_characters() -> Dict[str, Dict[str, Any]]:
    """Tüm karakter istatistiklerini getir."""
    return get_dashboard().summarize_all_characters()

def get_recent_sales(character_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Karakterin son satışlarını getir."""
    return get_dashboard().get_recent_sales(character_id, limit)

def export_summary_to_json(path: str) -> None:
    """İstatistikleri JSON'a kaydet."""
    get_dashboard().export_summary_to_json(path) 