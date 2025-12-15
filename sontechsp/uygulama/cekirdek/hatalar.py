# Version: 0.1.0
# Last Update: 2024-12-15
# Module: hatalar
# Description: SONTECHSP hata yönetimi modülü
# Changelog:
# - 0.1.0: İlk sürüm, hata sınıfları ve Türkçe hata mesajları

"""
SONTECHSP Hata Yönetimi Modülü

Bu modül uygulama hatalarını kategorize eder ve yönetir:
- Hata sınıf hiyerarşisi
- Türkçe hata mesajları
- Otomatik loglama entegrasyonu
- Hata seviye yönetimi
"""

import logging
from typing import Optional, Dict, Any
from enum import Enum


class HataSeviyesi(Enum):
    """Hata seviye enum'u"""
    DUSUK = "düşük"
    ORTA = "orta"
    YUKSEK = "yüksek"
    KRITIK = "kritik"


class SontechHatasi(Exception):
    """
    SONTECHSP temel hata sınıfı
    
    Tüm uygulama hatalarının ana sınıfı
    """
    
    def __init__(self, 
                 mesaj: str,
                 hata_kodu: Optional[str] = None,
                 seviye: HataSeviyesi = HataSeviyesi.ORTA,
                 ek_bilgi: Optional[Dict[str, Any]] = None):
        
        self.mesaj = mesaj
        self.hata_kodu = hata_kodu or self.__class__.__name__
        self.seviye = seviye
        self.ek_bilgi = ek_bilgi or {}
        
        # Türkçe mesaj oluştur
        super().__init__(self._turkce_mesaj_olustur())
        
        # Otomatik loglama
        self._hatayi_logla()

    def _turkce_mesaj_olustur(self) -> str:
        """Türkçe hata mesajı oluşturur"""
        temel_mesaj = f"[{self.hata_kodu}] {self.mesaj}"
        
        if self.ek_bilgi:
            ek_bilgi_str = ", ".join(f"{k}: {v}" for k, v in self.ek_bilgi.items())
            temel_mesaj += f" (Ek Bilgi: {ek_bilgi_str})"
        
        return temel_mesaj

    def _hatayi_logla(self) -> None:
        """Hatayı uygun seviyede loglar"""
        logger = logging.getLogger('sontechsp')
        
        # Seviyeye göre log seviyesi belirle
        if self.seviye == HataSeviyesi.DUSUK:
            logger.warning(f"Düşük seviye hata: {self}")
        elif self.seviye == HataSeviyesi.ORTA:
            logger.error(f"Orta seviye hata: {self}")
        elif self.seviye == HataSeviyesi.YUKSEK:
            logger.error(f"Yüksek seviye hata: {self}")
        elif self.seviye == HataSeviyesi.KRITIK:
            logger.critical(f"Kritik hata: {self}")

    def to_dict(self) -> Dict[str, Any]:
        """Hatayı sözlük formatında döndürür"""
        return {
            'hata_tipi': self.__class__.__name__,
            'hata_kodu': self.hata_kodu,
            'mesaj': self.mesaj,
            'seviye': self.seviye.value,
            'ek_bilgi': self.ek_bilgi
        }


class AlanHatasi(SontechHatasi):
    """
    Veri alanı doğrulama hataları
    
    Kullanım alanları:
    - Geçersiz veri formatı
    - Eksik zorunlu alan
    - Alan uzunluk sınırı aşımı
    - Tip uyumsuzluğu
    """
    
    def __init__(self, 
                 alan_adi: str,
                 mesaj: str,
                 alan_degeri: Any = None,
                 beklenen_tip: Optional[str] = None):
        
        # Türkçe mesaj oluştur
        turkce_mesaj = f"'{alan_adi}' alanında hata: {mesaj}"
        
        # Ek bilgi hazırla
        ek_bilgi = {'alan_adi': alan_adi}
        if alan_degeri is not None:
            ek_bilgi['alan_degeri'] = str(alan_degeri)
        if beklenen_tip:
            ek_bilgi['beklenen_tip'] = beklenen_tip
        
        super().__init__(
            mesaj=turkce_mesaj,
            hata_kodu=f"ALAN_HATA_{alan_adi.upper()}",
            seviye=HataSeviyesi.DUSUK,
            ek_bilgi=ek_bilgi
        )


