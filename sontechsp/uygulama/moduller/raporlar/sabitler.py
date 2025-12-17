# Version: 0.1.0
# Last Update: 2024-12-17
# Module: raporlar.sabitler
# Description: Raporlama modülü sabitleri ve enum'ları
# Changelog:
# - İlk oluşturma
# - Rapor sabitleri eklendi
# - Performans sabitleri eklendi

"""
SONTECHSP Raporlar Sabitler

Bu modül raporlama sisteminin sabitlerini içerir:
- Rapor türü sabitleri
- Performans sabitleri
- Dosya sabitleri
- Hata mesajları
"""

from enum import Enum


class SatisDurumu(Enum):
    """Satış durumu enum'u"""
    BEKLEMEDE = "BEKLEMEDE"
    TAMAMLANDI = "TAMAMLANDI"
    IPTAL = "IPTAL"
    IADE = "IADE"


class RaporSabitleri:
    """Rapor sabitleri sınıfı"""
    
    # Varsayılan değerler
    VARSAYILAN_LIMIT = 20
    MAKSIMUM_LIMIT = 1000
    VARSAYILAN_KRITIK_SEVIYE = 10
    
    # Dosya sabitleri
    VARSAYILAN_KLASOR = "raporlar"
    CSV_UZANTI = ".csv"
    PDF_UZANTI = ".pdf"
    
    # Tarih formatları
    TARIH_FORMAT = "%Y-%m-%d"
    ZAMAN_DAMGASI_FORMAT = "%Y%m%d_%H%M%S"
    
    # Performans sabitleri
    YAVAS_SORGU_ESIGI_SANIYE = 5.0
    MAKSIMUM_SATIR_SAYISI = 10000


class HataMesajlari:
    """Hata mesajları sınıfı"""
    
    # Parametre hataları
    GECERSIZ_MAGAZA_ID = "Geçersiz mağaza ID: {}"
    GECERSIZ_DEPO_ID = "Geçersiz depo ID: {}"
    GECERSIZ_TARIH_ARALIGI = "Geçersiz tarih aralığı: {} - {}"
    GECERSIZ_LIMIT = "Limit 1 ile {} arasında olmalıdır"
    
    # Veritabanı hataları
    VERITABANI_BAGLANTI_HATASI = "Veritabanı bağlantı hatası: {}"
    SORGU_HATASI = "Sorgu yürütme hatası: {}"
    VERI_BULUNAMADI = "Belirtilen kriterlere uygun veri bulunamadı"
    
    # Dosya hataları
    DOSYA_OLUSTURMA_HATASI = "Dosya oluşturma hatası: {}"
    KLASOR_OLUSTURMA_HATASI = "Klasör oluşturma hatası: {}"
    DOSYA_YAZMA_HATASI = "Dosya yazma hatası: {}"
    
    # Genel hataları
    BEKLENMEYEN_HATA = "Beklenmeyen hata oluştu: {}"
    MVP_PLACEHOLDER = "Bu özellik MVP'de placeholder olarak çalışmaktadır"


class LogMesajlari:
    """Log mesajları sınıfı"""
    
    # Bilgi mesajları
    RAPOR_BASLATILDI = "Rapor oluşturma başlatıldı: {} - Mağaza: {}"
    RAPOR_TAMAMLANDI = "Rapor oluşturma tamamlandı: {} - Süre: {}ms"
    DISARI_AKTARIM_BASLATILDI = "Dışa aktarım başlatıldı: {} - Format: {}"
    DISARI_AKTARIM_TAMAMLANDI = "Dışa aktarım tamamlandı: {}"
    
    # Uyarı mesajları
    YAVAS_SORGU_UYARISI = "Yavaş sorgu tespit edildi: {}ms - Sorgu: {}"
    BUYUK_VERI_SETI_UYARISI = "Büyük veri seti işleniyor: {} satır"
    MVP_PLACEHOLDER_UYARISI = "MVP placeholder çağrıldı: {}"
    
    # Hata mesajları
    KRITIK_HATA = "Kritik hata: {} - Detay: {}"
    PERFORMANS_SORUNU = "Performans sorunu tespit edildi: {}"