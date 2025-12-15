# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.modeller.belgeler
# Description: SONTECHSP belge modelleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Belge Modelleri

Tablolar:
- satis_belgeleri: Satış belgeleri
- satis_belge_satirlari: Satış belge detayları
"""

from decimal import Decimal
from typing import List
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..taban import Taban


class SatisBelge(Taban):
    """Satış belgeleri tablosu"""
    
    __tablename__ = "satis_belgeleri"
    
    belge_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    belge_tipi: Mapped[str] = mapped_column(String(20), nullable=False)
    toplam_tutar: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    
    satirlar: Mapped[List["SatisBelgeSatir"]] = relationship(
        "SatisBelgeSatir", back_populates="belge", cascade="all, delete-orphan"
    )


class SatisBelgeSatir(Taban):
    """Satış belge detayları tablosu"""
    
    __tablename__ = "satis_belge_satirlari"
    
    belge_id: Mapped[int] = mapped_column(ForeignKey("satis_belgeleri.id"), nullable=False)
    urun_id: Mapped[int] = mapped_column(ForeignKey("urunler.id"), nullable=False)
    miktar: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    
    belge: Mapped["SatisBelge"] = relationship("SatisBelge", back_populates="satirlar")