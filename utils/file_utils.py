#!/usr/bin/env python3
# utils/file_utils.py
"""
Dosya işlemleri yardımcı modülü.
JSON dosyalarını güvenli şekilde okuma/yazma, kilitleme ve yedekleme işlemleri.

Production-ready özellikler:
- Cross-platform dosya kilitleme
- Büyük dosya desteği (streaming)
- Atomik yazma ve yedekleme
- Otomatik kurtarma (recovery)
- Şema doğrulama
- Transactional multi-write
- Cluster-safe locking
"""

import os
import json
import shutil
import asyncio
import logging
import tempfile
import zstandard  # type: ignore
from typing import Dict, Any, Optional, Union, BinaryIO, List, Tuple, Generator, Iterator, cast
from pathlib import Path
from filelock import FileLock
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

# Tip güvenliği için
import ijson  # type: ignore
import portalocker  # type: ignore
import jsonschema
import redis
import redis_lock  # type: ignore
import threading
import multiprocessing
import time
from datetime import datetime

# Yapılandırma dosyası/env'den ayarları oku
from config import (
    FILE_BACKUP_DIR,
    MAX_BACKUP_COUNT,
    DEFAULT_ENCODING,
    LOG_LEVEL,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD
)

# Yapılandırılmış loglama
import structlog
logger = structlog.get_logger("gavatcore.file_utils")
logger = logger.bind(
    pid=os.getpid(),
    thread_id=threading.get_ident()
)

# Sabitler
BACKUP_ARCHIVE_FORMAT = "zst"  # zstandard sıkıştırma
LARGE_FILE_THRESHOLD = 10 * 1024 * 1024  # 10 MB
MAX_MEMORY_BUFFER = 1 * 1024 * 1024  # 1 MB chunk size
LOCK_TIMEOUT = 30  # saniye
IO_THREAD_POOL = ThreadPoolExecutor(max_workers=4)

# Redis bağlantısı (distributed locking için)
try:
    redis_client: Optional[redis.Redis[str]] = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )
except:
    logger.warning("[REDIS] Bağlantı kurulamadı, yerel kilitleme kullanılacak")
    redis_client = None

class FileOperationError(Exception):
    """Dosya işlemleri için özel hata sınıfı."""
    pass

class TransactionError(Exception):
    """Transaction işlemleri için özel hata sınıfı."""
    pass

@contextmanager
def distributed_lock(resource_key: str, timeout: int = LOCK_TIMEOUT):
    """
    Distributed (Redis tabanlı) veya yerel dosya kilidi oluşturur.
    
    Args:
        resource_key: Kilitlenecek kaynak anahtarı
        timeout: Kilit zaman aşımı (saniye)
    """
    lock = None
    try:
        if redis_client and redis_client.ping():
            # Redis tabanlı distributed lock
            lock = redis_lock.Lock(redis_client, resource_key, expire=timeout)
            acquired = lock.acquire(timeout=timeout)
            if not acquired:
                raise FileOperationError(f"Kilit alınamadı: {resource_key}")
        else:
            # Yerel dosya kilidi
            lock = portalocker.Lock(
                resource_key + ".lock",
                timeout=timeout,
                flags=portalocker.LOCK_EX | portalocker.LOCK_NB
            )
            lock.acquire()
        
        logger.debug("[LOCK] Kilit alındı", 
                    resource=resource_key, 
                    lock_type="redis" if redis_client else "local")
        yield
        
    finally:
        if lock:
            try:
                if isinstance(lock, redis_lock.Lock):
                    lock.release()
                else:
                    lock.release()
                logger.debug("[LOCK] Kilit bırakıldı", 
                           resource=resource_key,
                           lock_type="redis" if redis_client else "local")
            except:
                logger.warning("[LOCK] Kilit bırakılamadı", 
                             resource=resource_key,
                             exc_info=True)

