# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.taban
# Description: SONTECHSP SQLAlchemy DeclarativeBase tanımı
# Changelog:
# - İlk oluşturma

"""
SONTECHSP SQLAlchemy Taban Sınıfı

Bu modül tüm SQLAlchemy modellerinin türetileceği DeclarativeBase sınıfını içerir.
Türkçe ASCII tablo isimlendirme standardına uygun yapılandırma sağlar.

Özellikler:
- Otomatik tablo isimlendirme (snake_case)
- Türkçe ASCII karakter desteği
- Ortak sütunlar (id, olusturma_tarihi, guncelleme_tarihi)
- Timezone-aware datetime desteği
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Taban(DeclarativeBase):
    """
    SONTECHSP tüm modellerin türetileceği taban sınıf
    
    Ortak özellikler:
    - id: Primary key (otomatik artan)
    - olusturma_tarihi: Kayıt oluşturma zamanı
    - guncelleme_tarihi: Son güncelleme zamanı
    """
    
    # Otomatik tablo isimlendirme (snake_case)
    __abstract__ = True
    
    # Ortak sütunlar
    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="Benzersiz kayıt kimliği"
    )
    
    olusturma_tarihi: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Kayıt oluşturma tarihi"
    )
    
    guncelleme_tarihi: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
        comment="Son güncelleme tarihi"
    )
    
    def __repr__(self) -> str:
        """Model string temsili"""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    @classmethod
    def tablo_adi(cls) -> str:
        """Sınıf adından tablo adı üret (snake_case)"""
        import re
        # CamelCase'i snake_case'e çevir
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# Metadata nesnesi (Alembic için gerekli)
metadata = Taban.metadata