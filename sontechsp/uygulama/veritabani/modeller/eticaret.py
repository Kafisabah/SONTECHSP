# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.modeller.eticaret
# Description: SONTECHSP e-ticaret modelleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP E-ticaret Modelleri

Tablolar:
- eticaret_hesaplari: E-ticaret hesap bilgileri
- eticaret_siparisleri: E-ticaret sipariş bilgileri
"""

from decimal import Decimal
from sqlalchemy import Boolean, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..taban import Taban


class EticaretHesap(Taban):
    """E-ticaret hesap bilgileri tablosu"""
    
    __tablename__ = "eticaret_hesaplari"
    
    hesap_adi: Mapped[str] = mapped_column(String(100), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    aktif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class EticaretSiparis(Taban):
    """E-ticaret sipariş bilgileri tablosu"""
    
    __tablename__ = "eticaret_siparisleri"
    
    siparis_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    toplam_tutar: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    durum: Mapped[str] = mapped_column(String(20), nullable=False)