class DogrulamaHatasi(SontechHatasi):
    """
    İş kuralı doğrulama hataları
    
    Kullanım alanları:
    - İş kuralı ihlali
    - Veri tutarlılık hatası
    - Yetkilendirme hatası
    - Durum geçiş hatası
    """
    
    def __init__(self, 
                 kural_adi: str,
                 mesaj: str,
                 mevcut_deger: Any = None,
                 beklenen_deger: Any = None):
        
        # Türkçe mesaj oluştur
        turkce_mesaj = f"'{kural_adi}' kuralı ihlal edildi: {mesaj}"
        
        # Ek bilgi hazırla
        ek_bilgi = {'kural_adi': kural_adi}
        if mevcut_deger is not None:
            ek_bilgi['mevcut_deger'] = str(mevcut_deger)
        if beklenen_deger is not None:
            ek_bilgi['beklenen_deger'] = str(beklenen_deger)
        
        super().__init__(
            mesaj=turkce_mesaj,
            hata_kodu=f"DOGRULAMA_HATA_{kural_adi.upper()}",
            seviye=HataSeviyesi.ORTA,
            ek_bilgi=ek_bilgi
        )


class VeritabaniHatasi(SontechHatasi):
    """
    Veritabanı işlem hataları
    
    Kullanım alanları:
    - Bağlantı hatası
    - SQL sorgu hatası
    - Transaction hatası
    - Migration hatası
    """
    
    def __init__(self, 
                 mesaj: str,
                 sql_hata: Optional[str] = None,
                 tablo_adi: Optional[str] = None):
        
        # Türkçe mesaj oluştur
        turkce_mesaj = f"Veritabanı hatası: {mesaj}"
        
        # Ek bilgi hazırla
        ek_bilgi = {}
        if sql_hata:
            ek_bilgi['sql_hata'] = sql_hata
        if tablo_adi:
            ek_bilgi['tablo_adi'] = tablo_adi
        
        super().__init__(
            mesaj=turkce_mesaj,
            hata_kodu="VERITABANI_HATA",
            seviye=HataSeviyesi.YUKSEK,
            ek_bilgi=ek_bilgi
        )


class MigrationHatasi(SontechHatasi):
    """
    Migration işlem hataları
    
    Kullanım alanları:
    - Migration çalıştırma hatası
    - Schema değişiklik hatası
    - Version uyumsuzluğu
    """
    
    def __init__(self, 
                 mesaj: str,
                 migration_version: Optional[str] = None):
        
        # Türkçe mesaj oluştur
        turkce_mesaj = f"Migration hatası: {mesaj}"
        
        # Ek bilgi hazırla
        ek_bilgi = {}
        if migration_version:
            ek_bilgi['migration_version'] = migration_version
        
        super().__init__(
            mesaj=turkce_mesaj,
            hata_kodu="MIGRATION_HATA",
            seviye=HataSeviyesi.YUKSEK,
            ek_bilgi=ek_bilgi
        )


class VeriYuklemeHatasi(SontechHatasi):
    """
    Veri yükleme hataları
    
    Kullanım alanları:
    - Temel veri yükleme hatası
    - Seed data hatası
    - Veri tutarlılık hatası
    """
    
    def __init__(self, 
                 mesaj: str,
                 veri_tipi: Optional[str] = None):
        
        # Türkçe mesaj oluştur
        turkce_mesaj = f"Veri yükleme hatası: {mesaj}"
        
        # Ek bilgi hazırla
        ek_bilgi = {}
        if veri_tipi:
            ek_bilgi['veri_tipi'] = veri_tipi
        
        super().__init__(
            mesaj=turkce_mesaj,
            hata_kodu="VERI_YUKLEME_HATA",
            seviye=HataSeviyesi.ORTA,
            ek_bilgi=ek_bilgi
        )


class EntegrasyonHatasi(SontechHatasi):
    """
    Dış sistem entegrasyon hataları
    
    Kullanım alanları:
    - API çağrı hatası
    - Veritabanı bağlantı hatası
    - Dosya sistemi hatası
    - Ağ bağlantı hatası
    """
    
    def __init__(self, 
                 sistem_adi: str,
                 mesaj: str,
                 hata_detayi: Optional[str] = None,
                 yeniden_deneme_sayisi: int = 0):
        
        # Türkçe mesaj oluştur
        turkce_mesaj = f"'{sistem_adi}' sistemi ile entegrasyon hatası: {mesaj}"
        
        # Ek bilgi hazırla
        ek_bilgi = {
            'sistem_adi': sistem_adi,
            'yeniden_deneme_sayisi': yeniden_deneme_sayisi
        }
        if hata_detayi:
            ek_bilgi['hata_detayi'] = hata_detayi
        
        super().__init__(
            mesaj=turkce_mesaj,
            hata_kodu=f"ENTEGRASYON_HATA_{sistem_adi.upper()}",
            seviye=HataSeviyesi.YUKSEK,
            ek_bilgi=ek_bilgi
        )


