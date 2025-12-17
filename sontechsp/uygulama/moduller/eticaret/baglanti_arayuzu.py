# Version: 0.1.0
# Last Update: 2024-12-17
# Module: eticaret.baglanti_arayuzu
# Description: Tüm e-ticaret platform entegrasyonları için soyut arayüz
# Changelog:
# - İlk oluşturma
# - BaglantiArayuzu abstract base class eklendi

"""
E-ticaret platform entegrasyonları için soyut arayüz.
Tüm platform bağlayıcıları bu arayüzü implement etmelidir.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from .dto import SiparisDTO, StokGuncelleDTO, FiyatGuncelleDTO


class BaglantiArayuzu(ABC):
    """
    Tüm e-ticaret platform entegrasyonları için soyut temel sınıf.
    
    Bu arayüzü implement eden her platform bağlayıcısı:
    - Sipariş çekme
    - Stok güncelleme
    - Fiyat güncelleme
    - Sipariş durum güncelleme
    işlemlerini desteklemelidir.
    """
    
    def __init__(self, magaza_hesabi_id: int, kimlik_bilgileri: dict, ayarlar: dict = None):
        """
        Bağlayıcı başlatıcı
        
        Args:
            magaza_hesabi_id: Mağaza hesabı ID'si
            kimlik_bilgileri: Platform kimlik bilgileri (API key, secret vb.)
            ayarlar: Platform-spesifik ayarlar
        """
        self.magaza_hesabi_id = magaza_hesabi_id
        self.kimlik_bilgileri = kimlik_bilgileri
        self.ayarlar = ayarlar or {}
    
    @abstractmethod
    def siparisleri_cek(self, sonra: Optional[datetime] = None) -> List[SiparisDTO]:
        """
        Platformdan siparişleri çeker
        
        Args:
            sonra: Bu tarihten sonraki siparişleri getir (None ise tümü)
            
        Returns:
            SiparisDTO listesi
            
        Raises:
            EntegrasyonHatasi: Bağlantı veya veri hatası durumunda
        """
        pass
    
    @abstractmethod
    def stok_gonder(self, guncellemeler: List[StokGuncelleDTO]) -> None:
        """
        Platforma stok güncellemelerini gönderir
        
        Args:
            guncellemeler: Stok güncelleme listesi
            
        Raises:
            EntegrasyonHatasi: Bağlantı veya veri hatası durumunda
        """
        pass
    
    @abstractmethod
    def fiyat_gonder(self, guncellemeler: List[FiyatGuncelleDTO]) -> None:
        """
        Platforma fiyat güncellemelerini gönderir
        
        Args:
            guncellemeler: Fiyat güncelleme listesi
            
        Raises:
            EntegrasyonHatasi: Bağlantı veya veri hatası durumunda
        """
        pass
    
    @abstractmethod
    def siparis_durum_guncelle(self, dis_siparis_no: str, yeni_durum: str, 
                              takip_no: Optional[str] = None) -> None:
        """
        Platformda sipariş durumunu günceller
        
        Args:
            dis_siparis_no: Platform sipariş numarası
            yeni_durum: Yeni sipariş durumu
            takip_no: Kargo takip numarası (opsiyonel)
            
        Raises:
            EntegrasyonHatasi: Bağlantı veya veri hatası durumunda
        """
        pass
    
    def test_baglanti(self) -> bool:
        """
        Platform bağlantısını test eder
        
        Returns:
            Bağlantı başarılı ise True
        """
        try:
            # Basit bir test operasyonu (örn: hesap bilgisi çekme)
            self.siparisleri_cek()
            return True
        except Exception:
            return False