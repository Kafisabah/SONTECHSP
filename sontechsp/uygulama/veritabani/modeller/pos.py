# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.modeller.pos
# Description: SONTECHSP POS modelleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP POS Modelleri

Bu modül POS satış işlemleri ile ilgili SQLAlchemy modellerini içerir.
"""

from decimal import Decimal
from typing import List, Optional
from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..taban import Taban


class PosSatis(Taban):
    """POS satış ana kayıtları tablosu"""
    
    __tablename__ = "pos_satislar"
    
    satis_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    terminal_id: Mapped[int] = mapped_column(ForeignKey("terminaller.id", ondelete="CASCADE"), nullable=False)
    musteri_id: Mapped[Optional[int]] = mapped_column(ForeignKey("musteriler.id", ondelete="SET NULL"))
    ara_toplam: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    kdv_tutari: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    genel_toplam: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    durum: Mapped[str] = mapped_column(String(20), nullable=False, default="tamamlandi")
    
    satirlar: Mapped[List["PosSatisSatir"]] = relationship("PosSatisSatir", back_populates="satis", cascade="all, delete-orphan")
    odemeler: Mapped[List["OdemeKayit"]] = relationship("OdemeKayit", back_populates="satis", cascade="all, delete-orphan")


class PosSatisSatir(Taban):
    """POS satış detay kayıtları tablosu"""
    
    __tablename__ = "pos_satis_satirlari"
    
    satis_id: Mapped[int] = mapped_column(ForeignKey("pos_satislar.id", ondelete="CASCADE"), nullable=False)
    urun_id: Mapped[int] = mapped_column(ForeignKey("urunler.id", ondelete="CASCADE"), nullable=False)
    miktar: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    birim_fiyat: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    toplam_tutar: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    
    satis: Mapped["PosSatis"] = relationship("PosSatis", back_populates="satirlar")


class OdemeKayit(Taban):
    """Ödeme kayıtları tablosu"""
    
    __tablename__ = "odeme_kayitlari"
    
    satis_id: Mapped[int] = mapped_column(ForeignKey("pos_satislar.id", ondelete="CASCADE"), nullable=False)
    odeme_tipi: Mapped[str] = mapped_column(String(50), nullable=False)
    tutar: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    
    satis: Mapped["PosSatis"] = relationship("PosSatis", back_populates="odemeler")