# Version: 0.1.0
# Last Update: 2024-12-17
# Module: veritabani.modeller.kargo
# Description: Kargo modülü SQLAlchemy modelleri
# Changelog:
# - KargoEtiketleri modeli eklendi
# - KargoTakipleri modeli eklendi
# - Foreign key ilişkileri tanımlandı
# - Unique constraint'ler eklendi

"""
Kargo modülü SQLAlchemy modelleri.

Bu modül, kargo etiketleri ve takip kayıtları için
veritabanı modellerini içerir.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DECIMAL, TIMESTAMP, 
    ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from sontechsp.uygulama.veritabani.taban import Taban


class KargoEtiketleri(Taban):
    """Kargo etiketleri tablosu modeli."""
    
    __tablename__ = 'kargo_etiketleri'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Kaynak bilgileri
    kaynak_turu = Column(String(50), nullable=False, 
                        comment='POS_SATIS veya SATIS_BELGESI')
    kaynak_id = Column(Integer, nullable=False,
                      comment='Kaynak belge ID')
    
    # Taşıyıcı bilgileri
    tasiyici = Column(String(50), nullable=False,
                     comment='Taşıyıcı kodu')
    servis_kodu = Column(String(50), nullable=True,
                        comment='Taşıyıcı servis kodu')
    
    # Alıcı bilgileri
    alici_ad = Column(String(255), nullable=False,
                     comment='Alıcı adı')
    alici_telefon = Column(String(20), nullable=False,
                          comment='Alıcı telefonu')
    alici_adres = Column(Text, nullable=False,
                        comment='Alıcı adresi')
    alici_il = Column(String(100), nullable=False,
                     comment='Alıcı ili')
    alici_ilce = Column(String(100), nullable=False,
                       comment='Alıcı ilçesi')
    
    # Paket bilgileri
    paket_agirlik_kg = Column(DECIMAL(10, 2), nullable=False, default=1.0,
                             comment='Paket ağırlığı (kg)')
    
    # Durum bilgileri
    durum = Column(String(50), nullable=False,
                  comment='Etiket durumu')
    mesaj = Column(Text, nullable=True,
                  comment='Hata/bilgi mesajı')
    takip_no = Column(String(100), nullable=True,
                     comment='Takip numarası')
    
    # Retry bilgileri
    deneme_sayisi = Column(Integer, nullable=False, default=0,
                          comment='Retry sayısı')
    
    # Zaman damgaları
    olusturulma_zamani = Column(TIMESTAMP, nullable=False, 
                               server_default=func.now(),
                               comment='Oluşturulma zamanı')
    guncellenme_zamani = Column(TIMESTAMP, nullable=False,
                               server_default=func.now(),
                               onupdate=func.now(),
                               comment='Güncellenme zamanı')
    
    # İlişkiler
    takip_kayitlari = relationship("KargoTakipleri", 
                                  back_populates="etiket",
                                  cascade="all, delete-orphan")
    
    # Kısıtlamalar
    __table_args__ = (
        UniqueConstraint('kaynak_turu', 'kaynak_id', 'tasiyici',
                        name='uk_kargo_etiketleri_kaynak_tasiyici'),
        Index('ix_kargo_etiketleri_kaynak', 'kaynak_turu', 'kaynak_id'),
        Index('ix_kargo_etiketleri_durum', 'durum'),
        Index('ix_kargo_etiketleri_takip_no', 'takip_no'),
        Index('ix_kargo_etiketleri_tasiyici', 'tasiyici'),
        {'comment': 'Kargo etiketleri tablosu', 'extend_existing': True}
    )
    
    def __repr__(self):
        return (f"<KargoEtiketleri(id={self.id}, "
                f"kaynak_turu='{self.kaynak_turu}', "
                f"kaynak_id={self.kaynak_id}, "
                f"tasiyici='{self.tasiyici}', "
                f"durum='{self.durum}')>")


class KargoTakipleri(Taban):
    """Kargo takip kayıtları tablosu modeli."""
    
    __tablename__ = 'kargo_takipleri'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key
    etiket_id = Column(Integer, ForeignKey('kargo_etiketleri.id'),
                      nullable=False, comment='Etiket referansı')
    
    # Takip bilgileri
    takip_no = Column(String(100), nullable=False,
                     comment='Takip numarası')
    durum = Column(String(50), nullable=False,
                  comment='Takip durumu')
    aciklama = Column(Text, nullable=True,
                     comment='Durum açıklaması')
    zaman = Column(TIMESTAMP, nullable=True,
                  comment='Durum zamanı')
    
    # Zaman damgası
    olusturulma_zamani = Column(TIMESTAMP, nullable=False,
                               server_default=func.now(),
                               comment='Kayıt zamanı')
    
    # İlişkiler
    etiket = relationship("KargoEtiketleri", back_populates="takip_kayitlari")
    
    # İndeksler
    __table_args__ = (
        Index('ix_kargo_takipleri_etiket_id', 'etiket_id'),
        Index('ix_kargo_takipleri_takip_no', 'takip_no'),
        Index('ix_kargo_takipleri_durum', 'durum'),
        Index('ix_kargo_takipleri_zaman', 'zaman'),
        {'comment': 'Kargo takip kayıtları tablosu', 'extend_existing': True}
    )
    
    def __repr__(self):
        return (f"<KargoTakipleri(id={self.id}, "
                f"etiket_id={self.etiket_id}, "
                f"takip_no='{self.takip_no}', "
                f"durum='{self.durum}')>")