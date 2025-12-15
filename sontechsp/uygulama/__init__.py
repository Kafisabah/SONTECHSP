# Version: 0.1.1
# Last Update: 2024-12-15
# Module: uygulama
# Description: SONTECHSP ana uygulama modülü
# Changelog:
# - 0.1.1: Çekirdek altyapı modülü entegrasyonu eklendi
# - 0.1.0: İlk oluşturma

"""
SONTECHSP Ana Uygulama Modülü

Bu modül SONTECHSP sisteminin ana giriş noktasını ve 
temel uygulama bileşenlerini içerir.

Katmanlar:
- cekirdek: Temel altyapı bileşenleri
- veritabani: Veri erişim katmanı
- servisler: İş mantığı katmanı
- arayuz: Kullanıcı arayüzü katmanı
- moduller: İş modülleri
"""

__version__ = "0.1.1"
__author__ = "SONTECHSP Geliştirme Ekibi"

# Çekirdek altyapı erişimi
from .cekirdek import (
    ayarlar_yoneticisi_al,
    kayit_sistemi_al, 
    yetki_kontrolcu_al,
    cekirdek_baslat
)