# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.modeller.magaza
# Description: SONTECHSP mağaza modelleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Mağaza Modelleri

Bu modül mağaza, terminal ve depo ile ilgili SQLAlchemy modellerini içerir.
"""

from typing import List, Optional
from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..taban import Taban


class Magaza(Taban):
    """Mağaza/şube bilgileri tablosu"""
    
    __tablename__ = "magazalar"
    
    firma_id: Mapped[int] = mapped_column(ForeignKey("firmalar.id", ondelete="CASCADE"), nullable=False)
    magaza_adi: Mapped[str] = mapped_column(String(200), nullable=False)
    magaza_kodu: Mapped[str] = mapped_column(String(20), nullable=False)
    adres: Mapped[Optional[str]] = mapped_column(Text)
    sehir: Mapped[Optional[str]] = mapped_column(String(100))
    ilce: Mapped[Optional[str]] = mapped_column(String(100))
    posta_kodu: Mapped[Optional[str]] = mapped_column(String(10))
    telefon: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    alan_m2: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    personel_sayisi: Mapped[Optional[int]]
    aktif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    firma: Mapped["Firma"] = relationship("Firma", back_populates="magazalar")
    terminaller: Mapped[List["Terminal"]] = relationship("Terminal", back_populates="magaza", cascade="all, delete-orphan")
    depolar: Mapped[List["Depo"]] = relationship("Depo", back_populates="magaza", cascade="all, delete-orphan")


class Terminal(Taban):
    """POS terminal bilgileri tablosu"""
    
    __tablename__ = "terminaller"
    
    magaza_id: Mapped[int] = mapped_column(ForeignKey("magazalar.id", ondelete="CASCADE"), nullable=False)
    terminal_adi: Mapped[str] = mapped_column(String(100), nullable=False)
    terminal_kodu: Mapped[str] = mapped_column(String(20), nullable=False)
    ip_adresi: Mapped[Optional[str]] = mapped_column(String(15))
    mac_adresi: Mapped[Optional[str]] = mapped_column(String(17))
    isletim_sistemi: Mapped[Optional[str]] = mapped_column(String(100))
    yazici_modeli: Mapped[Optional[str]] = mapped_column(String(100))
    barkod_okuyucu: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    aktif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    online: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    magaza: Mapped["Magaza"] = relationship("Magaza", back_populates="terminaller")


class Depo(Taban):
    """Stok depo bilgileri tablosu"""
    
    __tablename__ = "depolar"
    
    magaza_id: Mapped[int] = mapped_column(ForeignKey("magazalar.id", ondelete="CASCADE"), nullable=False)
    depo_adi: Mapped[str] = mapped_column(String(100), nullable=False)
    depo_kodu: Mapped[str] = mapped_column(String(20), nullable=False)
    depo_tipi: Mapped[str] = mapped_column(String(50), nullable=False, default="ana_depo")
    adres: Mapped[Optional[str]] = mapped_column(Text)
    alan_m2: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    kapasite_m3: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    soguk_depo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    otomatik_stok_takip: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    aktif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    magaza: Mapped["Magaza"] = relationship("Magaza", back_populates="depolar")