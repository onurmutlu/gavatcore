#!/usr/bin/env python3
"""
Character Analytics Demo Launcher

Terminal tabanlı test ve analiz aracı.
Karakter istatistiklerini gerçek zamanlı görüntüler.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Ana dizini Python path'ine ekle
sys.path.append(str(Path(__file__).parent.parent))

from core.analytics_dashboard import (
    summarize_character_stats,
    summarize_all_characters,
    get_recent_sales,
    export_summary_to_json
)

class AnalyticsDemoLauncher:
    def __init__(self):
        """Demo launcher'ı başlat."""
        self.log_dir = Path("logs/characters")
        self.characters = self._get_available_characters()
        
    def _get_available_characters(self) -> List[str]:
        """Log dizininden mevcut karakterleri bul."""
        if not self.log_dir.exists():
            return []
        
        return [
            f.stem.replace("_events", "")
            for f in self.log_dir.glob("*_events.jsonl")
        ]
    
    def _format_currency(self, amount: float) -> str:
        """Para birimini formatla."""
        return f"₺{amount:,.2f}"
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Timestamp'i okunabilir formata çevir."""
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%d %b %Y %H:%M")
        except:
            return timestamp
    
    def _print_character_stats(self, stats: Dict[str, Any]) -> None:
        """Karakter istatistiklerini güzel formatla ve yazdır."""
        if not stats:
            print("\n❌ Bu karakter için istatistik bulunamadı!")
            return
        
        print(f"\n📊 Karakter: {stats['character_id']}")
        print(f"{'Toplam Mesaj:':<15} {stats['message_count']:,}")
        print(f"{'Satış Sayısı:':<15} {stats['sale_count']:,}")
        print(f"{'Gelir:':<15} {self._format_currency(stats['total_revenue'])}")
        print(f"{'En Popüler VIP:':<15} {stats['top_service']}")
        print(f"{'İlgi Skoru:':<15} {stats['engagement_score']:.1f}")
        
        # Hizmet dağılımı
        if stats['service_breakdown']:
            print("\n📈 Hizmet Dağılımı:")
            for service, count in stats['service_breakdown'].items():
                print(f" - {service}: {count} satış")
    
    def _print_recent_sales(self, sales: List[Dict[str, Any]]) -> None:
        """Son satışları güzel formatla ve yazdır."""
        if not sales:
            print("\n💡 Henüz satış yapılmamış!")
            return
        
        print("\n🛍️  Son Satışlar:")
        for sale in sales:
            print(
                f" - {sale['service']} "
                f"({self._format_currency(sale['amount'])}) - "
                f"{self._format_timestamp(sale['timestamp'])}"
            )
    
    def _print_menu(self) -> None:
        """Ana menüyü yazdır."""
        print("\n" + "="*50)
        print("🤖 Karakter Analytics Demo Panel")
        print("="*50)
        
        if not self.characters:
            print("\n❌ Hiç karakter logu bulunamadı!")
            print(f"📁 Log dizini: {self.log_dir}")
            return
        
        print("\n📋 Karakter Listesi:")
        for i, char in enumerate(self.characters, 1):
            print(f"{i}. {char}")
        
        print("\nSeçenekler:")
        print("K. Karakter detayı göster (1-N arası numara girin)")
        print("T. Tüm karakterlerin özetini göster")
        print("E. JSON export")
        print("Q. Çıkış")
    
    def _handle_character_details(self, char_id: str) -> None:
        """Seçilen karakter için detaylı analiz göster."""
        stats = summarize_character_stats(char_id)
        self._print_character_stats(stats)
        
        sales = get_recent_sales(char_id, limit=5)
        self._print_recent_sales(sales)
    
    def _handle_all_characters(self) -> None:
        """Tüm karakterlerin özetini göster."""
        stats = summarize_all_characters()
        if not stats:
            print("\n❌ Hiç karakter verisi bulunamadı!")
            return
        
        print("\n📊 Tüm Karakterler:")
        print("-" * 65)
        print(f"{'Karakter':<12} {'Mesaj':<8} {'Satış':<8} {'Gelir':<12} {'Skor':<8}")
        print("-" * 65)
        
        for char_id, char_stats in stats.items():
            print(
                f"{char_id:<12} "
                f"{char_stats['message_count']:<8,} "
                f"{char_stats['sale_count']:<8,} "
                f"{self._format_currency(char_stats['total_revenue']):<12} "
                f"{char_stats['engagement_score']:<8.1f}"
            )
    
    def _handle_export(self) -> None:
        """İstatistikleri JSON dosyasına kaydet."""
        try:
            filename = f"character_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_summary_to_json(filename)
            print(f"\n✅ İstatistikler kaydedildi: {filename}")
        except Exception as e:
            print(f"\n❌ Export hatası: {str(e)}")
    
    def run(self) -> None:
        """Demo launcher'ı çalıştır."""
        while True:
            try:
                self._print_menu()
                
                choice = input("\n> ").strip().upper()
                if choice == "Q":
                    print("\n👋 Görüşürüz!\n")
                    break
                    
                elif choice == "T":
                    self._handle_all_characters()
                    
                elif choice == "E":
                    self._handle_export()
                    
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(self.characters):
                        self._handle_character_details(self.characters[idx])
                    else:
                        print("\n❌ Geçersiz karakter numarası!")
                        
                else:
                    print("\n❌ Geçersiz seçim!")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Görüşürüz!\n")
                break
                
            except Exception as e:
                print(f"\n❌ Hata: {str(e)}")
                continue
            
            input("\nDevam etmek için ENTER'a basın...")

if __name__ == "__main__":
    launcher = AnalyticsDemoLauncher()
    launcher.run() 