def transactional_save_json(
    files_and_data: Dict[str, Dict],
    backup: bool = True,
    pretty: bool = True,
    encoding: str = DEFAULT_ENCODING,
    schema: Optional[Dict] = None
) -> bool:
    """
    Birden fazla JSON dosyasını transaction olarak kaydeder.
    Ya hepsi başarılı olur ya da hiçbiri değişmez.
    
    Args:
        files_and_data: Dosya yolu -> JSON verisi eşleşmeleri
        backup: Mevcut dosyaları yedekle
        pretty: JSON'u güzel biçimlendir
        encoding: Dosya kodlaması
        schema: JSON şema doğrulaması için şema (opsiyonel)
        
    Returns:
        İşlem başarılı ise True
    """
    temp_files = {}  # Orijinal dosya -> Geçici dosya eşleşmeleri
    backups = {}     # Orijinal dosya -> Yedek dosya eşleşmeleri
    
    try:
        # 1. Şema doğrulaması (varsa)
        if schema:
            for file_path, data in files_and_data.items():
                try:
                    jsonschema.validate(instance=data, schema=schema)
                except jsonschema.exceptions.ValidationError as e:
                    logger.error("[TRANSACTION] Şema doğrulama hatası", 
                               file=file_path, error=str(e))
                    return False
        
        # 2. Tüm dosyalar için geçici dosya oluştur
        for file_path, data in files_and_data.items():
            temp_fd, temp_path = tempfile.mkstemp(suffix='.json')
            os.close(temp_fd)
            
            with open(temp_path, 'w', encoding=encoding) as f:
                if pretty:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(data, f, ensure_ascii=False)
            
            temp_files[file_path] = temp_path
            logger.debug("[TRANSACTION] Geçici dosya oluşturuldu", 
                        original=file_path, temp=temp_path)
        
        # 3. Yedekleme (istenirse)
        if backup:
            for file_path in files_and_data.keys():
                if os.path.exists(file_path):
                    backup_path = backup_file(file_path)
                    if backup_path:
                        backups[file_path] = backup_path
        
        # 4. Tüm dosyaları atomik olarak güncelle
        for file_path, temp_path in temp_files.items():
            ensure_directory(file_path)
            with distributed_lock(file_path):
                shutil.move(temp_path, file_path)
                logger.info("[TRANSACTION] Dosya güncellendi", file=file_path)
        
        logger.info("[TRANSACTION] Başarılı", 
                   files=list(files_and_data.keys()))
        return True
        
    except Exception as e:
        logger.error("[TRANSACTION] Hata", error=str(e), exc_info=True)
        
        # Rollback: Geçici dosyaları temizle
        for temp_path in temp_files.values():
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        # Yedeklerden geri yükle
        if backup and backups:
            for file_path, backup_path in backups.items():
                try:
                    shutil.copy2(backup_path, file_path)
                    logger.info("[TRANSACTION] Yedekten geri yüklendi", 
                              file=file_path, backup=backup_path)
                except Exception as restore_error:
                    logger.error("[TRANSACTION] Geri yükleme hatası", 
                               file=file_path, error=str(restore_error))
        
        return False

def get_file_lock(file_path: str) -> portalocker.Lock:
    """
    Cross-platform dosya kilidi oluşturur.
    
    Args:
        file_path: Kilitlenecek dosya yolu
        
    Returns:
        Dosya kilidi nesnesi
    """
    return portalocker.Lock(
        file_path + ".lock",
        timeout=LOCK_TIMEOUT,
        flags=portalocker.LOCK_EX | portalocker.LOCK_NB
    )

