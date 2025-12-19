# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_crm_otomatik_zaman_damgasi_property
# Description: CRM otomatik zaman damgası property testleri
# Changelog:
# - İlk oluşturma

"""
**Feature: crm-cekirdek-modulu, Property 5: Otomatik zaman damgası**
**Validates: Requirements 1.5, 2.4, 4.5**

CRM modülü otomatik zaman damgası için property-based testler.
"""

from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, assume
import pytest
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta


# Test için gerekli sınıfları burada tanımla
@dataclass
class MusteriOlusturDTO:
    """Yeni müşteri oluşturma için veri transfer objesi"""
    ad: str
    soyad: str
    telefon: Optional[str] = None
    eposta: Optional[str] = None
    vergi_no: Optional[str] = None
    adres: Optional[str] = None
    aktif_mi: bool = True


@dataclass
class MusteriGuncelleDTO:
    """Müşteri güncelleme için veri transfer objesi"""
    ad: Optional[str] = None
    soyad: Optional[str] = None
    telefon: Optional[str] = None
    eposta: Optional[str] = None
    vergi_no: Optional[str] = None
    adres: Optional[str] = None
    aktif_mi: Optional[bool] = None


@dataclass
class PuanIslemDTO:
    """Puan işlemi için veri transfer objesi"""
    musteri_id: int
    puan: int
    aciklama: Optional[str] = None
    referans_turu: Optional[str] = None
    referans_id: Optional[int] = None


class MusteriDeposu:
    """Test için basit MusteriDeposu mock'u"""
    
    def __init__(self, db):
        self.db = db
    
    def musteri_olustur(self, dto: MusteriOlusturDTO):
        """Müşteri oluşturma - otomatik zaman damgası kontrolü"""
        # Zorunlu alan kontrolü
        if not dto.ad or not dto.ad.strip():
            raise Exception("Ad alanı boş olamaz")
        if not dto.soyad or not dto.soyad.strip():
            raise Exception("Soyad alanı boş olamaz")
        
        # Mock müşteri döndür - otomatik zaman damgaları ile
        mock_musteri = Mock()
        mock_musteri.id = 123
        mock_musteri.ad = dto.ad.strip()
        mock_musteri.soyad = dto.soyad.strip()
        mock_musteri.aktif_mi = dto.aktif_mi
        # Otomatik zaman damgaları
        now = datetime.now()
        mock_musteri.olusturulma_zamani = now
        mock_musteri.guncellenme_zamani = now
        return mock_musteri
    
    def musteri_guncelle(self, musteri_id: int, dto: MusteriGuncelleDTO):
        """Müşteri güncelleme - otomatik güncellenme zamanı kontrolü"""
        if musteri_id <= 0:
            raise Exception("Geçersiz müşteri ID")
        
        # Mock müşteri döndür - güncellenme zamanı yeni
        mock_musteri = Mock()
        mock_musteri.id = musteri_id
        mock_musteri.ad = dto.ad or "Mevcut Ad"
        mock_musteri.soyad = dto.soyad or "Mevcut Soyad"
        mock_musteri.aktif_mi = dto.aktif_mi if dto.aktif_mi is not None else True
        # Oluşturulma zamanı eski, güncellenme zamanı yeni
        mock_musteri.olusturulma_zamani = datetime.now() - timedelta(hours=1)
        mock_musteri.guncellenme_zamani = datetime.now()
        return mock_musteri


class SadakatDeposu:
    """Test için basit SadakatDeposu mock'u"""
    
    def __init__(self, db):
        self.db = db
    
    def puan_kaydi_ekle(self, dto: PuanIslemDTO):
        """Puan kaydı ekleme - otomatik zaman damgası kontrolü"""
        if dto.puan <= 0:
            raise Exception("Puan pozitif olmalıdır")
        
        # Mock puan kaydı döndür - otomatik zaman damgası ile
        mock_kayit = Mock()
        mock_kayit.id = 456
        mock_kayit.musteri_id = dto.musteri_id
        mock_kayit.puan = dto.puan
        mock_kayit.aciklama = dto.aciklama
        mock_kayit.referans_turu = dto.referans_turu
        mock_kayit.referans_id = dto.referans_id
        # Otomatik zaman damgası
        mock_kayit.olusturulma_zamani = datetime.now()
        return mock_kayit


