# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.database.models.iade
# Description: POS İade ve IadeSatiri veri modelleri
# Changelog:
# - İlk oluşturma

"""
POS İade Veri Modelleri

Bu modül POS sisteminin iade ve iade satırı veri modellerini içerir.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Integer, String, Numeric, ForeignKey, Enum as SQLEnum,
    Index, CheckConstraint, DateTime, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sontechsp.uygulama.veritabani.taban import Taban


class Iade(Taban):
    """
    İade modeli
    
    Müşteri tarafından iade edilen ürünlerin kaydını tutar.
    Her iade bir orijinal satışa bağlıdır.
    """
    
    __tablename__ = 'pos_iade'
    
    # İlişki alanları
    orijinal_satis_id: Mapped[int] = mapped_column(
        ForeignKey('pos_satis.id'),
        nullable=False,
        comment="Orijinal satış kimliği"
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
        comment="İadeyi yapan kasiyer kimliği"
    )
    
    iade_tarihi: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="İade tarihi"
    )
    
    toplam_tutar: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="İade toplam tutarı"
    )
    
    neden: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="İade nedeni"
    )
    
    musteri_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Müşteri kimliği (opsiyonel)"
    )
    
    notlar: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="İade notları"
    )
    
    fis_no: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="İade fiş numarası"
    )
    
    # İlişkiler
    satirlar: Mapped[List["IadeSatiri"]] = relationship(
        "IadeSatiri",
        back_populates="iade",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Kısıtlamalar
    __table_args__ = (
        CheckConstraint(
            'toplam_tutar >= 0',
            name='ck_iade_toplam_tutar_pozitif'
        ),
        CheckConstraint(
            'terminal_id > 0',
            name='ck_iade_terminal_id_pozitif'
        ),
        CheckConstraint(
            'kasiyer_id > 0',
            name='ck_iade_kasiyer_id_pozitif'
        ),
        CheckConstraint(
            'orijinal_satis_id > 0',
            name='ck_iade_orijinal_satis_id_pozitif'
        ),
        Index('ix_iade_orijinal_satis_id', 'orijinal_satis_id'),
        Index('ix_iade_terminal_id', 'terminal_id'),
        Index('ix_iade_kasiyer_id', 'kasiyer_id'),
        Index('ix_iade_iade_tarihi', 'iade_tarihi'),
        Index('ix_iade_fis_no', 'fis_no'),
        Index('ix_iade_musteri_id', 'musteri_id'),
    )
    
    def __repr__(self) -> str:
        return (f"<Iade(id={self.id}, orijinal_satis_id={self.orijinal_satis_id}, "
                f"fis_no={self.fis_no}, toplam_tutar={self.toplam_tutar})>")
    
    def satir_sayisi(self) -> int:
        """İadedeki satır sayısını döner"""
        return len(self.satirlar) if self.satirlar else 0
    
    def toplam_adet(self) -> int:
        """İadedeki toplam ürün adedini döner"""
        if not self.satirlar:
            return 0
        return sum(satir.adet for satir in self.satirlar)
    
    def hesaplanan_toplam_tutar(self) -> Decimal:
        """Satırlardan hesaplanan toplam tutarı döner"""
        if not self.satirlar:
            return Decimal('0.00')
        return sum(satir.toplam_tutar for satir in self.satirlar)


class IadeSatiri(Taban):
    """
    İade satırı modeli
    
    İade edilen her ürün için ayrı bir satır oluşturulur.
    """
    
    __tablename__ = 'pos_iade_satiri'
    
    # İlişki alanları
    iade_id: Mapped[int] = mapped_column(
        ForeignKey('pos_iade.id', ondelete='CASCADE'),
        nullable=False,
        comment="Bağlı olduğu iade kimliği"
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
        comment="İade edilen adet"
    )
    
    birim_fiyat: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Birim fiyat (orijinal satış fiyatı)"
    )
    
    toplam_tutar: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Satır toplam tutarı"
    )
    
    # Orijinal satış bilgileri
    orijinal_sepet_satiri_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Orijinal sepet satırı kimliği"
    )
    
    iade_nedeni: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Bu satır için özel iade nedeni"
    )
    
    # İlişkiler
    iade: Mapped["Iade"] = relationship(
        "Iade",
        back_populates="satirlar"
    )
    
    # Kısıtlamalar
    __table_args__ = (
        CheckConstraint(
            'adet > 0',
            name='ck_iade_satiri_adet_pozitif'
        ),
        CheckConstraint(
            'birim_fiyat >= 0',
            name='ck_iade_satiri_birim_fiyat_pozitif'
        ),
        CheckConstraint(
            'toplam_tutar >= 0',
            name='ck_iade_satiri_toplam_tutar_pozitif'
        ),
        CheckConstraint(
            'urun_id > 0',
            name='ck_iade_satiri_urun_id_pozitif'
        ),
        Index('ix_iade_satiri_iade_id', 'iade_id'),
        Index('ix_iade_satiri_urun_id', 'urun_id'),
        Index('ix_iade_satiri_barkod', 'barkod'),
        Index('ix_iade_satiri_orijinal_sepet_satiri_id', 'orijinal_sepet_satiri_id'),
    )
    
    def __repr__(self) -> str:
        return (f"<IadeSatiri(id={self.id}, iade_id={self.iade_id}, "
                f"urun_id={self.urun_id}, adet={self.adet}, "
                f"toplam_tutar={self.toplam_tutar})>")
    
    def birim_net_fiyat_hesapla(self) -> Decimal:
        """Birim net fiyatı hesaplar"""
        return self.toplam_tutar / Decimal(str(self.adet))
    
    def toplam_tutar_guncelle(self) -> None:
        """Toplam tutarı adet ve birim fiyata göre günceller"""
        self.toplam_tutar = Decimal(str(self.adet)) * self.birim_fiyat


# Model validasyon fonksiyonları
def iade_validasyon(iade: Iade) -> List[str]:
    """
    İade validasyon kuralları
    
    Args:
        iade: Validasyon yapılacak iade
        
    Returns:
        Hata mesajları listesi (boş liste = geçerli)
    """
    hatalar = []
    
    if iade.orijinal_satis_id <= 0:
        hatalar.append("Orijinal satış ID pozitif olmalıdır")
    
    if iade.terminal_id <= 0:
        hatalar.append("Terminal ID pozitif olmalıdır")
    
    if iade.kasiyer_id <= 0:
        hatalar.append("Kasiyer ID pozitif olmalıdır")
    
    if iade.toplam_tutar < 0:
        hatalar.append("Toplam tutar negatif olamaz")
    
    if not iade.neden or len(iade.neden.strip()) == 0:
        hatalar.append("İade nedeni boş olamaz")
    
    if iade.musteri_id and iade.musteri_id <= 0:
        hatalar.append("Müşteri ID pozitif olmalıdır")
    
    # Satırlar ile toplam tutar uyumu kontrolü
    if iade.satirlar:
        hesaplanan_toplam = iade.hesaplanan_toplam_tutar()
        if abs(iade.toplam_tutar - hesaplanan_toplam) > Decimal('0.01'):
            hatalar.append("Toplam tutar satırlar toplamı ile uyuşmuyor")
    
    # En az bir satır olmalı
    if not iade.satirlar or len(iade.satirlar) == 0:
        hatalar.append("İade en az bir satır içermelidir")
    
    return hatalar


def iade_satiri_validasyon(satir: IadeSatiri) -> List[str]:
    """
    İade satırı validasyon kuralları
    
    Args:
        satir: Validasyon yapılacak iade satırı
        
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
    
    if not satir.barkod or len(satir.barkod.strip()) == 0:
        hatalar.append("Barkod boş olamaz")
    
    if not satir.urun_adi or len(satir.urun_adi.strip()) == 0:
        hatalar.append("Ürün adı boş olamaz")
    
    # Hesaplanan toplam tutar kontrolü
    beklenen_toplam = Decimal(str(satir.adet)) * satir.birim_fiyat
    if abs(satir.toplam_tutar - beklenen_toplam) > Decimal('0.01'):
        hatalar.append("Toplam tutar hesaplaması hatalı")
    
    return hatalar