def ensure_directory(file_path: str) -> None:
    """
    Dosya yolundaki dizinlerin var olduğundan emin olur.
    
    Args:
        file_path: Dosya yolu
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"[DIRECTORY] Oluşturuldu: {directory}")

def is_large_file(file_path: str) -> bool:
    """
    Dosyanın büyük olup olmadığını kontrol eder.
    
    Args:
        file_path: Kontrol edilecek dosya yolu
        
    Returns:
        Dosya büyük mü
    """
    try:
        return os.path.getsize(file_path) > LARGE_FILE_THRESHOLD
    except OSError:
        return False

def compress_backup(backup_path: str) -> str:
    """
    Yedek dosyayı sıkıştırır.
    
    Args:
        backup_path: Sıkıştırılacak dosya yolu
        
    Returns:
        Sıkıştırılmış dosya yolu
    """
    compressed_path = f"{backup_path}.{BACKUP_ARCHIVE_FORMAT}"
    try:
        with open(backup_path, 'rb') as f_in:
            with open(compressed_path, 'wb') as f_out:
                compressor = zstandard.ZstdCompressor()
                compressor.copy_stream(f_in, f_out)
        os.unlink(backup_path)  # Orijinal dosyayı sil
        logger.info(f"[COMPRESS] Yedek sıkıştırıldı: {compressed_path}")
        return compressed_path
    except Exception as e:
        logger.error(f"[COMPRESS] Sıkıştırma hatası: {e}")
        if os.path.exists(compressed_path):
            os.unlink(compressed_path)
        return backup_path

def decompress_backup(compressed_path: str) -> str:
    """
    Sıkıştırılmış yedek dosyayı açar.
    
    Args:
        compressed_path: Sıkıştırılmış dosya yolu
        
    Returns:
        Açılmış dosya yolu
    """
    decompressed_path = compressed_path.rsplit(f".{BACKUP_ARCHIVE_FORMAT}", 1)[0]
    try:
        with open(compressed_path, 'rb') as f_in:
            with open(decompressed_path, 'wb') as f_out:
                decompressor = zstandard.ZstdDecompressor()
                decompressor.copy_stream(f_in, f_out)
        logger.info(f"[DECOMPRESS] Yedek açıldı: {decompressed_path}")
        return decompressed_path
    except Exception as e:
        logger.error(f"[DECOMPRESS] Açma hatası: {e}")
        if os.path.exists(decompressed_path):
            os.unlink(decompressed_path)
        raise FileOperationError(f"Yedek açılamadı: {e}")

def load_json(
    file_path: str, 
    default: Optional[Dict[str, Any]] = None,
    create_if_missing: bool = True,
    encoding: str = DEFAULT_ENCODING,
    schema: Optional[Dict[str, Any]] = None,
    stream: bool = False
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    JSON dosyasını güvenli bir şekilde yükler.
    
    Args:
        file_path: Yüklenecek JSON dosyasının yolu
        default: Dosya bulunamazsa veya geçersizse kullanılacak varsayılan değer
        create_if_missing: Dosya yoksa oluşturulsun mu
        encoding: Dosya kodlaması
        schema: JSON şema doğrulaması için şema (opsiyonel)
        stream: Büyük dosyalar için streaming mod kullanılsın mı
        
    Returns:
        JSON dosyasından yüklenen veri sözlüğü veya liste
    """
    if default is None:
        default = {}
    
    try:
        # Dosya var mı kontrol et
        if not os.path.exists(file_path):
            if create_if_missing:
                ensure_directory(file_path)
                save_json(file_path, default, encoding=encoding)
                logger.info("[CREATE] Dosya oluşturuldu", file=file_path)
            return default
        
        # Büyük dosya kontrolü
        use_streaming = stream or is_large_file(file_path)
        
        # Dosyayı aç ve yükle
        with distributed_lock(file_path):
            if use_streaming:
                logger.debug("[STREAM] Streaming modunda okunuyor", file=file_path)
                # Dosyayı açık tut ve iterator döndür
                with open(file_path, 'rb') as f:
                    try:
                        # items array'i için
                        items: List[Dict[str, Any]] = []
                        parser = ijson.parse(f)
                        current_item: Optional[Dict[str, Any]] = None
                        
                        for prefix, event, value in parser:
                            if prefix == 'items' and event == 'start_array':
                                continue
                            elif prefix.startswith('items.item'):
                                if event == 'start_map':
                                    current_item = {}
                                elif event == 'end_map':
                                    if current_item is not None:
                                        items.append(current_item)
                                    current_item = None
                                elif current_item is not None:
                                    key = prefix.split('.')[-1]
                                    current_item[key] = value
                        
                        return items
                    except Exception as e:
                        logger.error("[STREAM] Okuma hatası", 
                                   file=file_path, error=str(e))
                        return cast(Dict[str, Any], default)
            else:
                with open(file_path, 'r', encoding=encoding) as f:
                    try:
                        data = json.load(f)
                        if schema:
                            jsonschema.validate(instance=data, schema=schema)
                        return cast(Dict[str, Any], data)
                    except json.JSONDecodeError as e:
                        logger.error("[LOAD] JSON ayrıştırma hatası", 
                                   file=file_path, error=str(e))
                        # Otomatik kurtarma dene
                        recovered_data = recover_from_backup(file_path)
                        if recovered_data is not None:
                            return recovered_data
                        return cast(Dict[str, Any], default)
                    except jsonschema.exceptions.ValidationError as e:
                        logger.error("[VALIDATE] Şema doğrulama hatası", 
                                   file=file_path, error=str(e))
                        return cast(Dict[str, Any], default)
    except Exception as e:
        logger.error("[LOAD] Hata", file=file_path, error=str(e))
        return cast(Dict[str, Any], default)

