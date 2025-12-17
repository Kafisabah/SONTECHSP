# Version: 0.1.0
# Last Update: 2024-12-17
# Module: eticaret.sabitler
# Description: E-ticaret entegrasyonu için sabitler ve enum'lar
# Changelog:
# - İlk oluşturma
# - Platform, durum ve iş türü sabitleri eklendi

"""
E-ticaret entegrasyonu için merkezi sabitler.
Magic string kullanımını önlemek için tüm sabitler burada tanımlanır.
"""

from enum import Enum


class Platformlar(str, Enum):
    """Desteklenen e-ticaret platformları"""
    WOOCOMMERCE = "WOOCOMMERCE"
    SHOPIFY = "SHOPIFY"
    MAGENTO = "MAGENTO"
    TRENDYOL = "TRENDYOL"
    HEPSIBURADA = "HEPSIBURADA"
    N11 = "N11"
    AMAZON = "AMAZON"


class SiparisDurumlari(str, Enum):
    """Sipariş durumları"""
    YENI = "YENI"
    HAZIRLANIYOR = "HAZIRLANIYOR"
    KARGODA = "KARGODA"
    TESLIM = "TESLIM"
    IPTAL = "IPTAL"


class JobTurleri(str, Enum):
    """İş kuyruğu türleri"""
    SIPARIS_CEK = "SIPARIS_CEK"
    STOK_GONDER = "STOK_GONDER"
    FIYAT_GONDER = "FIYAT_GONDER"
    DURUM_GUNCELLE = "DURUM_GUNCELLE"


class JobDurumlari(str, Enum):
    """İş durumları"""
    BEKLIYOR = "BEKLIYOR"
    GONDERILDI = "GONDERILDI"
    HATA = "HATA"


# Varsayılan değerler
VARSAYILAN_PARA_BIRIMI = "TRY"
MAKSIMUM_YENIDEN_DENEME = 6
YENIDEN_DENEME_ARALIĞI_DAKIKA = [1, 2, 4, 8, 16, 32]  # Üstel geri çekilme