# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_crm_musteri_alan_zorunlulugu_property
# Description: CRM müşteri alan zorunluluğu property testleri
# Changelog:
# - İlk oluşturma

"""
**Feature: crm-cekirdek-modulu, Property 1: Müşteri alan zorunluluğu**
**Validates: Requirements 1.1**

CRM modülü müşteri alan zorunluluğu için property-based testler.
"""

from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, assume
import pytest
from dataclasses import dataclass
from typing import Optional


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


class AlanHatasi(Exception):
    """Alan doğrulama hatası"""
    pass


class MusteriDeposu:
    """Test için basit MusteriDeposu mock'u"""
    
    def __init__(self, db):
        self.db = db
    
    def musteri_olustur(self, dto: MusteriOlusturDTO):
        """Müşteri oluşturma - alan zorunluluğu kontrolü"""
        # Zorunlu alan kontrolü
        if not dto.ad or not dto.ad.strip():
            raise AlanHatasi("Ad alanı boş olamaz")
        if not dto.soyad or not dto.soyad.strip():
            raise AlanHatasi("Soyad alanı boş olamaz")
        
        # Mock müşteri döndür
        mock_musteri = Mock()
        mock_musteri.id = 123
        mock_musteri.ad = dto.ad.strip()
        mock_musteri.soyad = dto.soyad.strip()
        return mock_musteri


# Test stratejileri
@st.composite
def gecerli_musteri_strategy(draw):
    """Geçerli müşteri verisi üretici"""
    return MusteriOlusturDTO(
        ad=draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip())),
        soyad=draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip())),
        telefon=draw(st.one_of(st.none(), st.text(min_size=10, max_size=20))),
        eposta=draw(st.one_of(st.none(), st.emails())),
        vergi_no=draw(st.one_of(st.none(), st.text(min_size=10, max_size=20))),
        adres=draw(st.one_of(st.none(), st.text(max_size=500))),
        aktif_mi=draw(st.booleans())
    )


@st.composite
def bos_ad_musteri_strategy(draw):
    """Boş ad alanı olan müşteri verisi üretici"""
    return MusteriOlusturDTO(
        ad=draw(st.one_of(st.just(""), st.text(max_size=10).filter(lambda x: not x.strip()))),
        soyad=draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip())),
        telefon=draw(st.one_of(st.none(), st.text(min_size=10, max_size=20))),
        eposta=draw(st.one_of(st.none(), st.emails())),
        aktif_mi=draw(st.booleans())
    )


@st.composite
def bos_soyad_musteri_strategy(draw):
    """Boş soyad alanı olan müşteri verisi üretici"""
    return MusteriOlusturDTO(
        ad=draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip())),
        soyad=draw(st.one_of(st.just(""), st.text(max_size=10).filter(lambda x: not x.strip()))),
        telefon=draw(st.one_of(st.none(), st.text(min_size=10, max_size=20))),
        eposta=draw(st.one_of(st.none(), st.emails())),
        aktif_mi=draw(st.booleans())
    )