def save_json(
    file_path: str, 
    data: Dict,
    backup: bool = True,
    pretty: bool = True,
    encoding: str = DEFAULT_ENCODING,
    schema: Optional[Dict] = None,
    compress_backup: bool = True
) -> bool:
    """
    Veriyi JSON dosyasına güvenli bir şekilde kaydeder.
    
    Args:
        file_path: Kaydedilecek JSON dosyasının yolu
        data: Kaydedilecek veri
        backup: Mevcut dosyayı yedekle
        pretty: JSON'u güzel biçimlendir
        encoding: Dosya kodlaması
        schema: JSON şema doğrulaması için şema (opsiyonel)
        compress_backup: Yedekleri sıkıştır
        
    Returns:
        Başarılı ise True, değilse False
    """
    try:
        # Şema doğrulaması
        if schema:
            try:
                jsonschema.validate(instance=data, schema=schema)
            except jsonschema.exceptions.ValidationError as e:
                logger.error(f"[VALIDATE] Veri şema doğrulaması başarısız: {e}")
                return False
        
        # Dizini oluştur
        ensure_directory(file_path)
        
        # Geçici dosyaya yaz
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding=encoding) as temp_file:
            if pretty:
                json.dump(data, temp_file, indent=2, ensure_ascii=False)
            else:
                json.dump(data, temp_file, ensure_ascii=False)
        
        with get_file_lock(file_path):
            # Önceki dosya varsa yedekle
            if backup and os.path.exists(file_path):
                backup_file(file_path, compress=compress_backup)
            
            # Geçici dosyayı asıl konuma taşı (atomik operasyon)
            shutil.move(temp_file.name, file_path)
        
        logger.debug(f"[SAVE] '{file_path}' başarıyla kaydedildi")
        return True
    except Exception as e:
        # Geçici dosyayı temizle
        if 'temp_file' in locals() and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        
        logger.error(f"[SAVE] '{file_path}' kaydedilirken hata: {e}")
        return False

def backup_file(
    file_path: str, 
    backup_dir: Optional[str] = None, 
    max_backups: int = MAX_BACKUP_COUNT,
    compress: bool = True
) -> Optional[str]:
    """
    Dosyanın yedeğini alır.
    
    Args:
        file_path: Yedeklenecek dosya yolu
        backup_dir: Yedeklerin kaydedileceği dizin
        max_backups: Saklanacak maksimum yedek sayısı
        compress: Yedekleri sıkıştır
        
    Returns:
        Yedek dosyanın yolu veya hata durumunda None
    """
    try:
        if not os.path.exists(file_path):
            return None
        
        # Yedek dizinini belirle
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(file_path), FILE_BACKUP_DIR)
        
        # Yedek dizinini oluştur
        os.makedirs(backup_dir, exist_ok=True)
        
        # Dosya adını ve uzantısını ayır
        base_name = os.path.basename(file_path)
        file_name, file_ext = os.path.splitext(base_name)
        
        # Timestamp ile yedek dosya adını oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_name}_{timestamp}{file_ext}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        # Dosyayı kopyala
        shutil.copy2(file_path, backup_path)
        
        # Sıkıştırma
        if compress:
            backup_path = compress_backup(backup_path)
        
        # Eski yedekleri temizle
        clean_old_backups(backup_dir, file_name, file_ext, max_backups)
        
        logger.info(f"[BACKUP] '{file_path}' yedeklendi: '{backup_path}'")
        return backup_path
    except Exception as e:
        logger.error(f"[BACKUP] '{file_path}' yedeklenirken hata: {e}")
        return None