class HataYoneticisi:
    """
    Merkezi hata yönetim sınıfı
    
    Hata işleme, loglama ve raporlama işlevlerini sağlar
    """
    
    def __init__(self):
        self.hata_sayaclari: Dict[str, int] = {}
        self.son_hatalar: list = []
        self.maksimum_son_hata_sayisi = 100

    def hata_isle(self, hata: Exception, ek_bilgi: Optional[Dict[str, Any]] = None) -> None:
        """
        Hatayı işler ve kaydeder
        
        Args:
            hata: İşlenecek hata
            ek_bilgi: Ek bilgi sözlüğü
        """
        hata_tipi = hata.__class__.__name__
        
        # Hata sayacını artır
        self.hata_sayaclari[hata_tipi] = self.hata_sayaclari.get(hata_tipi, 0) + 1
        
        # Son hatalar listesine ekle
        hata_bilgisi = {
            'hata_tipi': hata_tipi,
            'mesaj': str(hata),
            'zaman': self._simdi(),
            'ek_bilgi': ek_bilgi or {}
        }
        
        self.son_hatalar.append(hata_bilgisi)
        
        # Liste boyutunu kontrol et
        if len(self.son_hatalar) > self.maksimum_son_hata_sayisi:
            self.son_hatalar.pop(0)
        
        # SontechHatasi değilse manuel loglama
        if not isinstance(hata, SontechHatasi):
            logger = logging.getLogger('sontechsp')
            logger.error(f"İşlenmemiş hata: {hata_tipi} - {hata}")

    def hata_istatistikleri(self) -> Dict[str, Any]:
        """
        Hata istatistiklerini döndürür
        
        Returns:
            İstatistik bilgileri
        """
        toplam_hata = sum(self.hata_sayaclari.values())
        
        return {
            'toplam_hata_sayisi': toplam_hata,
            'hata_tipi_sayaclari': self.hata_sayaclari.copy(),
            'son_hata_sayisi': len(self.son_hatalar),
            'en_sik_hata_tipi': max(self.hata_sayaclari.items(), key=lambda x: x[1])[0] if self.hata_sayaclari else None
        }

    def son_hatalari_getir(self, sayi: int = 10) -> list:
        """
        Son hataları getirir
        
        Args:
            sayi: Getirilecek hata sayısı
            
        Returns:
            Son hatalar listesi
        """
        return self.son_hatalar[-sayi:] if self.son_hatalar else []

    def hata_sayaclarini_sifirla(self) -> None:
        """Hata sayaçlarını sıfırlar"""
        self.hata_sayaclari.clear()
        self.son_hatalar.clear()

    def kritik_hata_kontrol(self) -> bool:
        """
        Kritik hata durumunu kontrol eder
        
        Returns:
            True: Kritik hata mevcut
        """
        kritik_hata_sayisi = sum(
            1 for hata in self.son_hatalar 
            if 'kritik' in hata.get('mesaj', '').lower()
        )
        
        return kritik_hata_sayisi > 0

    def _simdi(self) -> str:
        """Şu anki zamanı string olarak döndürür"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# Global hata yöneticisi instance'ı
_hata_yoneticisi = None


def get_hata_yoneticisi() -> HataYoneticisi:
    """Global hata yöneticisi instance'ını döndürür"""
    global _hata_yoneticisi
    if _hata_yoneticisi is None:
        _hata_yoneticisi = HataYoneticisi()
    return _hata_yoneticisi


# Yardımcı fonksiyonlar
def alan_hatasi_firlatir(alan_adi: str, mesaj: str, **kwargs) -> None:
    """Alan hatası fırlatır"""
    raise AlanHatasi(alan_adi, mesaj, **kwargs)


def dogrulama_hatasi_firlatir(kural_adi: str, mesaj: str, **kwargs) -> None:
    """Doğrulama hatası fırlatır"""
    raise DogrulamaHatasi(kural_adi, mesaj, **kwargs)


def entegrasyon_hatasi_firlatir(sistem_adi: str, mesaj: str, **kwargs) -> None:
    """Entegrasyon hatası fırlatır"""
    raise EntegrasyonHatasi(sistem_adi, mesaj, **kwargs)


def hata_yakala_ve_isle(func):
    """
    Decorator: Fonksiyon hatalarını yakalar ve işler
    
    Usage:
        @hata_yakala_ve_isle
        def my_function():
            # kod
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            get_hata_yoneticisi().hata_isle(e)
            raise
    return wrapper