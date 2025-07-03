#!/usr/bin/env python3
# core/metrics_collector.py
"""
Metrik toplama ve raporlama modülü.
Sistem performansı, kullanıcı davranışları ve işlem istatistiklerini izler.
"""

import os
import json
import csv
import time
import logging
import threading
import requests  # Global import
from typing import Dict, List, Any, Optional, Union, Set, Callable
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import queue
import atexit
import asyncio

# Yerel modüller
from utils.file_utils import ensure_directory, save_json, load_json
from config import (
    METRICS_DIR,
    METRICS_FORMAT,
    METRICS_FLUSH_INTERVAL,
    DASHBOARD_API_KEY,
    DASHBOARD_API_URL,
    METRICS_RETENTION_DAYS
)

# Logging yapılandırması
logger = logging.getLogger("gavatcore.metrics")
logger.setLevel(logging.INFO)

# Dosya handler
if not os.path.exists(METRICS_DIR):
    os.makedirs(METRICS_DIR, exist_ok=True)

log_path = os.path.join(METRICS_DIR, "metrics.log")
file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class MetricsCollector:
    """Metrik toplama ve raporlama için ana sınıf."""
    
    def __init__(self, flush_interval: int = METRICS_FLUSH_INTERVAL):
        """
        Metrics collector'ı başlat.
        
        Args:
            flush_interval: Metriklerin diske yazılma aralığı (saniye)
        """
        self._metrics_queue = queue.Queue()
        self._counters = defaultdict(Counter)
        self._gauges = {}
        self._last_flush = time.time()
        self._flush_interval = flush_interval
        self._running = False
        self._flush_lock = threading.RLock()
        self._worker_thread = None
        self._metric_handlers = []
        
        # Dosya yolları
        self._daily_file = None
        self._update_daily_file()
        
        # Uygulama çıkışında bekleyen metrikleri yaz
        atexit.register(self._flush_metrics_exit)
        
        # Dashboard callback
        if DASHBOARD_API_URL and DASHBOARD_API_KEY:
            # İstemcilerin yüklenmesi tembel (lazy) olsun
            try:
                import requests
                self._has_requests = True
            except ImportError:
                self._has_requests = False
                logger.warning("Dashboard entegrasyonu için 'requests' kütüphanesi yüklü değil")
        else:
            self._has_requests = False
    
    def _update_daily_file(self) -> None:
        """Günlük metrik dosyasını günceller."""
        today = datetime.now().strftime("%Y-%m-%d")
        self._daily_file = os.path.join(METRICS_DIR, f"metrics_{today}")
        
        # Uzantıyı format türüne göre ekle
        if METRICS_FORMAT.lower() == "csv":
            self._daily_file += ".csv"
        else:
            self._daily_file += ".jsonl"
    
    def start(self) -> None:
        """Asenkron metrik işleme iş parçacığını başlat."""
        if self._running:
            return
        
        self._running = True
        self._worker_thread = threading.Thread(target=self._process_metrics_queue, daemon=True)
        self._worker_thread.start()
        logger.info("Metrics collector başlatıldı")
    
    def stop(self) -> None:
        """Metrik işleme iş parçacığını durdur ve bekleyen metrikleri yaz."""
        if not self._running:
            return
        
        self._running = False
        
        # Son metrikleri yaz
        self._flush_metrics()
        
        # İş parçacığının durmasını bekle
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)
        
        logger.info("Metrics collector durduruldu")
    
    def add_metric_handler(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Özel metrik işleyici ekle.
        
        Args:
            handler: Metrikleri işleyecek fonksiyon
        """
        self._metric_handlers.append(handler)
    
    def log_metric(self, action: str, **kwargs) -> None:
        """
        Metrik kaydı oluşturur.
        
        Args:
            action: İşlem/olay adı
            **kwargs: Metrikle ilgili ek veriler
        """
        # Temel metrik verisi
        metric = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "data": kwargs
        }
        
        # Kuyruğa ekle
        self._metrics_queue.put(metric)
        
        # Counter'ları güncelle
        with self._flush_lock:
            self._counters["actions"][action] += 1
            
            # Kullanıcı bazlı metrikler
            if "user_id" in kwargs:
                user_id = str(kwargs["user_id"])
                self._counters["users"][user_id] += 1
                self._counters[f"user_{user_id}_actions"][action] += 1
            
            # Özel sayaçlar
            for key, value in kwargs.items():
                if isinstance(value, (int, float, bool)) and not isinstance(value, bool):
                    counter_key = f"{action}_{key}"
                    self._counters["numeric"][counter_key] += value
        
        # Periyodik olarak metrikleri diske yaz
        self._check_flush()
    
    def increment(self, metric_name: str, value: int = 1, tags: Dict[str, str] = None) -> None:
        """
        Sayaç metriğini artır.
        
        Args:
            metric_name: Metrik adı
            value: Artış miktarı
            tags: Metrik etiketleri
        """
        with self._flush_lock:
            self._counters["custom"][metric_name] += value
            
            if tags:
                for tag_key, tag_value in tags.items():
                    tag_name = f"{metric_name}:{tag_key}={tag_value}"
                    self._counters["tags"][tag_name] += value
        
        self._check_flush()
    
    def gauge(self, metric_name: str, value: Union[int, float], tags: Dict[str, str] = None) -> None:
        """
        Gösterge (gauge) metriği ayarla.
        
        Args:
            metric_name: Metrik adı
            value: Metrik değeri
            tags: Metrik etiketleri
        """
        with self._flush_lock:
            self._gauges[metric_name] = value
            
            if tags:
                for tag_key, tag_value in tags.items():
                    tag_name = f"{metric_name}:{tag_key}={tag_value}"
                    self._gauges[tag_name] = value
        
        self._check_flush()
    
    def _check_flush(self) -> None:
        """Flush zamanı geldiyse metrikleri yaz."""
        now = time.time()
        if now - self._last_flush > self._flush_interval:
            self._flush_metrics()
    
    def _flush_metrics(self) -> None:
        """Bekleyen metrikleri dosyaya yaz."""
        with self._flush_lock:
            self._last_flush = time.time()
            
            # Günlük dosya adını kontrol et
            self._update_daily_file()
            
            # JSON Lines formatı
            if METRICS_FORMAT.lower() == "jsonl":
                self._flush_jsonl()
            # CSV formatı
            else:
                self._flush_csv()
            
            # Eski dosyaları temizle
            self._cleanup_old_metrics()
    
    def _flush_jsonl(self) -> None:
        """Metrikleri JSONL formatında dosyaya yaz."""
        try:
            # Metrikleri kuyruğundan al
            metrics = []
            while not self._metrics_queue.empty():
                try:
                    metric = self._metrics_queue.get_nowait()
                    metrics.append(metric)
                    self._metrics_queue.task_done()
                except queue.Empty:
                    break
            
            if not metrics:
                return
            
            # Dosyaya ekle
            with open(self._daily_file, "a", encoding="utf-8") as f:
                for metric in metrics:
                    f.write(json.dumps(metric, ensure_ascii=False) + "\n")
            
            # Özel işleyicileri çalıştır
            for handler in self._metric_handlers:
                for metric in metrics:
                    try:
                        handler(metric)
                    except Exception as e:
                        logger.error(f"Metrik işleyici hatası: {e}")
            
            # Dashboard'a gönder
            if self._has_requests:
                self._send_to_dashboard(metrics)
                
            logger.debug(f"{len(metrics)} metrik yazıldı (JSONL)")
        except Exception as e:
            logger.error(f"Metrikler yazılırken hata: {e}")
    
    def _flush_csv(self) -> None:
        """Metrikleri CSV formatında dosyaya yaz."""
        try:
            # Metrikleri kuyruğundan al
            metrics = []
            while not self._metrics_queue.empty():
                try:
                    metric = self._metrics_queue.get_nowait()
                    metrics.append(metric)
                    self._metrics_queue.task_done()
                except queue.Empty:
                    break
            
            if not metrics:
                return
            
            # CSV başlıklarını belirle
            all_fields = set(["timestamp", "action"])
            for metric in metrics:
                all_fields.update(metric.get("data", {}).keys())
            
            # Sabit sıralı başlıklar
            fieldnames = sorted(list(all_fields))
            
            # Dosya varsa yeni satırlar ekle, yoksa oluştur
            file_exists = os.path.exists(self._daily_file)
            
            with open(self._daily_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # Başlığı sadece yeni dosya için yaz
                if not file_exists:
                    writer.writeheader()
                
                # Satırları yaz
                for metric in metrics:
                    row = {
                        "timestamp": metric["timestamp"],
                        "action": metric["action"]
                    }
                    
                    # Veri alanlarını ekle
                    for key, value in metric.get("data", {}).items():
                        if isinstance(value, (dict, list)):
                            row[key] = json.dumps(value, ensure_ascii=False)
                        else:
                            row[key] = value
                    
                    writer.writerow(row)
            
            # Özel işleyicileri çalıştır
            for handler in self._metric_handlers:
                for metric in metrics:
                    try:
                        handler(metric)
                    except Exception as e:
                        logger.error(f"Metrik işleyici hatası: {e}")
            
            # Dashboard'a gönder
            if self._has_requests:
                self._send_to_dashboard(metrics)
                
            logger.debug(f"{len(metrics)} metrik yazıldı (CSV)")
        except Exception as e:
            logger.error(f"Metrikler yazılırken hata: {e}")
    
    def _process_metrics_queue(self) -> None:
        """Arka planda metrikleri işle."""
        while self._running:
            try:
                # Bekleyen metrikler var mı diye düzenli kontrol et
                if not self._metrics_queue.empty():
                    self._flush_metrics()
                
                # Aralıklarla çalış
                time.sleep(1.0)
            except Exception as e:
                logger.error(f"Metrik işleme hatası: {e}")
    
    def _flush_metrics_exit(self) -> None:
        """Uygulama çıkışında bekleyen metrikleri yaz."""
        try:
            # Eğer çalışıyorsa durdur
            if self._running:
                self.stop()
            else:
                # Sadece bekleyen metrikleri yaz
                self._flush_metrics()
        except Exception as e:
            logger.error(f"Çıkış sırasında metrik yazma hatası: {e}")
    
    def _send_to_dashboard(self, metrics: List[Dict[str, Any]]) -> None:
        """
        Metrikleri dashboard'a gönder.
        
        Args:
            metrics: Gönderilecek metrikler listesi
        """
        if not self._has_requests or not DASHBOARD_API_URL or not DASHBOARD_API_KEY:
            return
        
        try:
            import requests
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DASHBOARD_API_KEY}"
            }
            
            # Metrikleri grupla ve batch halinde gönder
            batch_size = 100
            for i in range(0, len(metrics), batch_size):
                batch = metrics[i:i+batch_size]
                
                payload = {
                    "metrics": batch,
                    "source": "gavatcore",
                    "timestamp": datetime.now().isoformat()
                }
                
                try:
                    # Asenkron request için Thread havuzu kullan
                    threading.Thread(
                        target=self._send_request,
                        args=(DASHBOARD_API_URL, headers, payload),
                        daemon=True
                    ).start()
                except Exception as e:
                    logger.error(f"Dashboard metrik gönderimi hatası: {e}")
        except Exception as e:
            logger.error(f"Dashboard entegrasyonu hatası: {e}")
    
    def _send_request(self, url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> None:
        """
        HTTP isteği gönder.
        
        Args:
            url: API URL
            headers: HTTP başlıkları
            payload: Gönderilecek veri
        """
        try:
            import requests
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=5.0
            )
            
            if response.status_code not in (200, 201, 202):
                logger.warning(f"Dashboard API hatası: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"HTTP isteği hatası: {e}")
    
    def _cleanup_old_metrics(self) -> None:
        """Eski metrik dosyalarını temizle."""
        if not METRICS_RETENTION_DAYS or METRICS_RETENTION_DAYS <= 0:
            return
        
        try:
            now = datetime.now()
            cutoff_date = now - timedelta(days=METRICS_RETENTION_DAYS)
            
            for filename in os.listdir(METRICS_DIR):
                if filename.startswith("metrics_"):
                    try:
                        # Dosya adından tarihi çıkar
                        date_str = filename.split("_")[1].split(".")[0]
                        file_date = datetime.strptime(date_str, "%Y-%m-%d")
                        
                        # Eski dosyaları sil
                        if file_date < cutoff_date:
                            file_path = os.path.join(METRICS_DIR, filename)
                            os.remove(file_path)
                            logger.info(f"Eski metrik dosyası silindi: {filename}")
                    except Exception:
                        # Tarih çıkarma hatası, dosyayı atla
                        continue
        except Exception as e:
            logger.error(f"Eski metrik dosyaları temizlenirken hata: {e}")
    
    def get_daily_report(self, date_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Belirli bir gün için rapor oluşturur.
        
        Args:
            date_str: Rapor tarihi (YYYY-MM-DD), None ise bugün
            
        Returns:
            Günlük rapor verileri
        """
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        report = {
            "date": date_str,
            "actions": {},
            "users": {},
            "hourly": defaultdict(int),
            "summary": {}
        }
        
        try:
            # Metrik dosyasını belirle
            file_path = os.path.join(METRICS_DIR, f"metrics_{date_str}")
            
            # JSONL formatı
            if os.path.exists(file_path + ".jsonl"):
                file_path += ".jsonl"
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            metric = json.loads(line.strip())
                            self._process_metric_for_report(metric, report)
                        except json.JSONDecodeError:
                            continue
            
            # CSV formatı
            elif os.path.exists(file_path + ".csv"):
                file_path += ".csv"
                with open(file_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            # CSV'den metrik nesnesi oluştur
                            metric = {
                                "timestamp": row["timestamp"],
                                "action": row["action"],
                                "data": {}
                            }
                            
                            for key, value in row.items():
                                if key not in ("timestamp", "action"):
                                    metric["data"][key] = value
                            
                            self._process_metric_for_report(metric, report)
                        except Exception:
                            continue
            
            # Özet hesapla
            report["summary"] = {
                "total_actions": sum(report["actions"].values()),
                "total_users": len(report["users"]),
                "most_common_action": max(report["actions"].items(), key=lambda x: x[1])[0] if report["actions"] else None,
                "peak_hour": max(report["hourly"].items(), key=lambda x: x[1])[0] if report["hourly"] else None
            }
            
            return report
        except Exception as e:
            logger.error(f"Günlük rapor oluşturma hatası: {e}")
            return report
    
    def _process_metric_for_report(self, metric: Dict[str, Any], report: Dict[str, Any]) -> None:
        """
        Metriği rapor için işle.
        
        Args:
            metric: İşlenecek metrik
            report: Güncellenecek rapor
        """
        try:
            # Aksiyon sayısını artır
            action = metric["action"]
            report["actions"][action] = report["actions"].get(action, 0) + 1
            
            # Kullanıcı bilgisi varsa ekle
            user_id = metric.get("data", {}).get("user_id")
            if user_id:
                user_id = str(user_id)
                if user_id not in report["users"]:
                    report["users"][user_id] = {"actions": 0, "last_seen": None}
                
                report["users"][user_id]["actions"] += 1
                report["users"][user_id]["last_seen"] = metric["timestamp"]
            
            # Saatlik dağılım
            try:
                timestamp = datetime.fromisoformat(metric["timestamp"])
                hour = timestamp.hour
                report["hourly"][hour] += 1
            except (ValueError, TypeError):
                pass
        except Exception:
            # Metrik işleme hatası, atla
            pass


# Global metrics collector nesnesi
metrics_collector = MetricsCollector()
metrics_collector.start()


def log_metric(action: str, **kwargs) -> None:
    """
    Metrik kaydı oluşturur.
    
    Args:
        action: İşlem/olay adı
        **kwargs: Metrikle ilgili ek veriler
    """
    metrics_collector.log_metric(action, **kwargs)


def increment(metric_name: str, value: int = 1, tags: Dict[str, str] = None) -> None:
    """
    Sayaç metriğini artır.
    
    Args:
        metric_name: Metrik adı
        value: Artış miktarı
        tags: Metrik etiketleri
    """
    metrics_collector.increment(metric_name, value, tags)


def gauge(metric_name: str, value: Union[int, float], tags: Dict[str, str] = None) -> None:
    """
    Gösterge (gauge) metriği ayarla.
    
    Args:
        metric_name: Metrik adı
        value: Metrik değeri
        tags: Metrik etiketleri
    """
    metrics_collector.gauge(metric_name, value, tags)


def get_daily_report(date_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Belirli bir gün için rapor oluşturur.
    
    Args:
        date_str: Rapor tarihi (YYYY-MM-DD), None ise bugün
        
    Returns:
        Günlük rapor verileri
    """
    return metrics_collector.get_daily_report(date_str)


async def log_metric_async(action: str, **kwargs) -> None:
    """
    Metrik kaydını asenkron olarak oluşturur.
    
    Args:
        action: İşlem/olay adı
        **kwargs: Metrikle ilgili ek veriler
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: log_metric(action, **kwargs))


def add_metric_handler(handler: Callable[[Dict[str, Any]], None]) -> None:
    """
    Özel metrik işleyici ekle.
    
    Args:
        handler: Metrikleri işleyecek fonksiyon
    """
    metrics_collector.add_metric_handler(handler)


# Temizleme işlevi
def shutdown_metrics():
    """Metrics collector'ı durdur ve bekleyen metrikleri yaz."""
    metrics_collector.stop()


# Atexit'e kaydol
atexit.register(shutdown_metrics)


# Kullanım örneği:
if __name__ == "__main__":
    # Basit metrik loglama
    log_metric("test_action", user_id=12345, value=100)
    
    # Sayaç artırma
    increment("api_calls", tags={"endpoint": "users"})
    
    # Gauge metriği
    gauge("system_memory", 85.5, tags={"server": "main"})
    
    # Rapor oluşturma
    report = get_daily_report()
    print(f"Günlük rapor: {report}")
    
    # Temizleme
    metrics_collector.stop() 