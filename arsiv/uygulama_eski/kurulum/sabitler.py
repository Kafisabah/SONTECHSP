# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kurulum.sabitler
# Description: Kurulum modülü sabitleri
# Changelog:
# - Klasör ve dosya sabitleri tanımlandı

"""
Kurulum modülü sabitleri

Bu modül, kurulum işlemleri sırasında kullanılan klasör adları,
dosya adları ve diğer sabitleri içerir.
"""

# Klasör sabitleri
VERI_KLASORU = "veri"
LOG_KLASORU = "loglar"
YEDEK_KLASORU = "yedekler"
RAPOR_KLASORU = "raporlar"

# Yapılandırma dosyası sabitleri
CONFIG_DOSYA_ADI = "config.json"

# Tüm gerekli klasörlerin listesi
GEREKLI_KLASORLER = [
    VERI_KLASORU,
    LOG_KLASORU,
    YEDEK_KLASORU,
    RAPOR_KLASORU
]

# Varsayılan ayarlar
VARSAYILAN_ORTAM = "dev"
VARSAYILAN_LOG_SEVIYESI = "INFO"
VARSAYILAN_VERITABANI_URL = "postgresql://kullanici:sifre@localhost:5432/sontechsp"

# Admin kullanıcı sabitleri
VARSAYILAN_ADMIN_KULLANICI = "admin"
VARSAYILAN_ADMIN_SIFRE = "admin123"

# Alembic yapılandırması
ALEMBIC_CONFIG_YOLU = "uygulama/veritabani/gocler"
ALEMBIC_CONFIG_DOSYASI = "alembic.ini"