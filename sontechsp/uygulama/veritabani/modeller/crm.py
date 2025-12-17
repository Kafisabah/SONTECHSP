# Version: 0.1.0
# Last Update: 2024-12-17
# Module: crm_modeller
# Description: CRM modülü SQLAlchemy veritabanı modelleri
# Changelog:
# - İlk oluşturma: Musteriler ve SadakatPuanlari tabloları
# - Taban sınıfla uyumlu hale getirildi
# - İndeksler ve constraint'ler eklendi
# - Kod analizi ve düzeltmeler yapıldı

from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship
from ..taban import Taban


class Musteriler(Taban):
    """Müşteri bilgileri tablosu"""
    __tablename__ = 'musteriler'
    
    # Taban sınıftan id, olusturma_tarihi, guncelleme_tarihi otomatik gelir
    ad = Column(String(100), nullable=False, comment="Müşteri adı")
    soyad = Column(String(100), nullable=False, comment="Müşteri soyadı")
    telefon = Column(String(20), unique=True, nullable=True, comment="Telefon numarası")
    eposta = Column(String(255), unique=True, nullable=True, comment="E-posta adresi")
    vergi_no = Column(String(20), nullable=True, comment="Vergi numarası")
    adres = Column(Text, nullable=True, comment="Müşteri adresi")
    aktif_mi = Column(Boolean, default=True, nullable=False, comment="Aktif durumu")
    
    # İlişkiler
    sadakat_puanlari = relationship("SadakatPuanlari", back_populates="musteri", cascade="all, delete-orphan")
    
    # İndeksler
    __table_args__ = (
        Index('idx_musteriler_telefon', 'telefon'),
        Index('idx_musteriler_eposta', 'eposta'),
        Index('idx_musteriler_ad_soyad', 'ad', 'soyad'),
        CheckConstraint("ad != ''", name='chk_musteriler_ad_bos_degil'),
        CheckConstraint("soyad != ''", name='chk_musteriler_soyad_bos_degil'),
    )
    
    def __repr__(self):
        return f"<Musteriler(id={self.id}, ad='{self.ad}', soyad='{self.soyad}')>"


class SadakatPuanlari(Taban):
    """Müşteri sadakat puanları tablosu"""
    __tablename__ = 'sadakat_puanlari'
    
    # Taban sınıftan id, olusturma_tarihi, guncelleme_tarihi otomatik gelir
    musteri_id = Column(Integer, ForeignKey('musteriler.id', ondelete='CASCADE'), nullable=False, comment="Müşteri ID")
    islem_turu = Column(String(20), nullable=False, comment="İşlem türü (KAZANIM, HARCAMA, DUZELTME)")
    puan = Column(Integer, nullable=False, comment="Puan miktarı")
    aciklama = Column(Text, nullable=True, comment="İşlem açıklaması")
    referans_turu = Column(String(50), nullable=True, comment="Referans türü (POS_SATIS, SATIS_BELGESI)")
    referans_id = Column(Integer, nullable=True, comment="Referans ID")
    
    # İlişkiler
    musteri = relationship("Musteriler", back_populates="sadakat_puanlari")
    
    # İndeksler ve constraint'ler
    __table_args__ = (
        Index('idx_sadakat_musteri_id', 'musteri_id'),
        Index('idx_sadakat_referans', 'referans_turu', 'referans_id'),
        Index('idx_sadakat_islem_turu', 'islem_turu'),
        Index('idx_sadakat_olusturma_tarihi', 'olusturma_tarihi'),
        CheckConstraint("islem_turu IN ('KAZANIM', 'HARCAMA', 'DUZELTME')", name='chk_sadakat_islem_turu'),
        CheckConstraint("puan != 0", name='chk_sadakat_puan_sifir_degil'),
    )
    
    def __repr__(self):
        return f"<SadakatPuanlari(id={self.id}, musteri_id={self.musteri_id}, islem_turu='{self.islem_turu}', puan={self.puan})>"