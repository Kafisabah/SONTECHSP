# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.modeller.firma
# Description: SONTECHSP firma modeli
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Firma Modeli

Bu modül ana firma bilgileri ile ilgili SQLAlchemy modelini içerir.
"""

from typing import List, Optional
from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..taban import Taban


class Firma(Taban):
    """Ana firma bilgileri tablosu"""
    
    __tablename__ = "firmalar"
    
    # Temel bilgiler
    firma_adi: Mapped[str] = mapped_column(
        String(200), 
        nullable=False,
        comment="Firma adı"
    )
    
    ticaret_unvani: Mapped[Optional[str]] = mapped_column(
        String(200),
        comment="Ticaret unvanı"
    )
    
    # Vergi bilgileri
    vergi_dairesi: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="Vergi dairesi"
    )
    
    vergi_no: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="Vergi numarası"
    )
    
    tc_kimlik_no: Mapped[Optional[str]] = mapped_column(
        String(11),
        comment="TC kimlik numarası (şahıs firması için)"
    )
    
    # İletişim bilgileri
    adres: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Firma adresi"
    )
    
    telefon: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="Telefon numarası"
    )
    
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="E-posta adresi"
    )
    
    website: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="Web sitesi"
    )
    
    # Durum bilgileri
    aktif: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Firma aktif mi"
    )
    
    # İlişkiler
    magazalar: Mapped[List["Magaza"]] = relationship(
        "Magaza", 
        back_populates="firma",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Firma(firma_adi='{self.firma_adi}')>"