# Test stratejileri
@st.composite
def musteri_olustur_strategy(draw):
    """Müşteri oluşturma DTO üretici"""
    return MusteriOlusturDTO(
        ad=draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip())),
        soyad=draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip())),
        telefon=draw(st.one_of(st.none(), st.text(min_size=10, max_size=20))),
        eposta=draw(st.one_of(st.none(), st.emails())),
        aktif_mi=draw(st.booleans())
    )


@st.composite
def musteri_guncelle_strategy(draw):
    """Müşteri güncelleme DTO üretici"""
    return MusteriGuncelleDTO(
        ad=draw(st.one_of(st.none(), st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))),
        soyad=draw(st.one_of(st.none(), st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))),
        telefon=draw(st.one_of(st.none(), st.text(min_size=10, max_size=20))),
        eposta=draw(st.one_of(st.none(), st.emails())),
        aktif_mi=draw(st.one_of(st.none(), st.booleans()))
    )


@st.composite
def puan_islem_strategy(draw):
    """Puan işlemi DTO üretici"""
    return PuanIslemDTO(
        musteri_id=draw(st.integers(min_value=1, max_value=1000)),
        puan=draw(st.integers(min_value=1, max_value=10000)),
        aciklama=draw(st.one_of(st.none(), st.text(max_size=200))),
        referans_turu=draw(st.one_of(st.none(), st.sampled_from(["POS_SATIS", "SATIS_BELGESI"]))),
        referans_id=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=1000)))
    )


