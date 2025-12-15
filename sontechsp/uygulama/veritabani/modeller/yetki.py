# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.modeller.yetki
# Description: SONTECHSP yetki modelleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Yetki Modelleri

Bu modül rol ve yetki yönetimi ile ilgili SQLAlchemy modellerini içerir.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..taban import Taban


class Rol(Taban):
    """Kullanıcı rolleri tablosu"""
    
    __tablename__ = "roller"
    
    rol_adi: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    aciklama: Mapped[Optional[str]] = mapped_column(Text)
    aktif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sistem_rolu: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    kullanici_rolleri: Mapped[List["KullaniciRol"]] = relationship(
        "KullaniciRol", back_populates="rol", cascade="all, delete-orphan"
    )
    rol_yetkileri: Mapped[List["RolYetki"]] = relationship(
        "RolYetki", back_populates="rol", cascade="all, delete-orphan"
    )


class Yetki(Taban):
    """Sistem yetkileri tablosu"""
    
    __tablename__ = "yetkiler"
    
    yetki_kodu: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    yetki_adi: Mapped[str] = mapped_column(String(100), nullable=False)
    aciklama: Mapped[Optional[str]] = mapped_column(Text)
    kategori: Mapped[str] = mapped_column(String(50), nullable=False)
    aktif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sistem_yetkisi: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    rol_yetkileri: Mapped[List["RolYetki"]] = relationship(
        "RolYetki", back_populates="yetki", cascade="all, delete-orphan"
    )


class KullaniciRol(Taban):
    """Kullanıcı-rol ilişki tablosu"""
    
    __tablename__ = "kullanici_rolleri"
    
    kullanici_id: Mapped[int] = mapped_column(ForeignKey("kullanicilar.id", ondelete="CASCADE"), nullable=False)
    rol_id: Mapped[int] = mapped_column(ForeignKey("roller.id", ondelete="CASCADE"), nullable=False)
    atayan_kullanici_id: Mapped[Optional[int]] = mapped_column(ForeignKey("kullanicilar.id"))
    atama_tarihi: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    aktif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    kullanici: Mapped["Kullanici"] = relationship("Kullanici", foreign_keys=[kullanici_id])
    rol: Mapped["Rol"] = relationship("Rol", back_populates="kullanici_rolleri")


class RolYetki(Taban):
    """Rol-yetki ilişki tablosu"""
    
    __tablename__ = "rol_yetkileri"
    
    rol_id: Mapped[int] = mapped_column(ForeignKey("roller.id", ondelete="CASCADE"), nullable=False)
    yetki_id: Mapped[int] = mapped_column(ForeignKey("yetkiler.id", ondelete="CASCADE"), nullable=False)
    atayan_kullanici_id: Mapped[Optional[int]] = mapped_column(ForeignKey("kullanicilar.id"))
    atama_tarihi: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    aktif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    rol: Mapped["Rol"] = relationship("Rol", back_populates="rol_yetkileri")
    yetki: Mapped["Yetki"] = relationship("Yetki", back_populates="rol_yetkileri")