# Version: 0.1.0
# Last Update: 2024-12-17
# Module: eticaret.baglanti_fabrikasi
# Description: Platform bağlayıcıları için fabrika sınıfı
# Changelog:
# - İlk oluşturma
# - BaglantiFabrikasi ve DummyConnector eklendi

"""
E-ticaret platform bağlayıcıları için fabrika sınıfı.
Platform türüne göre uygun bağlayıcı örneği döndürür.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from .baglanti_arayuzu import BaglantiArayuzu
from .dto import SiparisDTO, StokGuncelleDTO, FiyatGuncelleDTO
from .sabitler import Platformlar
from .hatalar import EntegrasyonHatasi, PlatformHatasi

logger = logging.getLogger(__name__)


class DummyConnector(BaglantiArayuzu):
    """
    Test ve geliştirme amaçlı dummy bağlayıcı.
    Gerçek API çağrısı yapmaz, sadece log basar.
    """
    
    def __init__(self, magaza_hesabi_id: int, kimlik_bilgileri: dict, ayarlar: dict = None):
        super().__init__(magaza_hesabi_id, kimlik_bilgileri, ayarlar)
        self.platform = "DUMMY"
        logger.info(f"DummyConnector başlatıldı - Mağaza ID: {magaza_hesabi_id}")
    
    def siparisleri_cek(self, sonra: Optional[datetime] = None) -> List[SiparisDTO]:
        """Dummy sipariş çekme - gerçek API çağrısı yapmaz"""
        logger.info(f"[{self.platform}] Siparişler çekiliyor - Sonra: {sonra}")
        
        # Test amaçlı dummy sipariş döndür
        dummy_siparis = SiparisDTO(
            platform=self.platform,
            dis_siparis_no="DUMMY-001",
            magaza_hesabi_id=self.magaza_hesabi_id,
            siparis_zamani=datetime.now(),
            musteri_ad_soyad="Test Müşteri",
            toplam_tutar=100.00,
            durum="YENI",
            ham_veri_json={"test": "data"}
        )
        
        logger.info(f"[{self.platform}] 1 adet dummy sipariş döndürüldü")
        return [dummy_siparis]
    
    def stok_gonder(self, guncellemeler: List[StokGuncelleDTO]) -> None:
        """Dummy stok güncelleme - gerçek API çağrısı yapmaz"""
        logger.info(f"[{self.platform}] {len(guncellemeler)} adet stok güncellemesi gönderiliyor")
        
        for guncelleme in guncellemeler:
            logger.debug(f"[{self.platform}] Stok güncelleme - Ürün: {guncelleme.urun_id}, "
                        f"Depo: {guncelleme.depo_id}, Miktar: {guncelleme.miktar}")
        
        logger.info(f"[{self.platform}] Stok güncellemeleri başarıyla gönderildi (dummy)")
    
    def fiyat_gonder(self, guncellemeler: List[FiyatGuncelleDTO]) -> None:
        """Dummy fiyat güncelleme - gerçek API çağrısı yapmaz"""
        logger.info(f"[{self.platform}] {len(guncellemeler)} adet fiyat güncellemesi gönderiliyor")
        
        for guncelleme in guncellemeler:
            logger.debug(f"[{self.platform}] Fiyat güncelleme - Ürün: {guncelleme.urun_id}, "
                        f"Fiyat: {guncelleme.fiyat} {guncelleme.para_birimi}")
        
        logger.info(f"[{self.platform}] Fiyat güncellemeleri başarıyla gönderildi (dummy)")
    
    def siparis_durum_guncelle(self, dis_siparis_no: str, yeni_durum: str, 
                              takip_no: Optional[str] = None) -> None:
        """Dummy sipariş durum güncelleme - gerçek API çağrısı yapmaz"""
        logger.info(f"[{self.platform}] Sipariş durum güncelleme - "
                   f"Sipariş: {dis_siparis_no}, Durum: {yeni_durum}, Takip: {takip_no}")
        
        logger.info(f"[{self.platform}] Sipariş durumu başarıyla güncellendi (dummy)")


class BaglantiFabrikasi:
    """
    Platform türüne göre uygun bağlayıcı örneği döndüren fabrika sınıfı.
    """
    
    # Platform bağlayıcı sınıfları registry'si
    _baglayicilar: Dict[str, type] = {
        # Şu aşamada sadece dummy connector
        Platformlar.WOOCOMMERCE: DummyConnector,
        Platformlar.SHOPIFY: DummyConnector,
        Platformlar.MAGENTO: DummyConnector,
        Platformlar.TRENDYOL: DummyConnector,
        Platformlar.HEPSIBURADA: DummyConnector,
        Platformlar.N11: DummyConnector,
        Platformlar.AMAZON: DummyConnector,
    }
    
    @classmethod
    def baglayici_olustur(cls, platform: str, magaza_hesabi_id: int, 
                         kimlik_bilgileri: dict, ayarlar: dict = None) -> BaglantiArayuzu:
        """
        Platform türüne göre uygun bağlayıcı örneği oluşturur
        
        Args:
            platform: Platform türü (Platformlar enum değeri)
            magaza_hesabi_id: Mağaza hesabı ID'si
            kimlik_bilgileri: Platform kimlik bilgileri
            ayarlar: Platform-spesifik ayarlar
            
        Returns:
            BaglantiArayuzu implementasyonu
            
        Raises:
            PlatformHatasi: Desteklenmeyen platform durumunda
        """
        if platform not in cls._baglayicilar:
            desteklenen = ", ".join(cls._baglayicilar.keys())
            raise PlatformHatasi(
                f"Desteklenmeyen platform: {platform}",
                platform=platform,
                detay=f"Desteklenen platformlar: {desteklenen}"
            )
        
        baglayici_sinifi = cls._baglayicilar[platform]
        
        try:
            baglayici = baglayici_sinifi(magaza_hesabi_id, kimlik_bilgileri, ayarlar)
            logger.info(f"Bağlayıcı oluşturuldu - Platform: {platform}, "
                       f"Mağaza ID: {magaza_hesabi_id}")
            return baglayici
            
        except Exception as e:
            logger.error(f"Bağlayıcı oluşturma hatası - Platform: {platform}, Hata: {str(e)}")
            raise EntegrasyonHatasi(
                f"Bağlayıcı oluşturulamadı: {platform}",
                detay=str(e)
            )
    
    @classmethod
    def baglayici_kaydet(cls, platform: str, baglayici_sinifi: type) -> None:
        """
        Yeni platform bağlayıcısı kaydeder
        
        Args:
            platform: Platform türü
            baglayici_sinifi: BaglantiArayuzu implementasyonu
        """
        if not issubclass(baglayici_sinifi, BaglantiArayuzu):
            raise ValueError("Bağlayıcı sınıfı BaglantiArayuzu'nü implement etmelidir")
        
        cls._baglayicilar[platform] = baglayici_sinifi
        logger.info(f"Yeni bağlayıcı kaydedildi - Platform: {platform}")
    
    @classmethod
    def desteklenen_platformlar(cls) -> List[str]:
        """Desteklenen platform listesini döndürür"""
        return list(cls._baglayicilar.keys())