# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.database.models.satis
# Description: POS Satis ve SatisOdeme veri modelleri
# Changelog:
# - İlk oluşturma

"""
POS Satış Veri Modelleri

Bu modül POS sisteminin satış ve ödeme veri modellerini içerir.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Integer, String, Numeric, ForeignKey, Enum as SQLEnum,
    Index, CheckConstraint, UniqueConstraint, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sontechsp.uygulama.veritabani.taban import Taban
from sontechsp.uygulama.moduller.pos.arayuzler import SatisDurum, OdemeTuru


class Satis(Taban):
    """
    Satış modeli
    
    Tamamlanan satış işlemlerinin kaydını tutar.
    Her satış bir sepetten oluşturulur ve ödeme bilgilerini içerir.
    """
    
    __tablename__ = 'pos_satis'
    
    # İlişki alanları
    sepet_id: Mapped[int] = mapped_column(
        ForeignKey('pos_sepet.id'),
        nullable=False,
        comment="Bağlı olduğu sepet kimliği"
    )
    
    # Temel alanlar
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
    
    satis_tarihi: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Satış tarihi"
    )
    
    toplam_tutar: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Satış toplam tutarı"
    )
    
    indirim_tutari: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        default=Decimal('0.00'),
        comment="Uygulanan indirim tutarı"
    )
    
    durum: Mapped[SatisDurum] = mapped_column(
        SQLEnum(SatisDurum),
        nullable=False,
        default=SatisDurum.BEKLEMEDE,
        comment="Satış durumu"
    )
    
    fis_no: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Fiş numarası"
    )
    
    musteri_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Müşteri kimliği (opsiyonel)"
    )
    
    notlar: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Satış notları"
    )
    
    # İlişkiler
    odemeler: Mapped[List["SatisOdeme"]] = relationship(
        "SatisOdeme",
        back_populates="satis",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Kısıtlamalar
    __table_args__ = (
        CheckConstraint(
            'toplam_tutar >= 0',
            name='ck_satis_toplam_tutar_pozitif'
        ),
        CheckConstraint(
            'indirim_tutari >= 0',
            name='ck_satis_indirim_tutari_pozitif'
        ),
        CheckConstraint(
            'terminal_id > 0',
            name='ck_satis_terminal_id_pozitif'
        ),
        CheckConstraint(
            'kasiyer_id > 0',
            name='ck_satis_kasiyer_id_pozitif'
        ),
        UniqueConstraint(
            'fis_no',
            name='uq_satis_fis_no'
        ),
        Index('ix_satis_terminal_id', 'terminal_id'),
        Index('ix_satis_kasiyer_id', 'kasiyer_id'),
        Index('ix_satis_satis_tarihi', 'satis_tarihi'),
        Index('ix_satis_durum', 'durum'),
        Index('ix_satis_fis_no', 'fis_no'),
        Index('ix_satis_musteri_id', 'musteri_id'),
    )
    
    def __repr__(self) -> str:
        return (f"<Satis(id={self.id}, fis_no={self.fis_no}, "
                f"durum={self.durum.value}, toplam_tutar={self.toplam_tutar})>")
    
    def net_tutar_hesapla(self) -> Decimal:
        """Net tutarı hesaplar (toplam - indirim)"""
        indirim = self.indirim_tutari or Decimal('0.00')
        return self.toplam_tutar - indirim
    
    def toplam_odeme_tutari(self) -> Decimal:
        """Toplam ödeme tutarını hesaplar"""
        if not self.odemeler:
            return Decimal('0.00')
        return sum(odeme.tutar for odeme in self.odemeler)
    
    def odeme_tamamlandi_mi(self) -> bool:
        """Ödeme tamamlandı mı kontrol eder"""
        net_tutar = self.net_tutar_hesapla()
        odeme_tutari = self.toplam_odeme_tutari()
        return abs(net_tutar - odeme_tutari) < Decimal('0.01')
    
    def kalan_tutar(self) -> Decimal:
        """Kalan ödeme tutarını hesaplar"""
        net_tutar = self.net_tutar_hesapla()
        odeme_tutari = self.toplam_odeme_tutari()
        kalan = net_tutar - odeme_tutari
        return max(kalan, Decimal('0.00'))


class SatisOdeme(Taban):
    """
    Satış ödeme modeli
    
    Bir satışa yapılan ödemelerin kaydını tutar.
    Tek veya parçalı ödeme destekler.
    """
    
    __tablename__ = 'pos_satis_odeme'
    
    # İlişki alanları
    satis_id: Mapped[int] = mapped_column(
        ForeignKey('pos_satis.id', ondelete='CASCADE'),
        nullable=False,
        comment="Bağlı olduğu satış kimliği"
    )
    
    # Ödeme bilgileri
    odeme_turu: Mapped[OdemeTuru] = mapped_column(
        SQLEnum(OdemeTuru),
        nullable=False,
        comment="Ödeme türü"
    )
    
    tutar: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Ödeme tutarı"
    )
    
    referans_no: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Ödeme referans numarası (kart, havale vb.)"
    )
    
    odeme_tarihi: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Ödeme tarihi"
    )
    
    # Kart ödemeleri için ek bilgiler
    kart_son_4_hane: Mapped[Optional[str]] = mapped_column(
        String(4),
        nullable=True,
        comment="Kart son 4 hanesi"
    )
    
    banka_kodu: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="Banka kodu"
    )
    
    taksit_sayisi: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=1,
        comment="Taksit sayısı"
    )
    
    # İlişkiler
    satis: Mapped["Satis"] = relationship(
        "Satis",
        back_populates="odemeler"
    )
    
    # Kısıtlamalar
    __table_args__ = (
        CheckConstraint(
            'tutar > 0',
            name='ck_satis_odeme_tutar_pozitif'
        ),
        CheckConstraint(
            'taksit_sayisi > 0',
            name='ck_satis_odeme_taksit_sayisi_pozitif'
        ),
        CheckConstraint(
            "kart_son_4_hane IS NULL OR length(kart_son_4_hane) = 4",
            name='ck_satis_odeme_kart_son_4_hane_uzunluk'
        ),
        Index('ix_satis_odeme_satis_id', 'satis_id'),
        Index('ix_satis_odeme_odeme_turu', 'odeme_turu'),
        Index('ix_satis_odeme_odeme_tarihi', 'odeme_tarihi'),
        Index('ix_satis_odeme_referans_no', 'referans_no'),
    )
    
    def __repr__(self) -> str:
        return (f"<SatisOdeme(id={self.id}, satis_id={self.satis_id}, "
                f"odeme_turu={self.odeme_turu.value}, tutar={self.tutar})>")
    
    def kart_odeme_mi(self) -> bool:
        """Kart ödemesi mi kontrol eder"""
        return self.odeme_turu == OdemeTuru.KART
    
    def nakit_odeme_mi(self) -> bool:
        """Nakit ödemesi mi kontrol eder"""
        return self.odeme_turu == OdemeTuru.NAKIT
    
    def taksitli_mi(self) -> bool:
        """Taksitli ödeme mi kontrol eder"""
        return self.taksit_sayisi and self.taksit_sayisi > 1


# Model validasyon fonksiyonları
def satis_validasyon(satis: Satis) -> List[str]:
    """
    Satış validasyon kuralları
    
    Args:
        satis: Validasyon yapılacak satış
        
    Returns:
        Hata mesajları listesi (boş liste = geçerli)
    """
    hatalar = []
    
    if satis.terminal_id <= 0:
        hatalar.append("Terminal ID pozitif olmalıdır")
    
    if satis.kasiyer_id <= 0:
        hatalar.append("Kasiyer ID pozitif olmalıdır")
    
    if satis.toplam_tutar < 0:
        hatalar.append("Toplam tutar negatif olamaz")
    
    if satis.indirim_tutari and satis.indirim_tutari < 0:
        hatalar.append("İndirim tutarı negatif olamaz")
    
    if satis.indirim_tutari and satis.indirim_tutari > satis.toplam_tutar:
        hatalar.append("İndirim tutarı toplam tutardan büyük olamaz")
    
    if satis.fis_no and len(satis.fis_no.strip()) == 0:
        hatalar.append("Fiş numarası boş olamaz")
    
    if satis.musteri_id and satis.musteri_id <= 0:
        hatalar.append("Müşteri ID pozitif olmalıdır")
    
    # Durum kontrolü
    if satis.durum == SatisDurum.TAMAMLANDI:
        if not satis.fis_no:
            hatalar.append("Tamamlanan satış için fiş numarası gereklidir")
        
        if not satis.odeme_tamamlandi_mi():
            hatalar.append("Tamamlanan satış için ödeme tamamlanmış olmalıdır")
    
    return hatalar


def satis_odeme_validasyon(odeme: SatisOdeme) -> List[str]:
    """
    Satış ödeme validasyon kuralları
    
    Args:
        odeme: Validasyon yapılacak ödeme
        
    Returns:
        Hata mesajları listesi (boş liste = geçerli)
    """
    hatalar = []
    
    if odeme.tutar <= 0:
        hatalar.append("Ödeme tutarı pozitif olmalıdır")
    
    if odeme.taksit_sayisi and odeme.taksit_sayisi <= 0:
        hatalar.append("Taksit sayısı pozitif olmalıdır")
    
    # Kart ödemesi kontrolleri
    if odeme.odeme_turu == OdemeTuru.KART:
        if odeme.kart_son_4_hane and len(odeme.kart_son_4_hane) != 4:
            hatalar.append("Kart son 4 hanesi 4 karakter olmalıdır")
        
        if odeme.kart_son_4_hane and not odeme.kart_son_4_hane.isdigit():
            hatalar.append("Kart son 4 hanesi sadece rakam içermelidir")
    
    # Referans numarası kontrolleri
    if odeme.odeme_turu in [OdemeTuru.KART, OdemeTuru.HAVALE]:
        if not odeme.referans_no or len(odeme.referans_no.strip()) == 0:
            hatalar.append(f"{odeme.odeme_turu.value} ödemesi için referans numarası gereklidir")
    
    return hatalar