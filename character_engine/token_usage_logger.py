"""
💰 Token Usage Logger - GPT API kullanım ve maliyet takibi
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class TokenUsage:
    """Token kullanım kaydı"""
    timestamp: str
    character: str
    user_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    reply_mode: str
    success: bool
    
    def to_dict(self) -> dict:
        return asdict(self)

class TokenUsageLogger:
    """GPT token kullanımı ve maliyet takip sistemi"""
    
    # Model başına token maliyetleri (USD per 1K tokens)
    MODEL_COSTS = {
        # GPT-4 modeller
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
        "gpt-4-turbo-preview": {"prompt": 0.01, "completion": 0.03},
        "gpt-4o": {"prompt": 0.005, "completion": 0.015},
        
        # GPT-3.5 modeller
        "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
        "gpt-3.5-turbo-16k": {"prompt": 0.001, "completion": 0.002},
        
        # Claude modeller (tahmini)
        "claude-3-opus": {"prompt": 0.015, "completion": 0.075},
        "claude-3-sonnet": {"prompt": 0.003, "completion": 0.015},
        "claude-3-haiku": {"prompt": 0.00025, "completion": 0.00125}
    }
    
    def __init__(self, log_dir: str = "logs/token_usage"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Günlük log dosyası
        self.current_log_file = self._get_log_file_path()
        
        # Bellekte tutulan günlük özet
        self.daily_summary: Dict[str, Any] = self._load_daily_summary()
        
        logger.info(f"💰 Token Usage Logger başlatıldı - Log dizini: {log_dir}")
    
    def _get_log_file_path(self, date: Optional[datetime] = None) -> str:
        """Log dosya yolunu getir"""
        if not date:
            date = datetime.now()
        
        filename = f"token_usage_{date.strftime('%Y%m%d')}.json"
        return os.path.join(self.log_dir, filename)
    
    def _load_daily_summary(self) -> Dict[str, Any]:
        """Günlük özeti yükle"""
        try:
            if os.path.exists(self.current_log_file):
                with open(self.current_log_file, 'r') as f:
                    data = json.load(f)
                    return data.get("summary", self._create_empty_summary())
            else:
                return self._create_empty_summary()
        except Exception as e:
            logger.error(f"❌ Günlük özet yükleme hatası: {e}")
            return self._create_empty_summary()
    
    def _create_empty_summary(self) -> Dict[str, Any]:
        """Boş günlük özet oluştur"""
        return {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "by_character": {},
            "by_model": {},
            "by_hour": {},
            "success_rate": 1.0,
            "peak_hour": None,
            "most_active_character": None,
            "most_active_user": None
        }
    
    def log_usage(
        self,
        character: str,
        user_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        reply_mode: str,
        success: bool = True
    ) -> TokenUsage:
        """
        Token kullanımını logla
        
        Args:
            character: Karakter adı
            user_id: Kullanıcı ID
            model: Kullanılan model
            prompt_tokens: Prompt token sayısı
            completion_tokens: Completion token sayısı
            reply_mode: Reply mode (gpt/hybrid/etc)
            success: İstek başarılı mı
        
        Returns:
            TokenUsage object
        """
        try:
            # Maliyet hesapla
            total_tokens = prompt_tokens + completion_tokens
            cost_usd = self._calculate_cost(model, prompt_tokens, completion_tokens)
            
            # Usage kaydı oluştur
            usage = TokenUsage(
                timestamp=datetime.now().isoformat(),
                character=character,
                user_id=user_id,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd=cost_usd,
                reply_mode=reply_mode,
                success=success
            )
            
            # Dosyaya yaz
            self._append_to_log(usage)
            
            # Özeti güncelle
            self._update_summary(usage)
            
            logger.info(
                f"💰 Token kullanımı loglandı - "
                f"Karakter: {character}, Model: {model}, "
                f"Tokens: {total_tokens}, Cost: ${cost_usd:.4f}"
            )
            
            return usage
            
        except Exception as e:
            logger.error(f"❌ Token loglama hatası: {e}")
            raise
    
    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Maliyet hesapla"""
        if model not in self.MODEL_COSTS:
            logger.warning(f"⚠️ Bilinmeyen model: {model}, default maliyet kullanılıyor")
            # Default olarak GPT-3.5 maliyeti
            costs = self.MODEL_COSTS["gpt-3.5-turbo"]
        else:
            costs = self.MODEL_COSTS[model]
        
        prompt_cost = (prompt_tokens / 1000.0) * costs["prompt"]
        completion_cost = (completion_tokens / 1000.0) * costs["completion"]
        
        return round(prompt_cost + completion_cost, 6)
    
    def _append_to_log(self, usage: TokenUsage) -> None:
        """Log dosyasına ekle"""
        try:
            # Mevcut logu oku
            logs = []
            if os.path.exists(self.current_log_file):
                with open(self.current_log_file, 'r') as f:
                    data = json.load(f)
                    logs = data.get("logs", [])
            
            # Yeni kaydı ekle
            logs.append(usage.to_dict())
            
            # Güncellenmiş veriyi yaz
            with open(self.current_log_file, 'w') as f:
                json.dump({
                    "summary": self.daily_summary,
                    "logs": logs
                }, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Log dosyası yazma hatası: {e}")
    
    def _update_summary(self, usage: TokenUsage) -> None:
        """Günlük özeti güncelle"""
        summary = self.daily_summary
        
        # Genel istatistikler
        summary["total_requests"] += 1
        summary["total_tokens"] += usage.total_tokens
        summary["total_cost_usd"] += usage.cost_usd
        
        # Karakter bazlı
        if usage.character not in summary["by_character"]:
            summary["by_character"][usage.character] = {
                "requests": 0, "tokens": 0, "cost": 0.0
            }
        summary["by_character"][usage.character]["requests"] += 1
        summary["by_character"][usage.character]["tokens"] += usage.total_tokens
        summary["by_character"][usage.character]["cost"] += usage.cost_usd
        
        # Model bazlı
        if usage.model not in summary["by_model"]:
            summary["by_model"][usage.model] = {
                "requests": 0, "tokens": 0, "cost": 0.0
            }
        summary["by_model"][usage.model]["requests"] += 1
        summary["by_model"][usage.model]["tokens"] += usage.total_tokens
        summary["by_model"][usage.model]["cost"] += usage.cost_usd
        
        # Saatlik dağılım
        hour = datetime.now().strftime("%H:00")
        if hour not in summary["by_hour"]:
            summary["by_hour"][hour] = {"requests": 0, "tokens": 0, "cost": 0.0}
        summary["by_hour"][hour]["requests"] += 1
        summary["by_hour"][hour]["tokens"] += usage.total_tokens
        summary["by_hour"][hour]["cost"] += usage.cost_usd
        
        # Başarı oranı
        if not usage.success:
            success_count = int(summary["success_rate"] * (summary["total_requests"] - 1))
            summary["success_rate"] = success_count / summary["total_requests"]
        
        # En aktif karakter
        most_active = max(summary["by_character"].items(), 
                         key=lambda x: x[1]["requests"])
        summary["most_active_character"] = most_active[0]
        
        # Peak saat
        if summary["by_hour"]:
            peak = max(summary["by_hour"].items(), 
                      key=lambda x: x[1]["requests"])
            summary["peak_hour"] = peak[0]
    
    def get_daily_stats(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Günlük istatistikleri getir"""
        if not date:
            return self.daily_summary
        
        # Farklı bir tarih istendiyse
        log_file = self._get_log_file_path(date)
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                data = json.load(f)
                return data.get("summary", {})
        
        return {}
    
    def get_monthly_stats(self, year: int, month: int) -> Dict[str, Any]:
        """Aylık istatistikleri topla"""
        monthly_stats = {
            "month": f"{year}-{month:02d}",
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "daily_breakdown": {},
            "character_totals": {},
            "model_totals": {}
        }
        
        # Her gün için logları topla
        for day in range(1, 32):
            try:
                date = datetime(year, month, day)
                daily = self.get_daily_stats(date)
                
                if daily:
                    monthly_stats["total_requests"] += daily.get("total_requests", 0)
                    monthly_stats["total_tokens"] += daily.get("total_tokens", 0)
                    monthly_stats["total_cost_usd"] += daily.get("total_cost_usd", 0)
                    
                    monthly_stats["daily_breakdown"][day] = {
                        "requests": daily.get("total_requests", 0),
                        "cost": daily.get("total_cost_usd", 0)
                    }
                    
                    # Karakter toplamları
                    for char, stats in daily.get("by_character", {}).items():
                        if char not in monthly_stats["character_totals"]:
                            monthly_stats["character_totals"][char] = {
                                "requests": 0, "tokens": 0, "cost": 0.0
                            }
                        monthly_stats["character_totals"][char]["requests"] += stats["requests"]
                        monthly_stats["character_totals"][char]["tokens"] += stats["tokens"]
                        monthly_stats["character_totals"][char]["cost"] += stats["cost"]
                    
                    # Model toplamları
                    for model, stats in daily.get("by_model", {}).items():
                        if model not in monthly_stats["model_totals"]:
                            monthly_stats["model_totals"][model] = {
                                "requests": 0, "tokens": 0, "cost": 0.0
                            }
                        monthly_stats["model_totals"][model]["requests"] += stats["requests"]
                        monthly_stats["model_totals"][model]["tokens"] += stats["tokens"]
                        monthly_stats["model_totals"][model]["cost"] += stats["cost"]
                        
            except ValueError:
                # Geçersiz gün (örn: 31 Şubat)
                break
        
        return monthly_stats
    
    def get_cost_projection(self) -> Dict[str, float]:
        """Maliyet projeksiyonu yap"""
        # Son 7 günün ortalamasını al
        total_cost_7d = 0.0
        days_with_data = 0
        
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            daily = self.get_daily_stats(date)
            if daily and daily.get("total_cost_usd", 0) > 0:
                total_cost_7d += daily["total_cost_usd"]
                days_with_data += 1
        
        if days_with_data == 0:
            return {
                "daily_average": 0.0,
                "monthly_projection": 0.0,
                "yearly_projection": 0.0
            }
        
        daily_avg = total_cost_7d / days_with_data
        
        return {
            "daily_average": round(daily_avg, 2),
            "monthly_projection": round(daily_avg * 30, 2),
            "yearly_projection": round(daily_avg * 365, 2)
        }
    
    def format_stats_message(self) -> str:
        """Admin /stats komutu için formatlanmış mesaj"""
        stats = self.daily_summary
        projection = self.get_cost_projection()
        
        msg = f"💰 **GPT Token İstatistikleri**\n\n"
        msg += f"📅 Tarih: {stats['date']}\n"
        msg += f"📊 Toplam İstek: {stats['total_requests']}\n"
        msg += f"🎯 Toplam Token: {stats['total_tokens']:,}\n"
        msg += f"💵 Günlük Maliyet: ${stats['total_cost_usd']:.2f}\n"
        msg += f"✅ Başarı Oranı: {stats['success_rate']*100:.1f}%\n\n"
        
        if stats['by_character']:
            msg += "👥 **Karakter Bazlı:**\n"
            for char, data in stats['by_character'].items():
                msg += f"  • {char}: {data['requests']} istek, ${data['cost']:.3f}\n"
        
        msg += f"\n📈 **Maliyet Projeksiyonu:**\n"
        msg += f"  • Günlük Ort: ${projection['daily_average']}\n"
        msg += f"  • Aylık Tahmin: ${projection['monthly_projection']}\n"
        msg += f"  • Yıllık Tahmin: ${projection['yearly_projection']}\n"
        
        if stats['peak_hour']:
            msg += f"\n⏰ Yoğun Saat: {stats['peak_hour']}"
        
        return msg

# Singleton instance
token_logger = TokenUsageLogger() 