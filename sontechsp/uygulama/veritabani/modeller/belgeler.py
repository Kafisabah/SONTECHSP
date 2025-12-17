# Version: 0.2.0
# Last Update: 2024-12-16
# Module: veritabani.modeller.belgeler
# Description: SONTECHSP belge modelleri - Satış Belgeleri Modülü
# Changelog:
# - İlk oluşturma
# - Satış belgeleri modülü için kapsamlı model güncellemesi

"""
SONTECHSP Belge Modelleri

Tablolar:
- satis_belgeleri: Satış belgeleri (sipariş, irsaliye, fatura)
- belge_satirlari: Belge satır detayları
- numara_sayaclari: Belge numarası üretim sayaçları
- belge_durum_gecmisi: Belge durum değişiklik geçmişi
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Index, Integer, 
    Numeric, String, Text, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..taban import Taban


class BelgeTuru(Enum):
    """Belge türü enum"""
    SIPARIS = "SIPARIS"
    IRSALIYE = "IRSALIYE"
    FATURA = "FATURA"


class BelgeDurumu(Enum):
    """Belge durumu enum"""
    TASLAK = "TASLAK"
    ONAYLANDI = "ONAYLANDI"
    FATURALANDI = "FATURALANDI"
    IPTAL = "IPTAL"


class SatisBelgesi(Taban):
    """Satış belgeleri ana tablosu"""
    
    __tablename__ = "satis_belgeleri"
    
    # Belge temel bilgileri
    belge_numarasi: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False,
        comment="Benzersiz belge numarası (MGZ-YYYY-MM-NNNN formatında)"
    )
    
    belge_turu: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        comment="Belge türü: SIPARIS, IRSALIYE, FATURA"
    )
    
    belge_durumu: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default=BelgeDurumu.TASLAK.value,
        comment="Belge durumu: TASLAK, ONAYLANDI, FATURALANDI, IPTAL"
    )
    
    # Referans bilgileri
    magaza_id: Mapped[int] = mapped_column(
        ForeignKey("magazalar.id"), 
        nullable=False,
        comment="Belgeyi oluşturan mağaza"
    )
    
    musteri_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("musteriler.id"), 
        nullable=True,
        comment="Müşteri referansı (opsiyonel)"
    )
    
    olusturan_kullanici_id: Mapped[int] = mapped_column(
        ForeignKey("kullanicilar.id"), 
        nullable=False,
        comment="Belgeyi oluşturan kullanıcı"
    )
    
    # Kaynak belge bilgileri (dönüşüm için)
    kaynak_belge_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("satis_belgeleri.id"), 
        nullable=True,
        comment="Kaynak belge ID (sipariş->irsaliye, sipariş->fatura)"
    )
    
    kaynak_belge_turu: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True,
        comment="Kaynak belge türü (POS, SIPARIS vb.)"
    )
    
    # Tutar bilgileri
    toplam_tutar: Mapped[Decimal] = mapped_column(
        Numeric(15, 4), 
        nullable=False, 
        default=Decimal('0.0000'),
        comment="Toplam tutar (KDV hariç)"
    )
    
    kdv_tutari: Mapped[Decimal] = mapped_column(
        Numeric(15, 4), 
        nullable=False, 
        default=Decimal('0.0000'),
        comment="Toplam KDV tutarı"
    )
    
    genel_toplam: Mapped[Decimal] = mapped_column(
        Numeric(15, 4), 
        nullable=False, 
        default=Decimal('0.0000'),
        comment="Genel toplam (KDV dahil)"
    )
    
    # İptal bilgileri
    iptal_nedeni: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="İptal nedeni açıklaması"
    )
    
    iptal_tarihi: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        comment="İptal tarihi"
    )
    
    # İlişkiler
    satirlar: Mapped[List["BelgeSatiri"]] = relationship(
        "BelgeSatiri", 
        back_populates="belge", 
        cascade="all, delete-orphan",
        order_by="BelgeSatiri.sira_no"
    )
    
    durum_gecmisi: Mapped[List["BelgeDurumGecmisi"]] = relationship(
        "BelgeDurumGecmisi", 
        back_populates="belge", 
        cascade="all, delete-orphan",
        order_by="BelgeDurumGecmisi.olusturma_tarihi"
    )
    
    kaynak_belge: Mapped[Optional["SatisBelgesi"]] = relationship(
        "SatisBelgesi", 
        remote_side=[id],
        back_populates="turetilen_belgeler"
    )
    
    turetilen_belgeler: Mapped[List["SatisBelgesi"]] = relationship(
        "SatisBelgesi", 
        back_populates="kaynak_belge"
    )
    
    # İndeksler
    __table_args__ = (
        Index('idx_satis_belgeleri_belge_numarasi', 'belge_numarasi'),
        Index('idx_satis_belgeleri_belge_turu', 'belge_turu'),
        Index('idx_satis_belgeleri_belge_durumu', 'belge_durumu'),
        Index('idx_satis_belgeleri_magaza_id', 'magaza_id'),
        Index('idx_satis_belgeleri_musteri_id', 'musteri_id'),
        Index('idx_satis_belgeleri_olusturma_tarihi', 'olusturma_tarihi'),
    )


class BelgeSatiri(Taban):
    """Belge satır detayları tablosu"""
    
    __tablename__ = "belge_satirlari"
    
    # Referans bilgileri
    belge_id: Mapped[int] = mapped_column(
        ForeignKey("satis_belgeleri.id"), 
        nullable=False,
        comment="Bağlı olduğu belge"
    )
    
    urun_id: Mapped[int] = mapped_column(
        ForeignKey("urunler.id"), 
        nullable=False,
        comment="Satır ürünü"
    )
    
    sira_no: Mapped[int] = mapped_column(
        Integer, 
        nullable=False,
        comment="Satır sıra numarası"
    )
    
    # Miktar ve fiyat bilgileri
    miktar: Mapped[Decimal] = mapped_column(
        Numeric(15, 4), 
        nullable=False,
        comment="Ürün miktarı"
    )
    
    birim_fiyat: Mapped[Decimal] = mapped_column(
        Numeric(15, 4), 
        nullable=False,
        comment="Birim fiyat (KDV hariç)"
    )
    
    kdv_orani: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), 
        nullable=False, 
        default=Decimal('18.00'),
        comment="KDV oranı (%)"
    )
    
    # Hesaplanan tutarlar
    satir_tutari: Mapped[Decimal] = mapped_column(
        Numeric(15, 4), 
        nullable=False,
        comment="Satır tutarı (miktar * birim_fiyat)"
    )
    
    kdv_tutari: Mapped[Decimal] = mapped_column(
        Numeric(15, 4), 
        nullable=False,
        comment="Satır KDV tutarı"
    )
    
    satir_toplami: Mapped[Decimal] = mapped_column(
        Numeric(15, 4), 
        nullable=False,
        comment="Satır toplamı (KDV dahil)"
    )
    
    # İlişkiler
    belge: Mapped["SatisBelgesi"] = relationship(
        "SatisBelgesi", 
        back_populates="satirlar"
    )
    
    # İndeksler ve kısıtlamalar
    __table_args__ = (
        Index('idx_belge_satirlari_belge_id', 'belge_id'),
        Index('idx_belge_satirlari_urun_id', 'urun_id'),
        UniqueConstraint('belge_id', 'sira_no', name='uq_belge_satirlari_belge_sira'),
    )


class NumaraSayaci(Taban):
    """Belge numarası üretim sayaçları"""
    
    __tablename__ = "numara_sayaclari"
    
    magaza_id: Mapped[int] = mapped_column(
        ForeignKey("magazalar.id"), 
        nullable=False,
        comment="Mağaza ID"
    )
    
    belge_turu: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        comment="Belge türü"
    )
    
    yil: Mapped[int] = mapped_column(
        Integer, 
        nullable=False,
        comment="Yıl"
    )
    
    ay: Mapped[int] = mapped_column(
        Integer, 
        nullable=False,
        comment="Ay (1-12)"
    )
    
    son_numara: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="Son kullanılan sıra numarası"
    )
    
    # İndeksler ve kısıtlamalar
    __table_args__ = (
        UniqueConstraint(
            'magaza_id', 'belge_turu', 'yil', 'ay', 
            name='uq_numara_sayaclari_magaza_tur_yil_ay'
        ),
        Index('idx_numara_sayaclari_magaza_tur', 'magaza_id', 'belge_turu'),
    )


class BelgeDurumGecmisi(Taban):
    """Belge durum değişiklik geçmişi"""
    
    __tablename__ = "belge_durum_gecmisi"
    
    belge_id: Mapped[int] = mapped_column(
        ForeignKey("satis_belgeleri.id"), 
        nullable=False,
        comment="Bağlı olduğu belge"
    )
    
    eski_durum: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True,
        comment="Önceki durum (ilk kayıt için null)"
    )
    
    yeni_durum: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        comment="Yeni durum"
    )
    
    degistiren_kullanici_id: Mapped[int] = mapped_column(
        ForeignKey("kullanicilar.id"), 
        nullable=False,
        comment="Durumu değiştiren kullanıcı"
    )
    
    aciklama: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="Durum değişikliği açıklaması"
    )
    
    # İlişkiler
    belge: Mapped["SatisBelgesi"] = relationship(
        "SatisBelgesi", 
        back_populates="durum_gecmisi"
    )
    
    # İndeksler
    __table_args__ = (
        Index('idx_belge_durum_gecmisi_belge_id', 'belge_id'),
        Index('idx_belge_durum_gecmisi_olusturma_tarihi', 'olusturma_tarihi'),
    )