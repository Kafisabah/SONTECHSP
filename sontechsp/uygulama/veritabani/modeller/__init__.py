# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.modeller
# Description: SONTECHSP veritabanı modelleri paketi
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Veritabanı Modelleri

Bu paket tüm SQLAlchemy modellerini içerir.
Türkçe ASCII tablo isimlendirme standardına uygun olarak organize edilmiştir.

Modül organizasyonu:
- kullanici_yetki.py: kullanicilar, roller, yetkiler
- firma_magaza.py: firmalar, magazalar, terminaller, depolar  
- stok.py: urunler, urun_barkodlari, stok_bakiyeleri, stok_hareketleri
- crm.py: musteriler, sadakat_puanlari
- pos.py: pos_satislar, pos_satis_satirlari, odeme_kayitlari
- belgeler.py: satis_belgeleri, satis_belge_satirlari
- eticaret.py: eticaret_hesaplari, eticaret_siparisleri
- ebelge.py: ebelge_cikis_kuyrugu, ebelge_durumlari
- kargo.py: kargo_etiketleri, kargo_takipleri
"""

# Tüm modelleri import et (Alembic için gerekli)
from .kullanici_yetki import *
from .firma_magaza import *
from .stok import *
from .crm import *
from .pos import *
from .belgeler import *
from .eticaret import *
from .ebelge import *
from .kargo import *

__all__ = [
    # Kullanıcı ve yetki modelleri
    'Kullanici', 'Rol', 'Yetki', 'KullaniciRol', 'RolYetki',
    
    # Firma ve mağaza modelleri
    'Firma', 'Magaza', 'Terminal', 'Depo',
    
    # Stok modelleri
    'Urun', 'UrunBarkod', 'StokBakiye', 'StokHareket',
    
    # CRM modelleri
    'Musteri', 'SadakatPuan',
    
    # POS modelleri
    'PosSatis', 'PosSatisSatir', 'OdemeKayit',
    
    # Belge modelleri
    'SatisBelge', 'SatisBelgeSatir',
    
    # E-ticaret modelleri
    'EticaretHesap', 'EticaretSiparis',
    
    # E-belge modelleri
    'EbelgeCikisKuyruk', 'EbelgeDurum',
    
    # Kargo modelleri
    'KargoEtiket', 'KargoTakip'
]