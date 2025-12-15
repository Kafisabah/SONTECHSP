# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.modeller.stok
# Description: SONTECHSP stok yönetimi modelleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Yönetimi Modelleri

Bu modül ürün, barkod, stok bakiyesi ve stok hareketleri ile ilgili SQLAlchemy modellerini içerir.
Çoklu mağaza stok takibi ve negatif stok kontrolü desteklenir.

Tablolar:
- urunler: Ürün ana bilgileri
- urun_barkodlari: Ürün barkod bilgileri (bir ürünün birden fazla barkodu olabilir)
- stok_bakiyeleri: Mağaza/depo bazında stok bakiyeleri
- stok_hareketleri: Tüm stok giriş/çıkış hareketleri
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..taban import Taban


class Urun(Taban):
    """
    Ürün ana bilgileri tablosu
    
    Sistemdeki tüm ürünlerin temel bilgilerini içerir.
    Stok takibi bu tablo üzerinden yapılır.
    """
    
    __tablename__ = "urunler"
    
    # Temel bilgiler
    urun_kodu: Mapped[str] = mapped_column(
        String(50), 
        unique=True,
        nullable=False,
        comment="Benzersiz ürün kodu"
    )
    
    urun_adi: Mapped[str] = mapped_column(
        String(200), 
        nullable=False,
        comment="Ürün adı"
    )
    
    aciklama: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Ürün açıklaması"
    )
    
    # Kategori bilgileri
    kategori: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="Ürün kategorisi"
    )
    
    alt_kategori: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="Ürün alt kategorisi"
    )
    
    marka: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="Ürün markası"
    )
    
    # Birim bilgileri
    birim: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        default="adet",
        comment="Stok birimi (adet, kg, lt, vs.)"
    )
    
    # Fiyat bilgileri
    alis_fiyati: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4),
        comment="Alış fiyatı"
    )
    
    satis_fiyati: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4),
        comment="Satış fiyatı"
    )
    
    kdv_orani: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), 
        nullable=False,
        default=Decimal('18.00'),
        comment="KDV oranı (%)"
    )
    
    # Stok kontrol bilgileri
    stok_takip: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Stok takibi yapılsın mı"
    )
    
    negatif_stok_izin: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False,
        comment="Negatif stoka izin verilsin mi"
    )
    
    minimum_stok: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4),
        comment="Minimum stok miktarı"
    )
    
    maksimum_stok: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4),
        comment="Maksimum stok miktarı"
    )
    
    # Durum bilgileri
    aktif: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Ürün aktif mi"
    )
    
    # İlişkiler
    barkodlar: Mapped[List["UrunBarkod"]] = relationship(
        "UrunBarkod", 
        back_populates="urun",
        cascade="all, delete-orphan"
    )
    
    stok_bakiyeleri: Mapped[List["StokBakiye"]] = relationship(
        "StokBakiye", 
        back_populates="urun",
        cascade="all, delete-orphan"
    )
    
    stok_hareketleri: Mapped[List["StokHareket"]] = relationship(
        "StokHareket", 
        back_populates="urun",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Urun(urun_kodu='{self.urun_kodu}', urun_adi='{self.urun_adi}')>"


class UrunBarkod(Taban):
    """
    Ürün barkod bilgileri tablosu
    
    Bir ürünün birden fazla barkodu olabilir.
    Farklı birimler için farklı barkodlar tanımlanabilir.
    """
    
    __tablename__ = "urun_barkodlari"
    
    # Foreign key
    urun_id: Mapped[int] = mapped_column(
        ForeignKey("urunler.id", ondelete="CASCADE"),
        nullable=False,
        comment="Ürün ID referansı"
    )
    
    # Barkod bilgileri
    barkod: Mapped[str] = mapped_column(
        String(50), 
        unique=True,
        nullable=False,
        comment="Barkod numarası"
    )
    
    barkod_tipi: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        default="EAN13",
        comment="Barkod tipi (EAN13, EAN8, CODE128, vs.)"
    )
    
    # Birim bilgileri
    birim: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        comment="Bu barkodun temsil ettiği birim"
    )
    
    carpan: Mapped[Decimal] = mapped_column(
        Numeric(15, 4), 
        nullable=False,
        default=Decimal('1.0000'),
        comment="Ana birime çevirme çarpanı"
    )
    
    # Durum bilgileri
    aktif: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Barkod aktif mi"
    )
    
    ana_barkod: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False,
        comment="Ana barkod mu"
    )
    
    # İlişkiler
    urun: Mapped["Urun"] = relationship(
        "Urun", 
        back_populates="barkodlar"
    )
    
    def __repr__(self) -> str:
        return f"<UrunBarkod(barkod='{self.barkod}', birim='{self.birim}')>"


