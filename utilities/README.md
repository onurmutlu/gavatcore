# Gavatcore Utility Araçları

Bu dizin, Gavatcore sisteminin çeşitli yönetim ve bakım araçlarını içerir.

## Dizin Yapısı

### 🔧 Bakım Araçları (`maintenance/`)
- `cleanup_sessions.py`: Session dosyalarını temizler
- `fix_sessions.py`: Bozuk session'ları onarır
- `reset_warnings.py`: Uyarı sayaçlarını sıfırlar
- `reset_dm_states.py`: DM durumlarını sıfırlar

### 🔄 Migrasyon Araçları (`migration/`)
- `migrate_sessions_to_db.py`: Session'ları veritabanına taşır
- `migrate_to_multidb.py`: Çoklu veritabanı yapısına geçiş yapar

### 📊 İzleme Araçları (`monitoring/`)
- `monitor_system.py`: Sistem durumunu izler
- `check_spam_status.py`: Spam durumunu kontrol eder

### 💾 Session Yönetimi (`session_management/`)
Session ile ilgili yönetim araçları

### 🛡️ Spam Yönetimi (`spam_management/`)
- `activate_spam_profiles.py`: Spam profillerini aktifleştirir

## Kullanım

Her aracı çalıştırmadan önce virtual environment'ı aktifleştirin:

```bash
source .venv/bin/activate
```

Örnek kullanımlar:

```bash
# Session temizliği
python utils/maintenance/cleanup_sessions.py

# Sistem izleme
python utils/monitoring/monitor_system.py

# Spam profili aktivasyonu
python utils/spam_management/activate_spam_profiles.py
```

## Önemli Notlar

1. Bu araçları kullanmadan önce sistemin yedeklerini alın
2. Migrasyon araçlarını sırayla çalıştırın
3. Bakım araçlarını maintenance modunda çalıştırın

## Otomatik Araç Bulma

Araçları bulmak için aşağıdaki Python fonksiyonunu kullanabilirsiniz:

```python
def find_utility_tool(tool_type: str, tool_name: str = None) -> str:
    """
    Utility aracını bulur ve tam yolunu döndürür
    
    Args:
        tool_type: Araç tipi ('maintenance', 'migration', 'monitoring', 'session_management', 'spam_management')
        tool_name: Araç adı (opsiyonel)
    
    Returns:
        str: Aracın tam yolu
    """
    base_path = "utils"
    type_map = {
        'maintenance': ['cleanup', 'fix', 'reset'],
        'migration': ['migrate'],
        'monitoring': ['monitor', 'check'],
        'session_management': ['session'],
        'spam_management': ['spam', 'activate']
    }
    
    if tool_type in type_map:
        tool_dir = f"{base_path}/{tool_type}"
        if tool_name:
            return f"{tool_dir}/{tool_name}"
        return tool_dir
    return base_path
```

## Kategoriler

1. 🔧 Bakım
   - Session temizleme
   - Hata düzeltme
   - Sıfırlama işlemleri

2. 🔄 Migrasyon
   - Veritabanı migrasyonları
   - Yapısal değişiklikler

3. 📊 İzleme
   - Sistem monitörleme
   - Durum kontrolleri

4. 💾 Session
   - Session yönetimi
   - Oturum işlemleri

5. 🛡️ Spam
   - Spam yönetimi
   - Profil aktivasyonları 