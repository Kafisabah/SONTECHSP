# Version: 0.2.0
# Last Update: 2024-12-17
# Module: veritabani.modeller.ebelge
# Description: SONTECHSP e-belge modelleri
# Changelog:
# - İlk oluşturma
# - Spec'e uygun olarak yeniden tasarlandı
# - Outbox pattern için uygun tablo yapısı eklendi

"""
SONTECHSP E-belge Modelleri

Tablolar:
- ebelge_cikis_kuyrugu: E-belge çıkış kuyruğu (Outbox Pattern)
- ebelge_durumlari: E-belge durum geçmişi (Audit Log)
"""

from sqlalchemy import (
    String, Text, Integer, DateTime, Index, 
    UniqueConstraint, ForeignKey, Numeric
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from decimal import Decimal

from ..taban import Taban


class EbelgeCikisKuyrugu(Taban):
    """E-belge çıkış kuyruğu tablosu (Outbox Pattern)"""
    
    __tablename__ = "ebelge_cikis_kuyrugu"
    
    # Kaynak bilgileri
    kaynak_turu: Mapped[str] = mapped_column(String(50), nullable=False)
    kaynak_id: Mapped[int] = mapped_column(Integer, nullable=False)
    belge_turu: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Müşteri bilgileri
    musteri_ad: Mapped[str] = mapped_column(String(200), nullable=False)
    vergi_no: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Tutar bilgileri
    toplam_tutar: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    para_birimi: Mapped[str] = mapped_column(String(3), nullable=False, default="TRY")
    
    # Belge verisi
    belge_json: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Durum bilgileri
    durum: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    mesaj: Mapped[str] = mapped_column(Text, nullable=True)
    dis_belge_no: Mapped[str] = mapped_column(String(100), nullable=True)
    deneme_sayisi: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # İsteğe bağlı açıklama
    aciklama: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Zaman damgaları
    olusturulma_zamani: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    guncellenme_zamani: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    durum_gecmisi = relationship("EbelgeDurumlari", back_populates="cikis_kaydi", cascade="all, delete-orphan")
    
    # Kısıtlamalar
    __table_args__ = (
        UniqueConstraint('kaynak_turu', 'kaynak_id', 'belge_turu', name='uq_ebelge_kaynak'),
        Index('ix_ebelge_durum_deneme', 'durum', 'deneme_sayisi'),
        Index('ix_ebelge_olusturulma', 'olusturulma_zamani'),
    )


class EbelgeDurumlari(Taban):
    """E-belge durum geçmişi tablosu (Audit Log)"""
    
    __tablename__ = "ebelge_durumlari"
    
    # Referans
    cikis_id: Mapped[int] = mapped_column(Integer, ForeignKey('ebelge_cikis_kuyrugu.id'), nullable=False)
    
    # Durum bilgileri
    durum: Mapped[str] = mapped_column(String(20), nullable=False)
    mesaj: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Zaman damgası
    olusturulma_zamani: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # İlişkiler
    cikis_kaydi = relationship("EbelgeCikisKuyrugu", back_populates="durum_gecmisi")
    
    # İndeksler
    __table_args__ = (
        Index('ix_ebelge_durum_cikis_id', 'cikis_id'),
        Index('ix_ebelge_durum_olusturulma', 'olusturulma_zamani'),
    )