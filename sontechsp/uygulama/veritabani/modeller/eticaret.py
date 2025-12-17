# Version: 0.2.0
# Last Update: 2024-12-17
# Module: veritabani.modeller.eticaret
# Description: SONTECHSP e-ticaret entegrasyon modelleri
# Changelog:
# - İlk oluşturma
# - Tasarıma uygun olarak yeniden yazıldı
# - eticaret_hesaplari, eticaret_siparisleri, eticaret_is_kuyrugu tabloları eklendi

"""
SONTECHSP E-ticaret Entegrasyon Modelleri

Tablolar:
- eticaret_hesaplari: Mağaza hesap bilgileri ve kimlik bilgileri
- eticaret_siparisleri: Platform siparişleri ve ham verileri
- eticaret_is_kuyrugu: Asenkron iş kuyruğu sistemi
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Index, Integer, 
    JSON, Numeric, String, Text, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..taban import Taban


class EticaretHesaplari(Taban):
    """
    E-ticaret mağaza hesapları tablosu
    
    Her platform için mağaza kimlik bilgileri ve ayarlarını saklar.
    Kimlik bilgileri şifrelenmiş olarak JSON formatında tutulur.
    """
    
    __tablename__ = "eticaret_hesaplari"
    
    # Temel alanlar
    platform: Mapped[str] = mapped_column(String(50), nullable=False, comment="Platform türü (TRENDYOL, SHOPIFY vb.)")
    magaza_adi: Mapped[str] = mapped_column(String(200), nullable=False, comment="Mağaza adı")
    aktif_mi: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="Hesap aktif mi")
    
    # JSON alanlar
    kimlik_json: Mapped[dict] = mapped_column(JSON, nullable=False, comment="Şifrelenmiş kimlik bilgileri")
    ayar_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="Platform ayarları")
    
    # İlişkiler
    siparisler: Mapped[list["EticaretSiparisleri"]] = relationship(
        "EticaretSiparisleri", 
        back_populates="magaza_hesabi",
        cascade="all, delete-orphan"
    )
    
    isler: Mapped[list["EticaretIsKuyrugu"]] = relationship(
        "EticaretIsKuyrugu",
        back_populates="magaza_hesabi",
        cascade="all, delete-orphan"
    )
    
    # İndeksler
    __table_args__ = (
        Index('idx_eticaret_hesaplari_platform', 'platform'),
        Index('idx_eticaret_hesaplari_aktif', 'aktif_mi'),
    )


class EticaretSiparisleri(Taban):
    """
    E-ticaret siparişleri tablosu
    
    Platformlardan çekilen siparişleri saklar.
    Ham veri JSON formatında korunur.
    """
    
    __tablename__ = "eticaret_siparisleri"
    
    # Foreign key
    magaza_hesabi_id: Mapped[int] = mapped_column(
        ForeignKey("eticaret_hesaplari.id", ondelete="CASCADE"),
        nullable=False,
        comment="Mağaza hesabı referansı"
    )
    
    # Sipariş bilgileri
    platform: Mapped[str] = mapped_column(String(50), nullable=False, comment="Platform türü")
    dis_siparis_no: Mapped[str] = mapped_column(String(100), nullable=False, comment="Platform sipariş numarası")
    siparis_zamani: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="Sipariş tarihi")
    
    # Müşteri bilgileri
    musteri_ad_soyad: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="Müşteri adı soyadı")
    
    # Tutar bilgileri
    toplam_tutar: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True, comment="Toplam tutar")
    para_birimi: Mapped[str] = mapped_column(String(3), default='TRY', nullable=False, comment="Para birimi")
    
    # Durum bilgileri
    durum: Mapped[str] = mapped_column(String(20), nullable=False, comment="Sipariş durumu")
    
    # Kargo bilgileri
    kargo_tasiyici: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="Kargo taşıyıcı")
    takip_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="Kargo takip numarası")
    
    # Ham veri
    ham_veri_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="Platform ham verisi")
    
    # İlişkiler
    magaza_hesabi: Mapped["EticaretHesaplari"] = relationship(
        "EticaretHesaplari",
        back_populates="siparisler"
    )
    
    # Kısıtlamalar ve indeksler
    __table_args__ = (
        UniqueConstraint('magaza_hesabi_id', 'dis_siparis_no', name='uk_siparis_unique'),
        Index('idx_eticaret_siparisleri_platform', 'platform'),
        Index('idx_eticaret_siparisleri_durum', 'durum'),
        Index('idx_eticaret_siparisleri_siparis_zamani', 'siparis_zamani'),
    )


class EticaretIsKuyrugu(Taban):
    """
    E-ticaret iş kuyruğu tablosu
    
    Asenkron entegrasyon işlerini yönetir.
    FIFO sırasında işlenir ve hata durumunda yeniden denenir.
    """
    
    __tablename__ = "eticaret_is_kuyrugu"
    
    # Foreign key
    magaza_hesabi_id: Mapped[int] = mapped_column(
        ForeignKey("eticaret_hesaplari.id", ondelete="CASCADE"),
        nullable=False,
        comment="Mağaza hesabı referansı"
    )
    
    # İş bilgileri
    tur: Mapped[str] = mapped_column(String(50), nullable=False, comment="İş türü (SIPARIS_CEK, STOK_GONDER vb.)")
    payload_json: Mapped[dict] = mapped_column(JSON, nullable=False, comment="İş verisi")
    
    # Durum bilgileri
    durum: Mapped[str] = mapped_column(String(20), default='BEKLIYOR', nullable=False, comment="İş durumu")
    hata_mesaji: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Hata mesajı")
    
    # Yeniden deneme bilgileri
    deneme_sayisi: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="Deneme sayısı")
    sonraki_deneme: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="Sonraki deneme zamanı")
    
    # İlişkiler
    magaza_hesabi: Mapped["EticaretHesaplari"] = relationship(
        "EticaretHesaplari",
        back_populates="isler"
    )
    
    # İndeksler
    __table_args__ = (
        Index('idx_eticaret_is_kuyrugu_durum', 'durum'),
        Index('idx_eticaret_is_kuyrugu_tur', 'tur'),
        Index('idx_eticaret_is_kuyrugu_sonraki_deneme', 'sonraki_deneme'),
    )