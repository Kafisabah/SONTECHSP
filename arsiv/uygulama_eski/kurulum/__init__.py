# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kurulum
# Description: SONTECHSP kurulum ve bootstrap altyapısı
# Changelog:
# - İlk kurulum modülü oluşturuldu
# - Hata sınıfları tanımlandı

"""
SONTECHSP Kurulum Bootstrap Altyapısı

Bu modül, uygulamanın ilk çalıştırılması için gerekli tüm hazırlık işlemlerini
otomatikleştiren bootstrap altyapısını içerir.

Özellikler:
- Klasör yapısı oluşturma
- Ayar dosyası yönetimi
- Veritabanı bağlantı kontrolü
- Alembic migration çalıştırma
- Varsayılan admin kullanıcı oluşturma
"""

import logging

# Kurulum modülü için logger
logger = logging.getLogger(__name__)


class KurulumHatasi(Exception):
    """Kurulum işlemleri için temel hata sınıfı"""
    pass


class DogrulamaHatasi(KurulumHatasi):
    """Veritabanı bağlantı ve doğrulama hataları"""
    pass


class KlasorHatasi(KurulumHatasi):
    """Klasör oluşturma ve erişim hataları"""
    pass


class AyarHatasi(KurulumHatasi):
    """Yapılandırma dosyası hataları"""
    pass


class MigrationHatasi(KurulumHatasi):
    """Alembic migration hataları"""
    pass


class KullaniciHatasi(KurulumHatasi):
    """Admin kullanıcı oluşturma hataları"""
    pass


__all__ = [
    'KurulumHatasi',
    'DogrulamaHatasi', 
    'KlasorHatasi',
    'AyarHatasi',
    'MigrationHatasi',
    'KullaniciHatasi',
    'logger'
]