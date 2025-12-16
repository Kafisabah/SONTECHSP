# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.database.models.offline_kuyruk
# Description: POS Offline Kuyruk veri modeli
# Changelog:
# - İlk oluşturma

"""
POS Offline Kuyruk Veri Modeli

Bu modül POS sisteminin offline kuyruk veri modelini içerir.
Network kesintilerinde işlemlerin geçici olarak saklandığı SQLite tabanlı kuyruk sistemi.
"""

from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import (
    Integer, String, Enum as SQLEnum, DateTime, Text, JSON,
    Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from sontechsp.uygulama.veritabani.taban import Taban
from sontechsp.uygulama.moduller.pos.arayuzler import IslemTuru, KuyrukDurum


class OfflineKuyruk(Taban):
    """
    Offline kuyruk modeli
    
    Network bağlantısı olmadığında işlemlerin geçici olarak saklandığı kuyruk sistemi.
    SQLite tabanlı olarak çalışır ve network geri geldiğinde senkronize edilir.
    """
    
    __tablename__ = 'pos_offline_kuyruk'
    
    # Temel alanlar
    islem_turu: Mapped[IslemTuru] = mapped_column(
        SQLEnum(IslemTuru),
        nullable=False,
        comment="İşlem türü (satış, iade, stok düşümü)"
    )
    
    durum: Mapped[KuyrukDurum] = mapped_column(
        SQLEnum(KuyrukDurum),
        nullable=False,
        default=KuyrukDurum.BEKLEMEDE,
        comment="Kuyruk durumu"
    )
    
    veri: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        comment="İşlem verisi (JSON formatında)"
    )
    
    # Terminal ve kullanıcı bilgileri
    terminal_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Terminal kimliği"
    )
    
    kasiyer_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Kasiyer kimliği"
    )
    
    # Zaman bilgileri
    islem_tarihi: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Orijinal işlem tarihi"
    )
    
    son_deneme_tarihi: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Son deneme tarihi"
    )
    
    tamamlanma_tarihi: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Tamamlanma tarihi"
    )
    
    # Hata yönetimi
    deneme_sayisi: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Deneme sayısı"
    )
    
    max_deneme_sayisi: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        comment="Maksimum deneme sayısı"
    )
    
    hata_mesaji: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Son hata mesajı"
    )
    
    # Öncelik ve sıralama
    oncelik: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="İşlem önceliği (1=yüksek, 5=düşük)"
    )
    
    # Ek bilgiler
    notlar: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="İşlem notları"
    )
    
    # Kısıtlamalar
    __table_args__ = (
        CheckConstraint(
            'terminal_id > 0',
            name='ck_offline_kuyruk_terminal_id_pozitif'
        ),
        CheckConstraint(
            'kasiyer_id > 0',
            name='ck_offline_kuyruk_kasiyer_id_pozitif'
        ),
        CheckConstraint(
            'deneme_sayisi >= 0',
            name='ck_offline_kuyruk_deneme_sayisi_pozitif'
        ),
        CheckConstraint(
            'max_deneme_sayisi > 0',
            name='ck_offline_kuyruk_max_deneme_sayisi_pozitif'
        ),
        CheckConstraint(
            'oncelik BETWEEN 1 AND 5',
            name='ck_offline_kuyruk_oncelik_aralik'
        ),
        Index('ix_offline_kuyruk_durum', 'durum'),
        Index('ix_offline_kuyruk_islem_turu', 'islem_turu'),
        Index('ix_offline_kuyruk_terminal_id', 'terminal_id'),
        Index('ix_offline_kuyruk_kasiyer_id', 'kasiyer_id'),
        Index('ix_offline_kuyruk_islem_tarihi', 'islem_tarihi'),
        Index('ix_offline_kuyruk_oncelik', 'oncelik'),
        Index('ix_offline_kuyruk_durum_oncelik', 'durum', 'oncelik'),
    )
    
    def __repr__(self) -> str:
        return (f"<OfflineKuyruk(id={self.id}, islem_turu={self.islem_turu.value}, "
                f"durum={self.durum.value}, deneme_sayisi={self.deneme_sayisi})>")
    
    def beklemede_mi(self) -> bool:
        """İşlem beklemede mi kontrol eder"""
        return self.durum == KuyrukDurum.BEKLEMEDE
    
    def isleniyor_mu(self) -> bool:
        """İşlem işleniyor mu kontrol eder"""
        return self.durum == KuyrukDurum.ISLENIYOR
    
    def tamamlandi_mi(self) -> bool:
        """İşlem tamamlandı mı kontrol eder"""
        return self.durum == KuyrukDurum.TAMAMLANDI
    
    def hata_durumunda_mi(self) -> bool:
        """İşlem hata durumunda mı kontrol eder"""
        return self.durum == KuyrukDurum.HATA
    
    def tekrar_denenebilir_mi(self) -> bool:
        """İşlem tekrar denenebilir mi kontrol eder"""
        return (self.durum in [KuyrukDurum.BEKLEMEDE, KuyrukDurum.HATA] and 
                self.deneme_sayisi < self.max_deneme_sayisi)
    
    def max_deneme_asildi_mi(self) -> bool:
        """Maksimum deneme sayısı aşıldı mı kontrol eder"""
        return self.deneme_sayisi >= self.max_deneme_sayisi
    
    def deneme_artir(self) -> None:
        """Deneme sayısını artırır ve son deneme tarihini günceller"""
        self.deneme_sayisi += 1
        self.son_deneme_tarihi = datetime.now()
    
    def isleme_basla(self) -> None:
        """İşlemi işleniyor durumuna getirir"""
        self.durum = KuyrukDurum.ISLENIYOR
        self.son_deneme_tarihi = datetime.now()
    
    def tamamla(self) -> None:
        """İşlemi tamamlandı durumuna getirir"""
        self.durum = KuyrukDurum.TAMAMLANDI
        self.tamamlanma_tarihi = datetime.now()
        self.hata_mesaji = None
    
    def hata_durumuna_getir(self, hata_mesaji: str) -> None:
        """İşlemi hata durumuna getirir"""
        self.durum = KuyrukDurum.HATA
        self.hata_mesaji = hata_mesaji
        self.son_deneme_tarihi = datetime.now()
    
    def beklemede_durumuna_getir(self) -> None:
        """İşlemi beklemede durumuna getirir (tekrar deneme için)"""
        if self.tekrar_denenebilir_mi():
            self.durum = KuyrukDurum.BEKLEMEDE
    
    def veri_getir(self, anahtar: str, varsayilan: Any = None) -> Any:
        """Veri JSON'ından belirli bir anahtarın değerini getirir"""
        return self.veri.get(anahtar, varsayilan) if self.veri else varsayilan
    
    def veri_guncelle(self, anahtar: str, deger: Any) -> None:
        """Veri JSON'ına yeni anahtar-değer çifti ekler veya günceller"""
        if not self.veri:
            self.veri = {}
        self.veri[anahtar] = deger
    
    def gecikme_suresi_hesapla(self) -> int:
        """Bir sonraki deneme için gecikme süresini hesaplar (saniye)"""
        # Exponential backoff: 2^deneme_sayisi * 60 saniye (max 30 dakika)
        gecikme = min(2 ** self.deneme_sayisi * 60, 1800)
        return gecikme
    
    def satis_verisi_mi(self) -> bool:
        """Satış verisi mi kontrol eder"""
        return self.islem_turu == IslemTuru.SATIS
    
    def iade_verisi_mi(self) -> bool:
        """İade verisi mi kontrol eder"""
        return self.islem_turu == IslemTuru.IADE
    
    def stok_dusumu_verisi_mi(self) -> bool:
        """Stok düşümü verisi mi kontrol eder"""
        return self.islem_turu == IslemTuru.STOK_DUSUMU