class StokBakiye(Taban):
    """
    Stok bakiye tablosu
    
    Her ürünün her mağaza/depo için ayrı stok bakiyesi tutulur.
    Çoklu mağaza stok takibi için kritik tablo.
    """
    
    __tablename__ = "stok_bakiyeleri"
    
    # Foreign key'ler
    urun_id: Mapped[int] = mapped_column(
        ForeignKey("urunler.id", ondelete="CASCADE"),
        nullable=False,
        comment="Ürün ID referansı"
    )
    
    magaza_id: Mapped[int] = mapped_column(
        ForeignKey("magazalar.id", ondelete="CASCADE"),
        nullable=False,
        comment="Mağaza ID referansı"
    )
    
    depo_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("depolar.id", ondelete="SET NULL"),
        comment="Depo ID referansı (opsiyonel)"
    )
    
    # Stok bilgileri
    miktar: Mapped[Decimal] = mapped_column(
        Numeric(15, 4), 
        nullable=False,
        default=Decimal('0.0000'),
        comment="Mevcut stok miktarı"
    )
    
    rezerve_miktar: Mapped[Decimal] = mapped_column(
        Numeric(15, 4), 
        nullable=False,
        default=Decimal('0.0000'),
        comment="Rezerve edilmiş miktar"
    )
    
    kullanilabilir_miktar: Mapped[Decimal] = mapped_column(
        Numeric(15, 4), 
        nullable=False,
        default=Decimal('0.0000'),
        comment="Kullanılabilir miktar (miktar - rezerve_miktar)"
    )
    
    # Maliyet bilgileri
    ortalama_maliyet: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4),
        comment="Ortalama maliyet"
    )
    
    son_alis_fiyati: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4),
        comment="Son alış fiyatı"
    )
    
    # Tarih bilgileri
    son_hareket_tarihi: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="Son stok hareket tarihi"
    )
    
    # İlişkiler
    urun: Mapped["Urun"] = relationship(
        "Urun", 
        back_populates="stok_bakiyeleri"
    )
    
    def __repr__(self) -> str:
        return f"<StokBakiye(urun_id={self.urun_id}, magaza_id={self.magaza_id}, miktar={self.miktar})>"


class StokHareket(Taban):
    """
    Stok hareket tablosu
    
    Tüm stok giriş/çıkış hareketlerini kaydeder.
    Stok takibi ve raporlama için kullanılır.
    """
    
    __tablename__ = "stok_hareketleri"
    
    # Foreign key'ler
    urun_id: Mapped[int] = mapped_column(
        ForeignKey("urunler.id", ondelete="CASCADE"),
        nullable=False,
        comment="Ürün ID referansı"
    )
    
    magaza_id: Mapped[int] = mapped_column(
        ForeignKey("magazalar.id", ondelete="CASCADE"),
        nullable=False,
        comment="Mağaza ID referansı"
    )
    
    depo_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("depolar.id", ondelete="SET NULL"),
        comment="Depo ID referansı (opsiyonel)"
    )
    
    # Hareket bilgileri
    hareket_tipi: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="Hareket tipi (giris, cikis, transfer, sayim, vs.)"
    )
    
    miktar: Mapped[Decimal] = mapped_column(
        Numeric(15, 4), 
        nullable=False,
        comment="Hareket miktarı (+ giriş, - çıkış)"
    )
    
    birim_fiyat: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4),
        comment="Birim fiyat"
    )
    
    toplam_tutar: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4),
        comment="Toplam tutar"
    )
    
    # Referans bilgileri
    referans_tablo: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="Referans tablo adı (pos_satislar, vs.)"
    )
    
    referans_id: Mapped[Optional[int]] = mapped_column(
        comment="Referans kayıt ID"
    )
    
    # Açıklama
    aciklama: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Hareket açıklaması"
    )
    
    # Kullanıcı bilgisi
    kullanici_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("kullanicilar.id", ondelete="SET NULL"),
        comment="Hareketi yapan kullanıcı"
    )
    
    # İlişkiler
    urun: Mapped["Urun"] = relationship(
        "Urun", 
        back_populates="stok_hareketleri"
    )
    
    def __repr__(self) -> str:
        return f"<StokHareket(urun_id={self.urun_id}, hareket_tipi='{self.hareket_tipi}', miktar={self.miktar})>"