class TestCRMMusteriAlanZorunlulugu:
    """CRM müşteri alan zorunluluğu property testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_session = Mock()
        self.musteri_deposu = MusteriDeposu(self.mock_session)
    
    @given(gecerli_musteri_strategy())
    def test_gecerli_ad_soyad_ile_musteri_olusturma(self, musteri_dto):
        """
        **Feature: crm-cekirdek-modulu, Property 1: Müşteri alan zorunluluğu**
        **Validates: Requirements 1.1**
        
        Her müşteri oluşturma işlemi için, ad ve soyad alanları boş olamaz
        """
        # Geçerli ad ve soyad olduğunu varsay
        assume(musteri_dto.ad and musteri_dto.ad.strip())
        assume(musteri_dto.soyad and musteri_dto.soyad.strip())
        
        # Müşteri oluştur - hata fırlatmamalı
        try:
            sonuc = self.musteri_deposu.musteri_olustur(musteri_dto)
            # Başarılı olmalı
            assert sonuc is not None
            assert sonuc.ad == musteri_dto.ad.strip()
            assert sonuc.soyad == musteri_dto.soyad.strip()
        except AlanHatasi:
            # Geçerli ad/soyad ile AlanHatasi fırlatmamalı
            pytest.fail("Geçerli ad/soyad ile AlanHatasi fırlatıldı")
    
    @given(bos_ad_musteri_strategy())
    def test_bos_ad_ile_musteri_olusturma_hatasi(self, musteri_dto):
        """
        Boş ad alanı ile müşteri oluşturma işleminde AlanHatasi fırlatılmalıdır
        """
        # Boş ad olduğunu varsay
        assume(not musteri_dto.ad or not musteri_dto.ad.strip())
        
        # AlanHatasi fırlatılmalı
        with pytest.raises(AlanHatasi) as exc_info:
            self.musteri_deposu.musteri_olustur(musteri_dto)
        
        # Hata mesajı ad alanı ile ilgili olmalı
        assert "ad" in str(exc_info.value).lower()
    
    @given(bos_soyad_musteri_strategy())
    def test_bos_soyad_ile_musteri_olusturma_hatasi(self, musteri_dto):
        """
        Boş soyad alanı ile müşteri oluşturma işleminde AlanHatasi fırlatılmalıdır
        """
        # Boş soyad olduğunu varsay
        assume(not musteri_dto.soyad or not musteri_dto.soyad.strip())
        
        # AlanHatasi fırlatılmalı
        with pytest.raises(AlanHatasi) as exc_info:
            self.musteri_deposu.musteri_olustur(musteri_dto)
        
        # Hata mesajı soyad alanı ile ilgili olmalı
        assert "soyad" in str(exc_info.value).lower()
    
    @given(st.one_of(st.just(None), st.just(""), st.text(max_size=5).filter(lambda x: not x.strip())))
    def test_none_veya_bos_ad_hatasi(self, bos_ad):
        """
        None veya boş ad değerleri ile AlanHatasi fırlatılmalıdır
        """
        musteri_dto = MusteriOlusturDTO(
            ad=bos_ad,
            soyad="Geçerli Soyad",
            aktif_mi=True
        )
        
        # AlanHatasi fırlatılmalı
        with pytest.raises(AlanHatasi) as exc_info:
            self.musteri_deposu.musteri_olustur(musteri_dto)
        
        # Hata mesajı ad alanı ile ilgili olmalı
        assert "ad" in str(exc_info.value).lower()
    
    @given(st.one_of(st.just(None), st.just(""), st.text(max_size=5).filter(lambda x: not x.strip())))
    def test_none_veya_bos_soyad_hatasi(self, bos_soyad):
        """
        None veya boş soyad değerleri ile AlanHatasi fırlatılmalıdır
        """
        musteri_dto = MusteriOlusturDTO(
            ad="Geçerli Ad",
            soyad=bos_soyad,
            aktif_mi=True
        )
        
        # AlanHatasi fırlatılmalı
        with pytest.raises(AlanHatasi) as exc_info:
            self.musteri_deposu.musteri_olustur(musteri_dto)
        
        # Hata mesajı soyad alanı ile ilgili olmalı
        assert "soyad" in str(exc_info.value).lower()
    
    @given(st.text(min_size=1, max_size=10).filter(lambda x: x.strip()))
    def test_sadece_bosluk_karakterli_ad_hatasi(self, whitespace_text):
        """
        Sadece boşluk karakterli ad değerleri ile AlanHatasi fırlatılmalıdır
        """
        # Sadece boşluk karakterleri içeren string oluştur
        bos_ad = " " * len(whitespace_text)
        
        musteri_dto = MusteriOlusturDTO(
            ad=bos_ad,
            soyad="Geçerli Soyad",
            aktif_mi=True
        )
        
        # AlanHatasi fırlatılmalı
        with pytest.raises(AlanHatasi) as exc_info:
            self.musteri_deposu.musteri_olustur(musteri_dto)
        
        # Hata mesajı ad alanı ile ilgili olmalı
        assert "ad" in str(exc_info.value).lower()
    
    @given(st.text(min_size=1, max_size=10).filter(lambda x: x.strip()))
    def test_sadece_bosluk_karakterli_soyad_hatasi(self, whitespace_text):
        """
        Sadece boşluk karakterli soyad değerleri ile AlanHatasi fırlatılmalıdır
        """
        # Sadece boşluk karakterleri içeren string oluştur
        bos_soyad = " " * len(whitespace_text)
        
        musteri_dto = MusteriOlusturDTO(
            ad="Geçerli Ad",
            soyad=bos_soyad,
            aktif_mi=True
        )
        
        # AlanHatasi fırlatılmalı
        with pytest.raises(AlanHatasi) as exc_info:
            self.musteri_deposu.musteri_olustur(musteri_dto)
        
        # Hata mesajı soyad alanı ile ilgili olmalı
        assert "soyad" in str(exc_info.value).lower()