# Model validasyon fonksiyonları
def offline_kuyruk_validasyon(kuyruk: OfflineKuyruk) -> List[str]:
    """
    Offline kuyruk validasyon kuralları
    
    Args:
        kuyruk: Validasyon yapılacak kuyruk kaydı
        
    Returns:
        Hata mesajları listesi (boş liste = geçerli)
    """
    hatalar = []
    
    if kuyruk.terminal_id <= 0:
        hatalar.append("Terminal ID pozitif olmalıdır")
    
    if kuyruk.kasiyer_id <= 0:
        hatalar.append("Kasiyer ID pozitif olmalıdır")
    
    if kuyruk.deneme_sayisi < 0:
        hatalar.append("Deneme sayısı negatif olamaz")
    
    if kuyruk.max_deneme_sayisi <= 0:
        hatalar.append("Maksimum deneme sayısı pozitif olmalıdır")
    
    if kuyruk.oncelik < 1 or kuyruk.oncelik > 5:
        hatalar.append("Öncelik 1-5 arasında olmalıdır")
    
    if not kuyruk.veri:
        hatalar.append("İşlem verisi boş olamaz")
    
    # Durum kontrolü
    if kuyruk.durum == KuyrukDurum.TAMAMLANDI:
        if not kuyruk.tamamlanma_tarihi:
            hatalar.append("Tamamlanan işlem için tamamlanma tarihi gereklidir")
    
    if kuyruk.durum == KuyrukDurum.HATA:
        if not kuyruk.hata_mesaji:
            hatalar.append("Hata durumundaki işlem için hata mesajı gereklidir")
    
    # Deneme sayısı kontrolü
    if kuyruk.deneme_sayisi > kuyruk.max_deneme_sayisi:
        hatalar.append("Deneme sayısı maksimum deneme sayısını aşamaz")
    
    return hatalar


# Yardımcı fonksiyonlar
def satis_kuyruk_verisi_olustur(satis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Satış işlemi için kuyruk verisi oluşturur
    
    Args:
        satis_data: Satış verisi
        
    Returns:
        Kuyruk için formatlanmış veri
    """
    return {
        'islem_turu': 'satis',
        'satis_id': satis_data.get('satis_id'),
        'sepet_id': satis_data.get('sepet_id'),
        'toplam_tutar': str(satis_data.get('toplam_tutar', '0.00')),
        'odemeler': satis_data.get('odemeler', []),
        'fis_no': satis_data.get('fis_no'),
        'timestamp': datetime.now().isoformat()
    }


def iade_kuyruk_verisi_olustur(iade_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    İade işlemi için kuyruk verisi oluşturur
    
    Args:
        iade_data: İade verisi
        
    Returns:
        Kuyruk için formatlanmış veri
    """
    return {
        'islem_turu': 'iade',
        'iade_id': iade_data.get('iade_id'),
        'orijinal_satis_id': iade_data.get('orijinal_satis_id'),
        'toplam_tutar': str(iade_data.get('toplam_tutar', '0.00')),
        'neden': iade_data.get('neden'),
        'satirlar': iade_data.get('satirlar', []),
        'timestamp': datetime.now().isoformat()
    }


def stok_dusumu_kuyruk_verisi_olustur(stok_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stok düşümü işlemi için kuyruk verisi oluşturur
    
    Args:
        stok_data: Stok düşümü verisi
        
    Returns:
        Kuyruk için formatlanmış veri
    """
    return {
        'islem_turu': 'stok_dusumu',
        'urun_id': stok_data.get('urun_id'),
        'adet': stok_data.get('adet'),
        'islem_referansi': stok_data.get('islem_referansi'),
        'timestamp': datetime.now().isoformat()
    }