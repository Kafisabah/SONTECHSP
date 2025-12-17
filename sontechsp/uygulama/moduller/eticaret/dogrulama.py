# Version: 0.1.0
# Last Update: 2024-12-17
# Module: eticaret.dogrulama
# Description: E-ticaret veri doğrulama yardımcıları
# Changelog:
# - İlk oluşturma
# - Stok, fiyat ve durum doğrulama eklendi

"""
E-ticaret veri doğrulama yardımcıları.
Platform gönderimlerinden önce veri doğruluğunu kontrol eder.
"""

import logging
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .dto import StokGuncelleDTO, FiyatGuncelleDTO, SiparisDTO
from .sabitler import SiparisDurumlari, Platformlar, VARSAYILAN_PARA_BIRIMI
from .hatalar import VeriDogrulamaHatasi

logger = logging.getLogger(__name__)


class VeriDogrulayici:
    """
    E-ticaret veri doğrulama sınıfı.
    
    Doğrulama türleri:
    - Stok güncelleme doğrulaması
    - Fiyat güncelleme doğrulaması
    - Sipariş durum geçiş doğrulaması
    - Platform-spesifik doğrulamalar
    """
    
    # Geçerli durum geçişleri
    GECERLI_DURUM_GECISLERI = {
        SiparisDurumlari.YENI: [SiparisDurumlari.HAZIRLANIYOR, SiparisDurumlari.IPTAL],
        SiparisDurumlari.HAZIRLANIYOR: [SiparisDurumlari.KARGODA, SiparisDurumlari.IPTAL],
        SiparisDurumlari.KARGODA: [SiparisDurumlari.TESLIM],
        SiparisDurumlari.TESLIM: [],  # Son durum
        SiparisDurumlari.IPTAL: []    # Son durum
    }
    
    # Para birimi kodları (ISO 4217)
    GECERLI_PARA_BIRIMLERI = {
        'TRY', 'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'SEK', 'NOK'
    }
    
    @classmethod
    def stok_guncellemelerini_dogrula(cls, guncellemeler: List[StokGuncelleDTO]) -> Tuple[bool, List[str]]:
        """
        Stok güncellemelerini doğrular
        
        Args:
            guncellemeler: Stok güncelleme listesi
            
        Returns:
            (Geçerli mi, Hata mesajları listesi)
        """
        hatalar = []
        
        if not guncellemeler:
            hatalar.append("Stok güncelleme listesi boş olamaz")
            return False, hatalar
        
        # Her güncellemeyi kontrol et
        for i, guncelleme in enumerate(guncellemeler):
            try:
                # DTO validasyonu (zaten __post_init__'te yapılıyor)
                pass
            except ValueError as e:
                hatalar.append(f"Stok güncelleme {i+1}: {str(e)}")
                continue
            
            # İş kuralı validasyonları
            if guncelleme.urun_id <= 0:
                hatalar.append(f"Stok güncelleme {i+1}: Ürün ID pozitif olmalıdır")
            
            if guncelleme.depo_id <= 0:
                hatalar.append(f"Stok güncelleme {i+1}: Depo ID pozitif olmalıdır")
            
            if guncelleme.miktar < 0:
                hatalar.append(f"Stok güncelleme {i+1}: Miktar negatif olamaz")
            
            # Makul değer kontrolü
            if guncelleme.miktar > 1000000:
                hatalar.append(f"Stok güncelleme {i+1}: Miktar çok yüksek (>1M)")
        
        # Duplicate kontrol
        urun_depo_ciftleri = set()
        for i, guncelleme in enumerate(guncellemeler):
            cift = (guncelleme.urun_id, guncelleme.depo_id)
            if cift in urun_depo_ciftleri:
                hatalar.append(f"Stok güncelleme {i+1}: Duplicate ürün-depo çifti")
            urun_depo_ciftleri.add(cift)
        
        gecerli = len(hatalar) == 0
        
        if gecerli:
            logger.debug(f"Stok güncellemeleri doğrulandı - Adet: {len(guncellemeler)}")
        else:
            logger.warning(f"Stok doğrulama hataları: {hatalar}")
        
        return gecerli, hatalar
    
    @classmethod
    def fiyat_guncellemelerini_dogrula(cls, guncellemeler: List[FiyatGuncelleDTO]) -> Tuple[bool, List[str]]:
        """
        Fiyat güncellemelerini doğrular
        
        Args:
            guncellemeler: Fiyat güncelleme listesi
            
        Returns:
            (Geçerli mi, Hata mesajları listesi)
        """
        hatalar = []
        
        if not guncellemeler:
            hatalar.append("Fiyat güncelleme listesi boş olamaz")
            return False, hatalar
        
        # Her güncellemeyi kontrol et
        for i, guncelleme in enumerate(guncellemeler):
            try:
                # DTO validasyonu (zaten __post_init__'te yapılıyor)
                pass
            except ValueError as e:
                hatalar.append(f"Fiyat güncelleme {i+1}: {str(e)}")
                continue
            
            # İş kuralı validasyonları
            if guncelleme.urun_id <= 0:
                hatalar.append(f"Fiyat güncelleme {i+1}: Ürün ID pozitif olmalıdır")
            
            if guncelleme.fiyat < 0:
                hatalar.append(f"Fiyat güncelleme {i+1}: Fiyat negatif olamaz")
            
            # Para birimi kontrolü
            if guncelleme.para_birimi not in cls.GECERLI_PARA_BIRIMLERI:
                hatalar.append(f"Fiyat güncelleme {i+1}: Geçersiz para birimi: {guncelleme.para_birimi}")
            
            # Makul değer kontrolü
            if guncelleme.fiyat > Decimal('1000000'):
                hatalar.append(f"Fiyat güncelleme {i+1}: Fiyat çok yüksek (>1M)")
            
            # Decimal precision kontrolü
            try:
                # 2 ondalık basamak kontrolü
                if guncelleme.fiyat.as_tuple().exponent < -2:
                    hatalar.append(f"Fiyat güncelleme {i+1}: Fiyat en fazla 2 ondalık basamak içerebilir")
            except (AttributeError, InvalidOperation):
                hatalar.append(f"Fiyat güncelleme {i+1}: Geçersiz fiyat formatı")
        
        # Duplicate kontrol
        urun_ids = set()
        for i, guncelleme in enumerate(guncellemeler):
            if guncelleme.urun_id in urun_ids:
                hatalar.append(f"Fiyat güncelleme {i+1}: Duplicate ürün ID")
            urun_ids.add(guncelleme.urun_id)
        
        gecerli = len(hatalar) == 0
        
        if gecerli:
            logger.debug(f"Fiyat güncellemeleri doğrulandı - Adet: {len(guncellemeler)}")
        else:
            logger.warning(f"Fiyat doğrulama hataları: {hatalar}")
        
        return gecerli, hatalar
    
    @classmethod
    def siparis_durum_gecisini_dogrula(cls, mevcut_durum: str, yeni_durum: str) -> Tuple[bool, Optional[str]]:
        """
        Sipariş durum geçişini doğrular
        
        Args:
            mevcut_durum: Mevcut sipariş durumu
            yeni_durum: Yeni sipariş durumu
            
        Returns:
            (Geçerli mi, Hata mesajı)
        """
        # Durum değerleri kontrolü
        try:
            mevcut_enum = SiparisDurumlari(mevcut_durum)
            yeni_enum = SiparisDurumlari(yeni_durum)
        except ValueError as e:
            return False, f"Geçersiz sipariş durumu: {str(e)}"
        
        # Aynı durum kontrolü
        if mevcut_durum == yeni_durum:
            return True, None  # Aynı durum geçerli (idempotent)
        
        # Geçerli geçiş kontrolü
        gecerli_gecisler = cls.GECERLI_DURUM_GECISLERI.get(mevcut_enum, [])
        
        if yeni_enum not in gecerli_gecisler:
            return False, f"Geçersiz durum geçişi: {mevcut_durum} -> {yeni_durum}"
        
        logger.debug(f"Sipariş durum geçişi doğrulandı: {mevcut_durum} -> {yeni_durum}")
        return True, None
    
    @classmethod
    def siparis_dto_dogrula(cls, siparis: SiparisDTO) -> Tuple[bool, List[str]]:
        """
        Sipariş DTO'sunu doğrular
        
        Args:
            siparis: Sipariş DTO'su
            
        Returns:
            (Geçerli mi, Hata mesajları listesi)
        """
        hatalar = []
        
        try:
            # DTO validasyonu (zaten __post_init__'te yapılıyor)
            pass
        except ValueError as e:
            hatalar.append(str(e))
            return False, hatalar
        
        # Platform kontrolü
        if siparis.platform not in [p.value for p in Platformlar]:
            hatalar.append(f"Desteklenmeyen platform: {siparis.platform}")
        
        # Durum kontrolü
        if siparis.durum not in [d.value for d in SiparisDurumlari]:
            hatalar.append(f"Geçersiz sipariş durumu: {siparis.durum}")
        
        # Para birimi kontrolü
        if siparis.para_birimi not in cls.GECERLI_PARA_BIRIMLERI:
            hatalar.append(f"Geçersiz para birimi: {siparis.para_birimi}")
        
        # Tarih kontrolü
        if siparis.siparis_zamani > datetime.now():
            hatalar.append("Sipariş tarihi gelecekte olamaz")
        
        # Tutar kontrolü
        if siparis.toplam_tutar < 0:
            hatalar.append("Toplam tutar negatif olamaz")
        
        if siparis.toplam_tutar > Decimal('1000000'):
            hatalar.append("Toplam tutar çok yüksek (>1M)")
        
        # String uzunluk kontrolleri
        if len(siparis.dis_siparis_no) > 100:
            hatalar.append("Dış sipariş numarası çok uzun (>100 karakter)")
        
        if len(siparis.musteri_ad_soyad) > 200:
            hatalar.append("Müşteri adı soyadı çok uzun (>200 karakter)")
        
        if siparis.kargo_tasiyici and len(siparis.kargo_tasiyici) > 100:
            hatalar.append("Kargo taşıyıcı adı çok uzun (>100 karakter)")
        
        if siparis.takip_no and len(siparis.takip_no) > 100:
            hatalar.append("Takip numarası çok uzun (>100 karakter)")
        
        gecerli = len(hatalar) == 0
        
        if gecerli:
            logger.debug(f"Sipariş DTO doğrulandı - Sipariş: {siparis.dis_siparis_no}")
        else:
            logger.warning(f"Sipariş doğrulama hataları: {hatalar}")
        
        return gecerli, hatalar
    
    @classmethod
    def platform_spesifik_dogrula(cls, platform: str, veri: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Platform-spesifik doğrulamalar
        
        Args:
            platform: Platform türü
            veri: Doğrulanacak veri
            
        Returns:
            (Geçerli mi, Hata mesajları listesi)
        """
        hatalar = []
        
        # Platform kontrolü
        if platform not in [p.value for p in Platformlar]:
            hatalar.append(f"Desteklenmeyen platform: {platform}")
            return False, hatalar
        
        # Platform-spesifik kurallar
        if platform == Platformlar.TRENDYOL:
            # Trendyol spesifik kurallar
            if 'barcode' in veri and not veri['barcode']:
                hatalar.append("Trendyol için barkod zorunludur")
        
        elif platform == Platformlar.HEPSIBURADA:
            # Hepsiburada spesifik kurallar
            if 'merchant_id' in veri and not veri['merchant_id']:
                hatalar.append("Hepsiburada için merchant_id zorunludur")
        
        elif platform == Platformlar.N11:
            # N11 spesifik kurallar
            if 'category_id' in veri and not veri['category_id']:
                hatalar.append("N11 için category_id zorunludur")
        
        # Genel platform kuralları
        if 'api_key' in veri and not veri['api_key']:
            hatalar.append(f"{platform} için API key zorunludur")
        
        gecerli = len(hatalar) == 0
        
        if gecerli:
            logger.debug(f"Platform spesifik doğrulama başarılı - Platform: {platform}")
        else:
            logger.warning(f"Platform doğrulama hataları ({platform}): {hatalar}")
        
        return gecerli, hatalar


# Kolaylık fonksiyonları

def stok_guncellemelerini_dogrula(guncellemeler: List[StokGuncelleDTO]) -> None:
    """
    Stok güncellemelerini doğrular ve hata varsa exception fırlatır
    
    Args:
        guncellemeler: Stok güncelleme listesi
        
    Raises:
        VeriDogrulamaHatasi: Doğrulama hatası durumunda
    """
    gecerli, hatalar = VeriDogrulayici.stok_guncellemelerini_dogrula(guncellemeler)
    
    if not gecerli:
        raise VeriDogrulamaHatasi(
            "Stok güncelleme doğrulama hatası",
            detay="; ".join(hatalar)
        )


def fiyat_guncellemelerini_dogrula(guncellemeler: List[FiyatGuncelleDTO]) -> None:
    """
    Fiyat güncellemelerini doğrular ve hata varsa exception fırlatır
    
    Args:
        guncellemeler: Fiyat güncelleme listesi
        
    Raises:
        VeriDogrulamaHatasi: Doğrulama hatası durumunda
    """
    gecerli, hatalar = VeriDogrulayici.fiyat_guncellemelerini_dogrula(guncellemeler)
    
    if not gecerli:
        raise VeriDogrulamaHatasi(
            "Fiyat güncelleme doğrulama hatası",
            detay="; ".join(hatalar)
        )


def siparis_durum_gecisini_dogrula(mevcut_durum: str, yeni_durum: str) -> None:
    """
    Sipariş durum geçişini doğrular ve hata varsa exception fırlatır
    
    Args:
        mevcut_durum: Mevcut sipariş durumu
        yeni_durum: Yeni sipariş durumu
        
    Raises:
        VeriDogrulamaHatasi: Doğrulama hatası durumunda
    """
    gecerli, hata = VeriDogrulayici.siparis_durum_gecisini_dogrula(mevcut_durum, yeni_durum)
    
    if not gecerli:
        raise VeriDogrulamaHatasi(
            "Sipariş durum geçiş doğrulama hatası",
            detay=hata
        )