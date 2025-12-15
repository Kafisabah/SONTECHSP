# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.modeller.kargo
# Description: SONTECHSP kargo modelleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Kargo Modelleri

Tablolar:
- kargo_etiketleri: Kargo etiket bilgileri
- kargo_takipleri: Kargo takip bilgileri
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..taban import Taban


class KargoEtiket(Taban):
    """Kargo etiket bilgileri tablosu"""
    
    __tablename__ = "kargo_etiketleri"
    
    takip_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    kargo_firmasi: Mapped[str] = mapped_column(String(50), nullable=False)
    alici_adi: Mapped[str] = mapped_column(String(100), nullable=False)
    durum: Mapped[str] = mapped_column(String(20), nullable=False)


class KargoTakip(Taban):
    """Kargo takip bilgileri tablosu"""
    
    __tablename__ = "kargo_takipleri"
    
    takip_no: Mapped[str] = mapped_column(String(50), nullable=False)
    durum: Mapped[str] = mapped_column(String(50), nullable=False)
    aciklama: Mapped[str] = mapped_column(String(200), nullable=False)