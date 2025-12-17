# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kargo.sabitler
# Description: Kargo modülü için sabit değerler
# Changelog:
# - Kaynak türleri sabitleri eklendi
# - Etiket durumları sabitleri eklendi
# - Takip durumları sabitleri eklendi
# - Taşıyıcı kodları sabitleri eklendi

"""
Kargo modülü için sabit değerler.

Bu modül, kargo işlemlerinde kullanılan tüm sabit değerleri içerir.
Kaynak türleri, durum kodları ve taşıyıcı bilgileri burada tanımlanır.
"""


class KaynakTurleri:
    """Kargo etiketinin oluşturulduğu kaynak türleri."""
    
    POS_SATIS = "POS_SATIS"
    SATIS_BELGESI = "SATIS_BELGESI"
    
    @classmethod
    def tum_turler(cls):
        """Tüm kaynak türlerini liste olarak döndürür."""
        return [cls.POS_SATIS, cls.SATIS_BELGESI]
    
    @classmethod
    def gecerli_mi(cls, kaynak_turu):
        """Verilen kaynak türünün geçerli olup olmadığını kontrol eder."""
        return kaynak_turu in cls.tum_turler()


class EtiketDurumlari:
    """Kargo etiketlerinin durumları."""
    
    BEKLIYOR = "BEKLIYOR"
    OLUSTURULDU = "OLUSTURULDU"
    HATA = "HATA"
    
    @classmethod
    def tum_durumlar(cls):
        """Tüm etiket durumlarını liste olarak döndürür."""
        return [cls.BEKLIYOR, cls.OLUSTURULDU, cls.HATA]
    
    @classmethod
    def gecerli_mi(cls, durum):
        """Verilen durumun geçerli olup olmadığını kontrol eder."""
        return durum in cls.tum_durumlar()


class TakipDurumlari:
    """Kargo takip durumları."""
    
    BILINMIYOR = "BILINMIYOR"
    KARGODA = "KARGODA"
    TESLIM = "TESLIM"
    IPTAL = "IPTAL"
    
    @classmethod
    def tum_durumlar(cls):
        """Tüm takip durumlarını liste olarak döndürür."""
        return [cls.BILINMIYOR, cls.KARGODA, cls.TESLIM, cls.IPTAL]
    
    @classmethod
    def gecerli_mi(cls, durum):
        """Verilen durumun geçerli olup olmadığını kontrol eder."""
        return durum in cls.tum_durumlar()


class Tasiyicilar:
    """Desteklenen kargo taşıyıcıları (MVP sabit listesi)."""
    
    YURTICI = "YURTICI"
    ARAS = "ARAS"
    MNG = "MNG"
    PTT = "PTT"
    SURAT = "SURAT"
    
    @classmethod
    def tum_tasiyicilar(cls):
        """Tüm taşıyıcıları liste olarak döndürür."""
        return [cls.YURTICI, cls.ARAS, cls.MNG, cls.PTT, cls.SURAT]
    
    @classmethod
    def gecerli_mi(cls, tasiyici):
        """Verilen taşıyıcının geçerli olup olmadığını kontrol eder."""
        return tasiyici in cls.tum_tasiyicilar()


# Maksimum deneme sayısı sabiti
MAKSIMUM_DENEME_SAYISI = 3

# Varsayılan paket ağırlığı (kg)
VARSAYILAN_PAKET_AGIRLIK_KG = 1.0