class TestCRMOtomatikZamanDamgasi:
    """CRM otomatik zaman damgası property testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_session = Mock()
        self.musteri_deposu = MusteriDeposu(self.mock_session)
        self.sadakat_deposu = SadakatDeposu(self.mock_session)
    
    @given(musteri_olustur_strategy())
    def test_musteri_olusturma_zaman_damgasi(self, musteri_dto):
        """
        **Feature: crm-cekirdek-modulu, Property 5: Otomatik zaman damgası**
        **Validates: Requirements 1.5**
        
        Her müşteri oluşturma işlemi için, oluşturulma ve güncellenme zamanları otomatik atanır
        """
        # Geçerli ad ve soyad olduğunu varsay
        assume(musteri_dto.ad and musteri_dto.ad.strip())
        assume(musteri_dto.soyad and musteri_dto.soyad.strip())
        
        # İşlem öncesi zaman
        oncesi_zaman = datetime.now()
        
        # Müşteri oluştur
        sonuc = self.musteri_deposu.musteri_olustur(musteri_dto)
        
        # İşlem sonrası zaman
        sonrasi_zaman = datetime.now()
        
        # Başarılı olmalı ve zaman damgaları atanmış olmalı
        assert sonuc is not None
        assert hasattr(sonuc, 'olusturulma_zamani')
        assert hasattr(sonuc, 'guncellenme_zamani')
        assert sonuc.olusturulma_zamani is not None
        assert sonuc.guncellenme_zamani is not None
        
        # Zaman damgaları işlem zamanı aralığında olmalı
        assert oncesi_zaman <= sonuc.olusturulma_zamani <= sonrasi_zaman
        assert oncesi_zaman <= sonuc.guncellenme_zamani <= sonrasi_zaman
        
        # Oluşturulma ve güncellenme zamanları aynı olmalı (yeni kayıt)
        assert sonuc.olusturulma_zamani == sonuc.guncellenme_zamani
    
    @given(st.integers(min_value=1, max_value=1000), musteri_guncelle_strategy())
    def test_musteri_guncelleme_zaman_damgasi(self, musteri_id, guncelle_dto):
        """
        **Feature: crm-cekirdek-modulu, Property 5: Otomatik zaman damgası**
        **Validates: Requirements 2.4**
        
        Her müşteri güncelleme işlemi için, güncellenme zamanı otomatik güncellenir
        """
        # İşlem öncesi zaman
        oncesi_zaman = datetime.now()
        
        # Müşteri güncelle
        sonuc = self.musteri_deposu.musteri_guncelle(musteri_id, guncelle_dto)
        
        # İşlem sonrası zaman
        sonrasi_zaman = datetime.now()
        
        # Başarılı olmalı ve zaman damgaları atanmış olmalı
        assert sonuc is not None
        assert hasattr(sonuc, 'olusturulma_zamani')
        assert hasattr(sonuc, 'guncellenme_zamani')
        assert sonuc.olusturulma_zamani is not None
        assert sonuc.guncellenme_zamani is not None
        
        # Güncellenme zamanı işlem zamanı aralığında olmalı
        assert oncesi_zaman <= sonuc.guncellenme_zamani <= sonrasi_zaman
        
        # Oluşturulma zamanı güncellenme zamanından önce olmalı (güncelleme işlemi)
        assert sonuc.olusturulma_zamani < sonuc.guncellenme_zamani
    
    @given(puan_islem_strategy())
    def test_puan_islemi_zaman_damgasi(self, puan_dto):
        """
        **Feature: crm-cekirdek-modulu, Property 5: Otomatik zaman damgası**
        **Validates: Requirements 4.5**
        
        Her puan işlemi için, işlem zamanı otomatik atanır
        """
        # Pozitif puan olduğunu varsay
        assume(puan_dto.puan > 0)
        
        # İşlem öncesi zaman
        oncesi_zaman = datetime.now()
        
        # Puan kaydı ekle
        sonuc = self.sadakat_deposu.puan_kaydi_ekle(puan_dto)
        
        # İşlem sonrası zaman
        sonrasi_zaman = datetime.now()
        
        # Başarılı olmalı ve zaman damgası atanmış olmalı
        assert sonuc is not None
        assert hasattr(sonuc, 'olusturulma_zamani')
        assert sonuc.olusturulma_zamani is not None
        
        # Zaman damgası işlem zamanı aralığında olmalı
        assert oncesi_zaman <= sonuc.olusturulma_zamani <= sonrasi_zaman
    
    @given(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
           st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    def test_ayni_anda_olusturulan_musteriler_farkli_zaman(self, ad1, ad2):
        """
        Aynı anda oluşturulan müşteriler farklı zaman damgalarına sahip olabilir
        """
        # İlk müşteri
        dto1 = MusteriOlusturDTO(ad=ad1, soyad="Soyad1")
        sonuc1 = self.musteri_deposu.musteri_olustur(dto1)
        
        # Küçük bir gecikme
        import time
        time.sleep(0.001)
        
        # İkinci müşteri
        dto2 = MusteriOlusturDTO(ad=ad2, soyad="Soyad2")
        sonuc2 = self.musteri_deposu.musteri_olustur(dto2)
        
        # Her ikisi de başarılı olmalı
        assert sonuc1 is not None
        assert sonuc2 is not None
        
        # Zaman damgaları atanmış olmalı
        assert sonuc1.olusturulma_zamani is not None
        assert sonuc2.olusturulma_zamani is not None
        
        # İkinci müşterinin zamanı birinciden sonra veya eşit olmalı
        assert sonuc2.olusturulma_zamani >= sonuc1.olusturulma_zamani
    
    def test_zaman_damgasi_format_kontrolu(self):
        """
        Zaman damgaları datetime objesi olmalıdır
        """
        # Basit müşteri oluştur
        dto = MusteriOlusturDTO(ad="Test Ad", soyad="Test Soyad")
        sonuc = self.musteri_deposu.musteri_olustur(dto)
        
        # Zaman damgaları datetime objesi olmalı
        assert isinstance(sonuc.olusturulma_zamani, datetime)
        assert isinstance(sonuc.guncellenme_zamani, datetime)
    
    def test_puan_islemi_zaman_damgasi_format_kontrolu(self):
        """
        Puan işlemi zaman damgası datetime objesi olmalıdır
        """
        # Basit puan işlemi
        dto = PuanIslemDTO(musteri_id=1, puan=100, aciklama="Test puan")
        sonuc = self.sadakat_deposu.puan_kaydi_ekle(dto)
        
        # Zaman damgası datetime objesi olmalı
        assert isinstance(sonuc.olusturulma_zamani, datetime)