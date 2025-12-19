# Version: 0.1.2
# Last Update: 2024-12-19
# Module: pos.arayuzler
# Description: POS modülü temel arayüzleri (interfaces)
# Changelog:
# - İlk oluşturma
# - Duplicate method düzeltmesi ve type hint iyileştirmeleri
# - Import düzenlemesi ve kod kalitesi iyileştirmeleri

"""
POS Modülü Temel Arayüzleri

Bu modül POS sisteminin temel arayüzlerini (interfaces) tanımlar.
Katmanlar arası sözleşmeleri belirler.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum


# Enum tanımları
class SepetDurum(Enum):
    """Sepet durumları"""

    AKTIF = "aktif"
    BEKLEMEDE = "beklemede"
    TAMAMLANDI = "tamamlandi"
    IPTAL = "iptal"


class SatisDurum(Enum):
    """Satış durumları"""

    BEKLEMEDE = "beklemede"
    TAMAMLANDI = "tamamlandi"
    IPTAL = "iptal"
    IADE = "iade"


class OdemeTuru(Enum):
    """Ödeme türleri"""

    NAKIT = "nakit"
    KART = "kart"
    HAVALE = "havale"
    PARCALI = "parcali"
    ACIK_HESAP = "acik_hesap"
    CEKIRDEK = "cekirdek"


class IslemTuru(Enum):
    """Offline kuyruk işlem türleri"""

    SATIS = "satis"
    IADE = "iade"
    STOK_DUSUMU = "stok_dusumu"


class KuyrukDurum(Enum):
    """Offline kuyruk durumları"""

    BEKLEMEDE = "beklemede"
    ISLENIYOR = "isleniyor"
    TAMAMLANDI = "tamamlandi"
    HATA = "hata"


class StokKilitTuru(Enum):
    """Stok kilit türleri"""

    REZERVASYON = "rezervasyon"
    SATIS = "satis"
    TRANSFER = "transfer"


# Repository Arayüzleri
class ISepetRepository(ABC):
    """Sepet repository arayüzü"""

    @abstractmethod
    def sepet_olustur(self, terminal_id: int, kasiyer_id: int) -> int:
        """Yeni sepet oluşturur"""
        pass

    @abstractmethod
    def sepet_getir(self, sepet_id: int) -> Optional[Dict[str, Any]]:
        """Sepet bilgilerini getirir"""
        pass

    @abstractmethod
    def sepet_satiri_ekle(self, sepet_id: int, urun_id: int, barkod: str, adet: int, birim_fiyat: Decimal) -> int:
        """Sepete satır ekler"""
        pass

    @abstractmethod
    def sepet_satiri_guncelle(self, satir_id: int, adet: int) -> bool:
        """Sepet satırını günceller"""
        pass

    @abstractmethod
    def sepet_satiri_sil(self, satir_id: int) -> bool:
        """Sepet satırını siler"""
        pass

    @abstractmethod
    def sepet_bosalt(self, sepet_id: int) -> bool:
        """Sepeti boşaltır"""
        pass


class ISatisRepository(ABC):
    """Satış repository arayüzü"""

    @abstractmethod
    def satis_olustur(self, sepet_id: int, terminal_id: int, kasiyer_id: int, toplam_tutar: Decimal) -> int:
        """Yeni satış kaydı oluşturur"""
        pass

    @abstractmethod
    def satis_getir(self, satis_id: int) -> Optional[Dict[str, Any]]:
        """Satış bilgilerini getirir"""
        pass

    @abstractmethod
    def satis_odeme_ekle(
        self, satis_id: int, odeme_turu: OdemeTuru, tutar: Decimal, referans_no: Optional[str] = None
    ) -> int:
        """Satışa ödeme ekler"""
        pass

    @abstractmethod
    def satis_tamamla(self, satis_id: int, fis_no: str) -> bool:
        """Satışı tamamlar"""
        pass


class IIadeRepository(ABC):
    """İade repository arayüzü"""

    @abstractmethod
    def iade_olustur(self, orijinal_satis_id: int, terminal_id: int, kasiyer_id: int, neden: str) -> int:
        """Yeni iade kaydı oluşturur"""
        pass

    @abstractmethod
    def iade_satiri_ekle(self, iade_id: int, urun_id: int, adet: int, birim_fiyat: Decimal) -> int:
        """İade satırı ekler"""
        pass

    @abstractmethod
    def iade_tamamla(self, iade_id: int) -> bool:
        """İadeyi tamamlar"""
        pass


class IOfflineKuyrukRepository(ABC):
    """Offline kuyruk repository arayüzü"""

    @abstractmethod
    def kuyruga_ekle(
        self,
        islem_turu: IslemTuru,
        veri: Dict[str, Any],
        terminal_id: Optional[int] = None,
        kasiyer_id: Optional[int] = None,
        oncelik: int = 1,
        notlar: Optional[str] = None,
    ) -> int:
        """Kuyruğa işlem ekler"""
        pass

    @abstractmethod
    def bekleyen_islemler(self) -> List[Dict[str, Any]]:
        """Bekleyen işlemleri getirir"""
        pass

    @abstractmethod
    def islem_tamamla(self, kuyruk_id: int) -> bool:
        """İşlemi tamamlandı olarak işaretler"""
        pass

    @abstractmethod
    def islem_hata(self, kuyruk_id: int, hata_mesaji: str) -> bool:
        """İşlemi hatalı olarak işaretler"""
        pass

    @abstractmethod
    def kuyruk_temizle(self, gun_sayisi: int = 7) -> bool:
        """Eski kuyruk kayıtlarını temizler"""
        pass

    @abstractmethod
    def bekleyen_kuyruk_listesi(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Bekleyen kuyruk listesini getirir"""
        pass

    @abstractmethod
    def kuyruk_durum_guncelle(self, kuyruk_id: int, durum: KuyrukDurum) -> bool:
        """Kuyruk durumunu günceller"""
        pass

    @abstractmethod
    def kuyruk_deneme_artir(self, kuyruk_id: int, hata_mesaji: str) -> bool:
        """Kuyruk deneme sayısını artırır"""
        pass

    @abstractmethod
    def kuyruk_istatistikleri(self, terminal_id: Optional[int] = None) -> Dict[str, Any]:
        """Kuyruk istatistiklerini getirir"""
        pass

    @abstractmethod
    def hata_durumundaki_kuyruklar(self, terminal_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Hata durumundaki kuyrukları getirir"""
        pass


# Service Arayüzleri
class ISepetService(ABC):
    """Sepet service arayüzü"""

    @abstractmethod
    def yeni_sepet_olustur(self, terminal_id: int, kasiyer_id: int) -> int:
        """Yeni sepet oluşturur"""
        pass

    @abstractmethod
    def barkod_ekle(self, sepet_id: int, barkod: str) -> bool:
        """Barkod ile ürün ekler"""
        pass

    @abstractmethod
    def urun_adedi_degistir(self, satir_id: int, yeni_adet: int) -> bool:
        """Ürün adedini değiştirir"""
        pass

    @abstractmethod
    def indirim_uygula(self, sepet_id: int, indirim_tutari: Decimal) -> bool:
        """İndirim uygular"""
        pass

    @abstractmethod
    def sepet_bosalt(self, sepet_id: int) -> bool:
        """Sepeti boşaltır"""
        pass


class IOdemeService(ABC):
    """Ödeme service arayüzü"""

    @abstractmethod
    def tek_odeme_yap(self, sepet_id: int, odeme_turu: OdemeTuru, tutar: Decimal) -> bool:
        """Tek ödeme işlemi yapar"""
        pass

    @abstractmethod
    def parcali_odeme_yap(self, sepet_id: int, odemeler: List[Dict[str, Any]]) -> bool:
        """Parçalı ödeme işlemi yapar"""
        pass


class IIadeService(ABC):
    """İade service arayüzü"""

    @abstractmethod
    def iade_baslat(self, satis_id: int, neden: str) -> int:
        """İade işlemi başlatır"""
        pass

    @abstractmethod
    def iade_kalemi_ekle(self, iade_id: int, urun_id: int, adet: int) -> bool:
        """İade kalemi ekler"""
        pass

    @abstractmethod
    def iade_tamamla(self, iade_id: int) -> bool:
        """İadeyi tamamlar"""
        pass


class IFisService(ABC):
    """Fiş service arayüzü"""

    @abstractmethod
    def satis_fisi_olustur(self, satis_id: int) -> str:
        """Satış fişi oluşturur"""
        pass

    @abstractmethod
    def iade_fisi_olustur(self, iade_id: int) -> str:
        """İade fişi oluşturur"""
        pass

    @abstractmethod
    def fis_yazdir(self, fis_icerik: str) -> bool:
        """Fiş yazdırır"""
        pass


class IOfflineKuyrukService(ABC):
    """Offline kuyruk service arayüzü"""

    @abstractmethod
    def network_durumu_kontrol(self) -> bool:
        """Network durumunu kontrol eder"""
        pass

    @abstractmethod
    def islem_kuyruga_ekle(self, islem_turu: IslemTuru, veri: Dict[str, Any]) -> bool:
        """İşlemi kuyruğa ekler"""
        pass

    @abstractmethod
    def kuyruk_senkronize_et(self) -> int:
        """Kuyruğu senkronize eder, işlenen kayıt sayısını döner"""
        pass


class ISatisIptalService(ABC):
    """Satış iptal service arayüzü"""

    @abstractmethod
    def satis_iptal_et(self, sepet_id: int, iptal_nedeni: str) -> bool:
        """Satış işlemini iptal eder"""
        pass

    @abstractmethod
    def iptal_nedeni_sorgula(self, sepet_id: int) -> str:
        """İptal nedeni sorgular"""
        pass

    @abstractmethod
    def stok_rezervasyon_serbest_birak(self, sepet_id: int) -> bool:
        """Stok rezervasyonunu serbest bırakır"""
        pass

    @abstractmethod
    def yeni_satis_hazirla(self, terminal_id: int, kasiyer_id: int) -> int:
        """Yeni satış için hazırlık yapar"""
        pass


class IStokService(ABC):
    """Stok service arayüzü"""

    @abstractmethod
    def urun_bilgisi_getir(self, barkod: str) -> Optional[Dict[str, Any]]:
        """Barkod ile ürün bilgisi getirir"""
        pass

    @abstractmethod
    def stok_kontrol(self, urun_id: int, adet: int) -> bool:
        """Stok kontrolü yapar"""
        pass

    @abstractmethod
    def stok_rezerve_et(self, urun_id: int, adet: int) -> bool:
        """Stok rezerve eder"""
        pass

    @abstractmethod
    def stok_dusur(self, urun_id: int, adet: int) -> bool:
        """Stok düşer"""
        pass

    @abstractmethod
    def stok_artir(self, urun_id: int, adet: int) -> bool:
        """Stok artırır (iade için)"""
        pass

    @abstractmethod
    def stok_rezervasyon_serbest_birak(self, urun_id: int, adet: int) -> bool:
        """Stok rezervasyonunu serbest bırakır"""
        pass
