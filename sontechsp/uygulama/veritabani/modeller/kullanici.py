# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.modeller.kullanici
# Description: SONTECHSP kullanıcı modeli
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Kullanıcı Modeli

Bu modül sistem kullanıcıları ile ilgili SQLAlchemy modelini içerir.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..taban import Taban


class Kullanici(Taban):
    """Sistem kullanıcıları tablosu"""
    
    __tablename__ = "kullanicilar"
    
    # Temel bilgiler
    kullanici_adi: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False,
        comment="Benzersiz kullanıcı adı"
    )
    
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        nullable=False,
        comment="E-posta adresi"
    )
    
    sifre_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
        comment="Şifrelenmiş parola"
    )
    
    # Kişisel bilgiler
    ad: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="Kullanıcı adı"
    )
    
    soyad: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="Kullanıcı soyadı"
    )
    
    telefon: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="Telefon numarası"
    )
    
    # Durum bilgileri
    aktif: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Kullanıcı aktif mi"
    )
    
    son_giris_tarihi: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="Son giriş tarihi"
    )
    
    sifre_degisim_tarihi: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="Son şifre değişim tarihi"
    )
    
    # İlişkiler
    kullanici_rolleri: Mapped[List["KullaniciRol"]] = relationship(
        "KullaniciRol", 
        back_populates="kullanici",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Kullanici(kullanici_adi='{self.kullanici_adi}', email='{self.email}')>"