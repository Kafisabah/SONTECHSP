# Version: 0.1.0
# Last Update: 2024-12-15
# Module: taban_servis
# Description: SONTECHSP servis katmanı temel sınıfları
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Servis Katmanı Temel Sınıfları

Tüm iş servislerinin türeyeceği temel sınıfları içerir.
Katmanlar arası bağımlılık kurallarını uygular.

Sorumluluklar:
- İş kuralları yürütme
- Repository katmanını çağırma
- Hata yönetimi ve loglama
- Transaction yönetimi
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from contextlib import contextmanager

from sontechsp.uygulama.cekirdek.kayit import logger_al
from sontechsp.uygulama.cekirdek.hatalar import (
    SONTECHSPHatasi, 
    DogrulamaHatasi, 
    EntegrasyonHatasi
)
from sontechsp.uygulama.cekirdek.oturum import oturum_baglamini_al


T = TypeVar('T')


class TabanServis(ABC):
    """
    Tüm servis sınıflarının türeyeceği temel sınıf
    
    Katman kuralları:
    - UI katmanından çağrılır
    - Repository katmanını çağırır
    - Veritabanına doğrudan erişemez
    """
    
    def __init__(self, servis_adi: str):
        """
        Servis başlatıcı
        
        Args:
            servis_adi: Servis adı (loglama için)
        """
        self.servis_adi = servis_adi
        self.logger = logger_al(f"servis.{servis_adi}")
        self.oturum_baglami = oturum_baglamini_al()
        
        self.logger.debug(f"{servis_adi} servisi başlatıldı")
    
    @contextmanager
    def islem_baglami(self, islem_adi: str):
        """
        İşlem bağlamı yöneticisi
        
        Args:
            islem_adi: İşlem adı (loglama için)
        """
        self.logger.info(f"{islem_adi} işlemi başlatıldı")
        
        try:
            yield
            self.logger.info(f"{islem_adi} işlemi başarıyla tamamlandı")
            
        except DogrulamaHatasi as e:
            self.logger.warning(f"{islem_adi} doğrulama hatası: {e}")
            raise
            
        except EntegrasyonHatasi as e:
            self.logger.error(f"{islem_adi} entegrasyon hatası: {e}")
            raise
            
        except Exception as e:
            self.logger.error(f"{islem_adi} beklenmeyen hata: {e}")
            raise SONTECHSPHatasi(f"{islem_adi} işlemi başarısız: {str(e)}")
    
    def _dogrula_oturum(self):
        """Oturum bağlamını doğrular"""
        if not self.oturum_baglami.aktif_mi():
            raise DogrulamaHatasi("Aktif oturum bulunamadı")
        
        if not self.oturum_baglami.kullanici_id:
            raise DogrulamaHatasi("Kullanıcı bilgisi eksik")
    
    def _dogrula_magaza(self):
        """Mağaza bağlamını doğrular"""
        self._dogrula_oturum()
        
        if not self.oturum_baglami.magaza_id:
            raise DogrulamaHatasi("Mağaza seçimi yapılmamış")
    
    def _dogrula_terminal(self):
        """Terminal bağlamını doğrular"""
        self._dogrula_magaza()
        
        if not self.oturum_baglami.terminal_id:
            raise DogrulamaHatasi("Terminal seçimi yapılmamış")


class SorguServisi(TabanServis, Generic[T]):
    """
    Sorgulama işlemleri için temel servis sınıfı
    
    Sadece okuma işlemleri yapar, veri değiştirmez.
    """
    
    def __init__(self, servis_adi: str):
        super().__init__(servis_adi)
    
    @abstractmethod
    def listele(self, filtreler: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        Kayıtları listeler
        
        Args:
            filtreler: Filtreleme kriterleri
            
        Returns:
            List[T]: Kayıt listesi
        """
        pass
    
    @abstractmethod
    def getir(self, kayit_id: int) -> Optional[T]:
        """
        Tek kayıt getirir
        
        Args:
            kayit_id: Kayıt ID'si
            
        Returns:
            Optional[T]: Kayıt veya None
        """
        pass


class KomutServisi(TabanServis, Generic[T]):
    """
    Veri değiştirme işlemleri için temel servis sınıfı
    
    Oluşturma, güncelleme, silme işlemleri yapar.
    """
    
    def __init__(self, servis_adi: str):
        super().__init__(servis_adi)
    
    @abstractmethod
    def olustur(self, veri: Dict[str, Any]) -> T:
        """
        Yeni kayıt oluşturur
        
        Args:
            veri: Kayıt verisi
            
        Returns:
            T: Oluşturulan kayıt
        """
        pass
    
    @abstractmethod
    def guncelle(self, kayit_id: int, veri: Dict[str, Any]) -> T:
        """
        Kayıt günceller
        
        Args:
            kayit_id: Kayıt ID'si
            veri: Güncellenecek veri
            
        Returns:
            T: Güncellenmiş kayıt
        """
        pass
    
    @abstractmethod
    def sil(self, kayit_id: int) -> bool:
        """
        Kayıt siler
        
        Args:
            kayit_id: Kayıt ID'si
            
        Returns:
            bool: Silme başarılı mı
        """
        pass


class IsAkisiServisi(TabanServis):
    """
    Karmaşık iş akışları için temel servis sınıfı
    
    Çoklu adım içeren işlemler için kullanılır.
    """
    
    def __init__(self, servis_adi: str):
        super().__init__(servis_adi)
        self._adimlar: List[str] = []
    
    def adim_ekle(self, adim_adi: str):
        """
        İş akışına adım ekler
        
        Args:
            adim_adi: Adım adı
        """
        self._adimlar.append(adim_adi)
        self.logger.debug(f"İş akışı adımı eklendi: {adim_adi}")
    
    @contextmanager
    def adim_baglami(self, adim_adi: str):
        """
        İş akışı adımı bağlamı
        
        Args:
            adim_adi: Adım adı
        """
        self.logger.info(f"İş akışı adımı başlatıldı: {adim_adi}")
        
        try:
            yield
            self.logger.info(f"İş akışı adımı tamamlandı: {adim_adi}")
            
        except Exception as e:
            self.logger.error(f"İş akışı adımı başarısız: {adim_adi} - {e}")
            raise
    
    def akis_durumunu_logla(self):
        """İş akışı durumunu loglar"""
        self.logger.info(f"İş akışı durumu - Toplam adım: {len(self._adimlar)}")
        for i, adim in enumerate(self._adimlar, 1):
            self.logger.debug(f"  {i}. {adim}")