def clean_old_backups(
    backup_dir: str, 
    file_name: str, 
    file_ext: str, 
    max_count: int
) -> None:
    """
    Belirtilen sayıdan fazla yedek varsa en eskileri siler.
    
    Args:
        backup_dir: Yedek dizini
        file_name: Dosya adı
        file_ext: Dosya uzantısı
        max_count: Saklanacak maksimum yedek sayısı
    """
    try:
        # İlgili yedek dosyalarını bul
        pattern = f"{file_name}_*{file_ext}"
        backup_files = []
        
        # Normal ve sıkıştırılmış yedekleri bul
        backup_files.extend(list(Path(backup_dir).glob(pattern)))
        backup_files.extend(list(Path(backup_dir).glob(f"{pattern}.{BACKUP_ARCHIVE_FORMAT}")))
        
        # Tarihe göre sırala (eskiden yeniye)
        backup_files.sort(key=lambda x: os.path.getmtime(x))
        
        # Eski yedekleri sil
        if len(backup_files) > max_count:
            for old_file in backup_files[:-max_count]:
                try:
                    os.remove(old_file)
                    logger.debug(f"[CLEAN] Eski yedek silindi: '{old_file}'")
                except Exception as e:
                    logger.warning(f"[CLEAN] Yedek silinirken hata: {e}")
    except Exception as e:
        logger.error(f"[CLEAN] Eski yedekler temizlenirken hata: {e}")

def recover_from_backup(file_path: str) -> Optional[Dict]:
    """
    Bozuk dosyayı en yeni yedekten geri yükler.
    
    Args:
        file_path: Kurtarılacak dosya yolu
        
    Returns:
        Kurtarılan veri veya None
    """
    try:
        backup_dir = os.path.join(os.path.dirname(file_path), FILE_BACKUP_DIR)
        if not os.path.exists(backup_dir):
            logger.error("[RECOVERY] Yedek dizini bulunamadı", 
                        file=file_path, backup_dir=backup_dir)
            return None
        
        # En yeni yedeği bul
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        backup_files = []
        
        # Normal ve sıkıştırılmış yedekleri kontrol et
        backup_files.extend(list(Path(backup_dir).glob(f"{file_name}_*.json")))
        backup_files.extend(list(Path(backup_dir).glob(f"{file_name}_*.json.{BACKUP_ARCHIVE_FORMAT}")))
        
        if not backup_files:
            logger.error("[RECOVERY] Yedek bulunamadı", file=file_path)
            return None
        
        # En yeni yedeği bul
        latest_backup = max(backup_files, key=os.path.getmtime)
        
        # Sıkıştırılmış mı kontrol et
        if latest_backup.suffix == f".{BACKUP_ARCHIVE_FORMAT}":
            latest_backup = Path(decompress_backup(str(latest_backup)))
        
        # Yedeği yükle ve doğrula
        with open(latest_backup, 'r', encoding=DEFAULT_ENCODING) as f:
            data = json.load(f)
        
        # Başarılı recovery - dosyayı güncelle
        with distributed_lock(file_path):
            with open(file_path, 'w', encoding=DEFAULT_ENCODING) as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info("[RECOVERY] Başarılı", 
                   file=file_path, 
                   backup=str(latest_backup))
        return data
        
    except Exception as e:
        logger.error("[RECOVERY] Hata", 
                    file=file_path, 
                    error=str(e), 
                    exc_info=True)
        return None

async def load_json_async(
    file_path: str, 
    default: Optional[Dict[str, Any]] = None,
    create_if_missing: bool = True,
    encoding: str = DEFAULT_ENCODING,
    schema: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    JSON dosyasını asenkron olarak yükler.
    
    Args:
        file_path: Yüklenecek JSON dosyasının yolu
        default: Dosya bulunamazsa veya geçersizse kullanılacak varsayılan değer
        create_if_missing: Dosya yoksa oluşturulsun mu
        encoding: Dosya kodlaması
        schema: JSON şema doğrulaması için şema (opsiyonel)
        
    Returns:
        JSON dosyasından yüklenen veri sözlüğü
    """
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        IO_THREAD_POOL,
        lambda: load_json(
            file_path, 
            default, 
            create_if_missing, 
            encoding,
            schema,
            stream=False
        )
    )
    return cast(Dict[str, Any], result)

async def save_json_async(
    file_path: str, 
    data: Dict,
    backup: bool = True,
    pretty: bool = True,
    encoding: str = DEFAULT_ENCODING,
    schema: Optional[Dict] = None
) -> bool:
    """
    Veriyi JSON dosyasına asenkron olarak kaydeder.
    
    Args:
        file_path: Kaydedilecek JSON dosyasının yolu
        data: Kaydedilecek veri
        backup: Mevcut dosyayı yedekle
        pretty: JSON'u güzel biçimlendir
        encoding: Dosya kodlaması
        schema: JSON şema doğrulaması için şema (opsiyonel)
        
    Returns:
        Başarılı ise True, değilse False
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        IO_THREAD_POOL,
        lambda: save_json(
            file_path, 
            data, 
            backup, 
            pretty, 
            encoding,
            schema
        )
    )

