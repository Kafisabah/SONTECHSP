# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kargo.tasiyici_arayuzu
# Description: Kargo taşıyıcıları için standart arayüz
# Changelog:
# - TasiyiciArayuzu abstract base class eklendi
# - etiket_olustur ve durum_sorgula metodları tanımlandı

"""
Kargo taşıyıcıları için standart arayüz.

Bu modül, farklı kargo taşıyıcılarıyla iletişim için standart arayüz sağlar.
Tüm taşıyıcı implementasyonları bu arayüzü implement etmelidir.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class TasiyiciArayuzu(ABC):
    """
    Kargo taşıyıcıları için standart arayüz.
    
    Bu abstract class, tüm kargo taşıyıcı implementasyonlarının
    uyması gereken standart metodları tanımlar.
    """
    
    @abstractmethod
    def etiket_olustur(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kargo etiket oluşturur.
        
        Args:
            payload: Etiket oluşturma için gerekli veriler
                - alici_ad: str
                - alici_telefon: str
                - alici_adres: str
                - alici_il: str
                - alici_ilce: str
                - paket_agirlik_kg: Decimal
                - gonderen_ad: str (opsiyonel)
                - gonderen_telefon: str (opsiyonel)
                - servis_kodu: str (opsiyonel)
                - aciklama: str (opsiyonel)
        
        Returns:
            Dict[str, Any]: Etiket oluşturma sonucu
                - takip_no: str (başarılı ise)
                - etiket_verisi_base64: str (opsiyonel, etiket PDF'i)
                - durum: str (OLUSTURULDU/HATA)
                - mesaj: str (hata mesajı veya bilgi)
        
        Raises:
            EntegrasyonHatasi: Taşıyıcı API hatası durumunda
        """
        pass
    
    @abstractmethod
    def durum_sorgula(self, takip_no: str) -> Dict[str, Any]:
        """
        Takip numarası ile kargo durumunu sorgular.
        
        Args:
            takip_no: Sorgulanacak takip numarası
        
        Returns:
            Dict[str, Any]: Durum sorgulama sonucu
                - durum: str (BILINMIYOR/KARGODA/TESLIM/IPTAL)
                - aciklama: str (durum açıklaması)
                - zaman: datetime (opsiyonel, durum zamanı)
        
        Raises:
            EntegrasyonHatasi: Taşıyıcı API hatası durumunda
        """
        pass
    
    def get_tasiyici_adi(self) -> str:
        """
        Taşıyıcının adını döndürür.
        
        Returns:
            str: Taşıyıcı adı
        """
        return self.__class__.__name__