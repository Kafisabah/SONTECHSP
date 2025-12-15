# Version: 0.1.0
# Last Update: 2024-12-15
# Module: sontechsp
# Description: SONTECHSP ana paket modülü
# Changelog:
# - 0.1.0: İlk sürüm, çekirdek altyapı entegrasyonu

"""
SONTECHSP - Satış Noktası ve ERP Sistemi

Windows tabanlı, çoklu mağaza/şube destekli POS + ERP + CRM sistemi.

Temel Özellikler:
- Satış Noktası (POS) işlemleri
- Stok yönetimi
- Müşteri ilişkileri yönetimi (CRM)
- E-ticaret entegrasyonları
- E-belge (fatura/irsaliye) işlemleri
- Kargo entegrasyonları
- Raporlama sistemi

Teknoloji Stack:
- Python 3.11+
- PyQt6 (GUI)
- PostgreSQL (Ana veritabanı)
- SQLite (Offline cache)
- SQLAlchemy (ORM)
- FastAPI (Servis katmanı)
"""

__version__ = "0.1.0"
__author__ = "SONTECHSP Geliştirme Ekibi"
__email__ = "gelistirme@sontechsp.com"

# Ana uygulama erişimi
from .uygulama import (
    ayarlar_yoneticisi_al,
    kayit_sistemi_al,
    yetki_kontrolcu_al, 
    cekirdek_baslat
)