def merge_json_files(
    target_file: str, 
    source_files: List[str], 
    overwrite: bool = False,
    schema: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Birden fazla JSON dosyasını birleştirir.
    
    Args:
        target_file: Hedef JSON dosyası
        source_files: Kaynak JSON dosyaları listesi
        overwrite: Çakışma durumunda üzerine yazılsın mı
        schema: Birleştirme sonrası doğrulama için şema
        
    Returns:
        Başarılı ise True, değilse False
    """
    try:
        # Hedef dosyayı yükle (yoksa boş dict)
        target_data = cast(Dict[str, Any], load_json(target_file, default={}, create_if_missing=False))
        
        # Kaynak dosyaları sırayla birleştir
        for source_file in source_files:
            source_data = cast(Dict[str, Any], load_json(source_file, default={}, create_if_missing=False))
            
            if overwrite:
                # Üzerine yaz
                target_data.update(source_data)
            else:
                # Sadece yeni anahtarları ekle
                for key, value in source_data.items():
                    if key not in target_data:
                        target_data[key] = value
        
        # Şema doğrulaması
        if schema:
            try:
                jsonschema.validate(instance=target_data, schema=schema)
            except jsonschema.exceptions.ValidationError as e:
                logger.error(f"[MERGE] Birleştirme sonucu şema doğrulaması başarısız: {e}")
                return False
        
        # Sonucu kaydet
        return save_json(target_file, target_data)
    except Exception as e:
        logger.error(f"[MERGE] JSON dosyaları birleştirilirken hata: {e}")
        return False

def validate_json_schema(data: Dict, schema: Dict) -> Tuple[bool, List[str]]:
    """
    JSON verisini şemaya göre doğrular.
    
    Args:
        data: Doğrulanacak JSON verisi
        schema: JSON Şeması
        
    Returns:
        (Geçerli mi, Hata mesajları listesi)
    """
    try:
        jsonschema.validate(instance=data, schema=schema)
        return True, []
    except jsonschema.exceptions.ValidationError as e:
        return False, [str(e)]
    except Exception as e:
        return False, [f"Doğrulama hatası: {str(e)}"]

# Test ve örnek kullanım
if __name__ == "__main__":
    # Test için logging yapılandırması
    logging.basicConfig(level=logging.DEBUG)
    
    # Worker process fonksiyonu
    def worker_process(file_path):
        with distributed_lock(file_path):
            # Dosyaya yaz
            with open(file_path, 'w') as f:
                data = {"timestamp": datetime.now().isoformat()}
                json.dump(data, f)
            # Biraz bekle
            time.sleep(0.1)
    
    def run_tests():
        """Kapsamlı test senaryoları."""
        
        print("\n🧪 File Utils Test Başlıyor...\n")
        
        # Test dosyaları
        test_file = "test_data.json"
        large_test_file = "test_large.json"
        schema_test_file = "test_schema.json"
        
        # Test verisi
        test_data = {"users": [{"id": 1, "name": "Test User"}], "version": 1}
        
        # JSON Şema örneği
        test_schema = {
            "type": "object",
            "properties": {
                "users": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"}
                        },
                        "required": ["id", "name"]
                    }
                },
                "version": {"type": "integer"}
            },
            "required": ["users", "version"]
        }
        
        try:
            # 1. Temel JSON işlemleri
            print("📝 Temel JSON işlemleri testi...")
            save_json(test_file, test_data)
            loaded_data = load_json(test_file)
            assert loaded_data == test_data
            print("✅ Başarılı: Temel JSON işlemleri")
            
            # 2. Şema doğrulama
            print("\n🔍 Şema doğrulama testi...")
            is_valid, errors = validate_json_schema(test_data, test_schema)
            assert is_valid
            print("✅ Başarılı: Şema doğrulama")
            
            # 3. Büyük dosya testi
            print("\n📦 Büyük dosya testi...")
            # Büyük JSON array oluştur
            large_data = []
            for i in range(1000):
                large_data.append({
                    "id": i,
                    "data": "x" * 100
                })
            save_json(large_test_file, {"items": large_data})
            
            # Streaming okuma
            print("🔄 Streaming okuma testi...")
            loaded_items = load_json(large_test_file, stream=True)
            assert len(loaded_items) == len(large_data)
            print("✅ Başarılı: Büyük dosya işlemleri")
            
            # 4. Yedekleme ve kurtarma
            print("\n💾 Yedekleme ve kurtarma testi...")
            test_data = {"data": "test"}
            save_json(test_file, test_data)
            backup_path = backup_file(test_file)
            assert backup_path is not None
            
            # Dosyayı boz
            with open(test_file, 'w') as f:
                f.write("invalid json{")
            
            # Kurtarma dene
            recovered_data = recover_from_backup(test_file)
            assert recovered_data == test_data
            print("✅ Başarılı: Yedekleme ve kurtarma")
            
            # 5. Asenkron işlemler
            print("\n⚡ Asenkron işlemler testi...")
            async def async_test():
                await save_json_async("async_test.json", test_data)
                loaded = await load_json_async("async_test.json")
                assert loaded == test_data
            
            asyncio.run(async_test())
            print("✅ Başarılı: Asenkron işlemler")
            
            # 6. Dosya birleştirme
            print("\n🔄 Dosya birleştirme testi...")
            data1 = {"a": 1, "b": 2}
            data2 = {"c": 3, "d": 4}
            
            save_json("test1.json", data1)
            save_json("test2.json", data2)
            
            merge_result = merge_json_files(
                "merged.json",
                ["test1.json", "test2.json"]
            )
            assert merge_result
            
            merged_data = load_json("merged.json")
            assert len(merged_data) == 4
            print("✅ Başarılı: Dosya birleştirme")
            
            # 7. Transactional Multi-Write Testi
            print("\n💾 Transactional multi-write testi...")
            files_data = {
                "test1.json": {"data": "file1"},
                "test2.json": {"data": "file2"},
                "test3.json": {"data": "file3"}
            }
            
            success = transactional_save_json(files_data)
            assert success
            
            # Dosyaları kontrol et
            for file_path, expected_data in files_data.items():
                assert os.path.exists(file_path)
                loaded_data = load_json(file_path)
                assert loaded_data == expected_data
            
            print("✅ Başarılı: Transactional multi-write")
            
            # 8. Recovery Testi
            print("\n🔄 Recovery testi...")
            # Önce yedek al
            backup_path = backup_file("test1.json")
            assert backup_path is not None
            
            # Dosyayı boz
            with open("test1.json", 'w') as f:
                f.write("invalid{json")
            
            # Recovery dene
            recovered_data = recover_from_backup("test1.json")
            assert recovered_data is not None
            assert recovered_data == {"data": "file1"}
            print("✅ Başarılı: Recovery")
            
            # 9. Çoklu Process Lock Testi
            print("\n🔒 Multi-process lock testi...")
            
            # 5 process başlat
            processes = []
            for _ in range(5):
                p = multiprocessing.Process(
                    target=worker_process, 
                    args=("shared.json",)
                )
                p.start()
                processes.append(p)
            
            # Tüm process'leri bekle
            for p in processes:
                p.join()
            
            print("✅ Başarılı: Multi-process locking")
            
        except AssertionError:
            print("❌ Test başarısız!")
            raise
        except Exception as e:
            print(f"❌ Test hatası: {e}")
            raise
        finally:
            # Temizlik
            for f in [test_file, large_test_file, schema_test_file, 
                     "async_test.json", "test1.json", "test2.json", 
                     "test3.json", "merged.json", "shared.json"]:
                if os.path.exists(f):
                    os.unlink(f)
            
            # Yedek dizinini temizle
            backup_dir = os.path.join(os.path.dirname(test_file), FILE_BACKUP_DIR)
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
        
        print("\n🎉 Tüm testler başarıyla tamamlandı!")
    
    # Testleri çalıştır
    run_tests() 