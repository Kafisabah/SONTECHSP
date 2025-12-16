# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.database.models.sepet
# Description: POS Sepet ve SepetSatiri veri modelleri
# Changelog:
# - İlk oluşturma

"""
POS Sepet Veri Modelleri

Bu modül POS sisteminin sepet ve sepet satırı veri modellerini içerir.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Integer, String, Numeric, ForeignKey, Enum as SQLEnum,
    Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sontechsp.uygulama.veritabani.taban import Taban
from sontechsp.uygulama.moduller.pos.arayuzler import SepetDurum


class Sepet(Taban):
    """
    Sepet modeli
    
    Müşterinin satın almak istediği ürünlerin geçici olarak tutulduğu liste.
    Her terminal için aktif sepet bulunur.
    """
    
    __tablename__ = 'pos_sepet'
    
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
    
    durum: Mapped[SepetDurum] = mapped_column(
        SQLEnum(SepetDurum),
        nullable=False,
        default=SepetDurum.AKTIF,
        comment="Sepet durumu"
    )
    
    toplam_tutar: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00'),
        comment="Sepet toplam tutarı"
    )
    
    indirim_tutari: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        default=Decimal('0.00'),
        comment="Uygulanan indirim tutarı"
    )
    
    # İlişkiler
    satirlar: Mapped[List["SepetSatiri"]] = relationship(
        "SepetSatiri",
        back_populates="sepet",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Kısıtlamalar
    __table_args__ = (
        CheckConstraint(
            'toplam_tutar >= 0',
            name='ck_sepet_toplam_tutar_pozitif'
        ),
        CheckConstraint(
            'indirim_tutari >= 0',
            name='ck_sepet_indirim_tutari_pozitif'
        ),
        CheckConstraint(
            'terminal_id > 0',
            name='ck_sepet_terminal_id_pozitif'
        ),
        CheckConstraint(
            'kasiyer_id > 0',
            name='ck_sepet_kasiyer_id_pozitif'
        ),
        Index('ix_sepet_terminal_durum', 'terminal_id', 'durum'),
        Index('ix_sepet_kasiyer', 'kasiyer_id'),
        Index('ix_sepet_olusturma_tarihi', 'olusturma_tarihi'),
    )
    
    def __repr__(self) -> str:
        return (f"<Sepet(id={self.id}, terminal_id={self.terminal_id}, "
                f"durum={self.durum.value}, toplam_tutar={self.toplam_tutar})>")
    
    def net_tutar_hesapla(self) -> Decimal:
        """Net tutarı hesaplar (toplam - indirim)"""
        indirim = self.indirim_tutari or Decimal('0.00')
        return self.toplam_tutar - indirim
    
    def satir_sayisi(self) -> int:
        """Sepetteki satır sayısını döner"""
        return len(self.satirlar) if self.satirlar else 0
    
    def toplam_adet(self) -> int:
        """Sepetteki toplam ürün adedini döner"""
        if not self.satirlar:
            return 0
        return sum(satir.adet for satir in self.satirlar)


class SepetSatiri(Taban):
    """
    Sepet satırı modeli
    
    Sepetteki her ürün için ayrı bir satır oluşturulur.
    Aynı üründen birden fazla adet varsa tek satırda tutulur.
    """
    
    __tablename__ = 'pos_sepet_satiri'
    
    # İlişki alanları
    sepet_id: Mapped[int] = mapped_column(
        ForeignKey('pos_sepet.id', ondelete='CASCADE'),
        nullable=False,
        comment="Bağlı olduğu sepet kimliği"
    )
    
    # Ürün bilgileri
    urun_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Ürün kimliği"
    )
    
    barkod: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Ürün barkodu"
    )
    
    urun_adi: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Ürün adı (snapshot)"
    )
    
    # Miktar ve fiyat bilgileri
    adet: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Ürün adedi"
    )
    
    birim_fiyat: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Birim fiyat"
    )
    
    indirim_tutari: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        default=Decimal('0.00'),
        comment="Satır indirim tutarı"
    )
    
    toplam_tutar: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Satır toplam tutarı"
    )
    
    # İlişkiler
    sepet: Mapped["Sepet"] = relationship(
        "Sepet",
        back_populates="satirlar"
    )
    
    # Kısıtlamalar
    __table_args__ = (
        CheckConstraint(
            'adet > 0',
            name='ck_sepet_satiri_adet_pozitif'
        ),
        CheckConstraint(
            'birim_fiyat >= 0',
            name='ck_sepet_satiri_birim_fiyat_pozitif'
        ),
        CheckConstraint(
            'indirim_tutari >= 0',
            name='ck_sepet_satiri_indirim_tutari_pozitif'
        ),
        CheckConstraint(
            'toplam_tutar >= 0',
            name='ck_sepet_satiri_toplam_tutar_pozitif'
        ),
        CheckConstraint(
            'urun_id > 0',
            name='ck_sepet_satiri_urun_id_pozitif'
        ),
        UniqueConstraint(
            'sepet_id', 'urun_id',
            name='uq_sepet_satiri_sepet_urun'
        ),
        Index('ix_sepet_satiri_sepet_id', 'sepet_id'),
        Index('ix_sepet_satiri_urun_id', 'urun_id'),
        Index('ix_sepet_satiri_barkod', 'barkod'),
    )
    
    def __repr__(self) -> str:
        return (f"<SepetSatiri(id={self.id}, sepet_id={self.sepet_id}, "
                f"urun_id={self.urun_id}, adet={self.adet}, "
                f"toplam_tutar={self.toplam_tutar})>")
    
    def net_tutar_hesapla(self) -> Decimal:
        """Net tutarı hesaplar (toplam - indirim)"""
        indirim = self.indirim_tutari or Decimal('0.00')
        return self.toplam_tutar - indirim
    
    def birim_net_fiyat_hesapla(self) -> Decimal:
        """Birim net fiyatı hesaplar"""
        net_tutar = self.net_tutar_hesapla()
        return net_tutar / Decimal(str(self.adet))
    
    def toplam_tutar_guncelle(self) -> None:
        """Toplam tutarı adet ve birim fiyata göre günceller"""
        self.toplam_tutar = Decimal(str(self.adet)) * self.birim_fiyat


# Model validasyon fonksiyonları
def sepet_validasyon(sepet: Sepet) -> List[str]:
    """
    Sepet validasyon kuralları
    
    Args:
        sepet: Validasyon yapılacak sepet
        
    Returns:
        Hata mesajları listesi (boş liste = geçerli)
    """
    hatalar = []
    
    if sepet.terminal_id <= 0:
        hatalar.append("Terminal ID pozitif olmalıdır")
    
    if sepet.kasiyer_id <= 0:
        hatalar.append("Kasiyer ID pozitif olmalıdır")
    
    if sepet.toplam_tutar < 0:
        hatalar.append("Toplam tutar negatif olamaz")
    
    if sepet.indirim_tutari and sepet.indirim_tutari < 0:
        hatalar.append("İndirim tutarı negatif olamaz")
    
    if sepet.indirim_tutari and sepet.indirim_tutari > sepet.toplam_tutar:
        hatalar.append("İndirim tutarı toplam tutardan büyük olamaz")
    
    return hatalar


def sepet_satiri_validasyon(satir: SepetSatiri) -> List[str]:
    """
    Sepet satırı validasyon kuralları
    
    Args:
        satir: Validasyon yapılacak sepet satırı
        
    Returns:
        Hata mesajları listesi (boş liste = geçerli)
    """
    hatalar = []
    
    if satir.urun_id <= 0:
        hatalar.append("Ürün ID pozitif olmalıdır")
    
    if satir.adet <= 0:
        hatalar.append("Adet pozitif olmalıdır")
    
    if satir.birim_fiyat < 0:
        hatalar.append("Birim fiyat negatif olamaz")
    
    if satir.toplam_tutar < 0:
        hatalar.append("Toplam tutar negatif olamaz")
    
    if satir.indirim_tutari and satir.indirim_tutari < 0:
        hatalar.append("İndirim tutarı negatif olamaz")
    
    if satir.indirim_tutari and satir.indirim_tutari > satir.toplam_tutar:
        hatalar.append("İndirim tutarı toplam tutardan büyük olamaz")
    
    if not satir.barkod or len(satir.barkod.strip()) == 0:
        hatalar.append("Barkod boş olamaz")
    
    if not satir.urun_adi or len(satir.urun_adi.strip()) == 0:
        hatalar.append("Ürün adı boş olamaz")
    
    # Hesaplanan toplam tutar kontrolü
    beklenen_toplam = Decimal(str(satir.adet)) * satir.birim_fiyat
    if abs(satir.toplam_tutar - beklenen_toplam) > Decimal('0.01'):
        hatalar.append("Toplam tutar hesaplaması hatalı")
    
    return hatalar