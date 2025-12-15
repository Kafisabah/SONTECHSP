# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.modeller.crm
# Description: SONTECHSP CRM modelleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP CRM Modelleri

Bu modül müşteri yönetimi ve sadakat programı ile ilgili SQLAlchemy modellerini içerir.

Tablolar:
- musteriler: Müşteri bilgileri
- sadakat_puanlari: Müşteri sadakat puanları
"""

from decimal import Decimal
from typing import List, Optional
from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..taban import Taban


class Musteri(Taban):
    """Müşteri bilgileri tablosu"""
    
    __tablename__ = "musteriler"
    
    # Temel bilgiler
    musteri_kodu: Mapped[str] = mapped_column(
        String(50), 
        unique=True,
        nullable=False,
        comment="Benzersiz müşteri kodu"
    )
    
    ad: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="Müşteri adı"
    )
    
    soyad: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="Müşteri soyadı"
    )
    
    # İletişim bilgileri
    telefon: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="Telefon numarası"
    )
    
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="E-posta adresi"
    )
    
    adres: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Adres bilgisi"
    )
    
    # Durum bilgileri
    aktif: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Müşteri aktif mi"
    )
    
    # İlişkiler
    sadakat_puanlari: Mapped[List["SadakatPuan"]] = relationship(
        "SadakatPuan", 
        back_populates="musteri",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Musteri(musteri_kodu='{self.musteri_kodu}', ad='{self.ad}')>"


class SadakatPuan(Taban):
    """Müşteri sadakat puanları tablosu"""
    
    __tablename__ = "sadakat_puanlari"
    
    # Foreign key
    musteri_id: Mapped[int] = mapped_column(
        ForeignKey("musteriler.id", ondelete="CASCADE"),
        nullable=False,
        comment="Müşteri ID referansı"
    )
    
    # Puan bilgileri
    puan: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), 
        nullable=False,
        comment="Puan miktarı"
    )
    
    hareket_tipi: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="Puan hareket tipi (kazanc, kullanim, vs.)"
    )
    
    aciklama: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Puan hareket açıklaması"
    )
    
    # İlişkiler
    musteri: Mapped["Musteri"] = relationship(
        "Musteri", 
        back_populates="sadakat_puanlari"
    )
    
    def __repr__(self) -> str:
        return f"<SadakatPuan(musteri_id={self.musteri_id}, puan={self.puan})>"