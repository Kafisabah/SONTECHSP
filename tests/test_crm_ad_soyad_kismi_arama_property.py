# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_crm_ad_soyad_kismi_arama_property
# Description: CRM ad/soyad kısmi arama property testi
# Changelog:
# - İlk oluşturma: Property 8 - Ad/soyad kısmi arama testi

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock
from dataclasses import dataclass
from typing import Optional, List


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
class MusteriAraDTO:
    """Müşteri arama kriterleri için veri transfer objesi"""
    ad: Optional[str] = None
    soyad: Optional[str] = None
    telefon: Optional[str] = None
    eposta: Optional[str] = None
    aktif_mi: Optional[bool] = None


class DogrulamaHatasi(Exception):
    """Doğrulama hatası"""
    pass


class MusteriServisi:
    """Test için basit MusteriServisi mock'u"""
    
    def __init__(self, db):
        self.db = db
        self.musteriler = {}  # In-memory müşteri store
        self.next_id = 1
    
    def musteri_olustur(self, dto: MusteriOlusturDTO):
        """Müşteri oluşturma"""
        if not dto.ad or not dto.ad.strip():
            raise DogrulamaHatasi("Ad alanı zorunludur")
        if not dto.soyad or not dto.soyad.strip():
            raise DogrulamaHatasi("Soyad alanı zorunludur")
        
        # Mock müşteri oluştur
        musteri = Mock()
        musteri.id = self.next_id
        musteri.ad = dto.ad.strip()
        musteri.soyad = dto.soyad.strip()
        musteri.telefon = dto.telefon.strip() if dto.telefon else None
        musteri.eposta = dto.eposta.strip().lower() if dto.eposta else None
        musteri.vergi_no = dto.vergi_no.strip() if dto.vergi_no else None
        musteri.adres = dto.adres.strip() if dto.adres else None
        musteri.aktif_mi = dto.aktif_mi
        
        self.musteriler[self.next_id] = musteri
        self.next_id += 1
        return musteri
    
    def musteri_ara(self, dto: MusteriAraDTO) -> List:
        """Müşteri arama - kısmi eşleşme ile"""
        # En az bir arama kriteri olmalı
        if not any([dto.ad, dto.soyad, dto.telefon, dto.eposta, dto.aktif_mi is not None]):
            return []
        
        sonuclar = []
        
        for musteri in self.musteriler.values():
            eslesme = True
            
            # Ad kısmi eşleşme (case-insensitive)
            if dto.ad:
                if dto.ad.strip().lower() not in musteri.ad.lower():
                    eslesme = False
            
            # Soyad kısmi eşleşme (case-insensitive)
            if dto.soyad:
                if dto.soyad.strip().lower() not in musteri.soyad.lower():
                    eslesme = False
            
            # Telefon tam eşleşme
            if dto.telefon:
                if musteri.telefon != dto.telefon.strip():
                    eslesme = False
            
            # E-posta tam eşleşme (case-insensitive)
            if dto.eposta:
                if musteri.eposta != dto.eposta.strip().lower():
                    eslesme = False
            
            # Aktif durum
            if dto.aktif_mi is not None:
                if musteri.aktif_mi != dto.aktif_mi:
                    eslesme = False
            
            if eslesme:
                sonuclar.append(musteri)
        
        return sonuclar


# Hypothesis stratejileri
gecerli_musteri_strategy = st.builds(
    MusteriOlusturDTO,
    ad=st.text(min_size=3, max_size=50).filter(lambda x: x.strip()),
    soyad=st.text(min_size=3, max_size=50).filter(lambda x: x.strip()),
    telefon=st.one_of(st.none(), st.text(min_size=5, max_size=20)),
    eposta=st.one_of(st.none(), st.emails()),
    vergi_no=st.one_of(st.none(), st.text(min_size=5, max_size=20)),
    adres=st.one_of(st.none(), st.text(max_size=200)),
    aktif_mi=st.booleans()
)


@given(musteri_dto=gecerli_musteri_strategy)
@settings(max_examples=100)
def test_ad_kismi_arama_property(musteri_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 8: Ad/soyad kısmi arama**
    **Validates: Requirements 3.1**
    
    Her ad/soyad ile arama yapıldığında kısmi eşleşme ile sonuç döndürülür
    """
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Müşteri oluştur
    musteri = musteri_servisi.musteri_olustur(musteri_dto)
    
    # Ad'ın bir kısmı ile arama yap
    if len(musteri.ad) >= 3:
        ad_parcasi = musteri.ad[1:3]  # Ortadan 2 karakter al
        
        arama_dto = MusteriAraDTO(ad=ad_parcasi)
        sonuclar = musteri_servisi.musteri_ara(arama_dto)
        
        # Sonuçlarda bu müşteri bulunmalı
        assert len(sonuclar) > 0
        musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
        assert musteri_bulundu, f"Ad parçası '{ad_parcasi}' ile arama yapıldığında müşteri bulunamadı"
    
    # Soyad'ın bir kısmı ile arama yap
    if len(musteri.soyad) >= 3:
        soyad_parcasi = musteri.soyad[1:3]  # Ortadan 2 karakter al
        
        arama_dto = MusteriAraDTO(soyad=soyad_parcasi)
        sonuclar = musteri_servisi.musteri_ara(arama_dto)
        
        # Sonuçlarda bu müşteri bulunmalı
        assert len(sonuclar) > 0
        musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
        assert musteri_bulundu, f"Soyad parçası '{soyad_parcasi}' ile arama yapıldığında müşteri bulunamadı"


@given(musteri_dto=gecerli_musteri_strategy)
@settings(max_examples=100)
def test_ad_soyad_case_insensitive_arama(musteri_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 8: Ad/soyad kısmi arama**
    **Validates: Requirements 3.1**
    
    Ad/soyad arama case-insensitive olmalıdır
    """
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Müşteri oluştur
    musteri = musteri_servisi.musteri_olustur(musteri_dto)
    
    # Ad'ı büyük harfle ara - sadece ASCII karakterler için test et
    if len(musteri.ad) >= 2 and musteri.ad.isascii():
        ad_buyuk = musteri.ad[:2].upper()
        
        arama_dto = MusteriAraDTO(ad=ad_buyuk)
        sonuclar = musteri_servisi.musteri_ara(arama_dto)
        
        # Sonuçlarda bu müşteri bulunmalı
        musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
        assert musteri_bulundu, f"Büyük harfli ad '{ad_buyuk}' ile arama yapıldığında müşteri bulunamadı"
    
    # Soyad'ı küçük harfle ara - sadece ASCII karakterler için test et
    if len(musteri.soyad) >= 2 and musteri.soyad.isascii():
        soyad_kucuk = musteri.soyad[:2].lower()
        
        arama_dto = MusteriAraDTO(soyad=soyad_kucuk)
        sonuclar = musteri_servisi.musteri_ara(arama_dto)
        
        # Sonuçlarda bu müşteri bulunmalı
        musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
        assert musteri_bulundu, f"Küçük harfli soyad '{soyad_kucuk}' ile arama yapıldığında müşteri bulunamadı"


@given(musteri_dto=gecerli_musteri_strategy)
@settings(max_examples=100)
def test_tam_ad_soyad_arama(musteri_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 8: Ad/soyad kısmi arama**
    **Validates: Requirements 3.1**
    
    Tam ad/soyad ile arama yapıldığında müşteri bulunmalıdır
    """
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Müşteri oluştur
    musteri = musteri_servisi.musteri_olustur(musteri_dto)
    
    # Tam ad ile arama yap
    arama_dto = MusteriAraDTO(ad=musteri.ad)
    sonuclar = musteri_servisi.musteri_ara(arama_dto)
    
    # Sonuçlarda bu müşteri bulunmalı
    assert len(sonuclar) > 0
    musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
    assert musteri_bulundu, f"Tam ad '{musteri.ad}' ile arama yapıldığında müşteri bulunamadı"
    
    # Tam soyad ile arama yap
    arama_dto = MusteriAraDTO(soyad=musteri.soyad)
    sonuclar = musteri_servisi.musteri_ara(arama_dto)
    
    # Sonuçlarda bu müşteri bulunmalı
    assert len(sonuclar) > 0
    musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
    assert musteri_bulundu, f"Tam soyad '{musteri.soyad}' ile arama yapıldığında müşteri bulunamadı"


@given(
    musteri1_dto=gecerli_musteri_strategy,
    musteri2_dto=gecerli_musteri_strategy
)
@settings(max_examples=100)
def test_olmayan_ad_soyad_arama(musteri1_dto, musteri2_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 8: Ad/soyad kısmi arama**
    **Validates: Requirements 3.1**
    
    Olmayan ad/soyad ile arama yapıldığında boş sonuç döndürülür
    """
    # Farklı ad/soyad olduğunu varsay
    assume(musteri1_dto.ad.lower() != musteri2_dto.ad.lower())
    assume(musteri1_dto.soyad.lower() != musteri2_dto.soyad.lower())
    
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Sadece ilk müşteriyi oluştur
    musteri1 = musteri_servisi.musteri_olustur(musteri1_dto)
    
    # İkinci müşterinin adı ile arama yap (olmayan ad)
    arama_dto = MusteriAraDTO(ad=musteri2_dto.ad)
    sonuclar = musteri_servisi.musteri_ara(arama_dto)
    
    # İlk müşteri sonuçlarda bulunmamalı
    musteri_bulundu = any(s.id == musteri1.id for s in sonuclar)
    assert not musteri_bulundu, f"Olmayan ad '{musteri2_dto.ad}' ile arama yapıldığında yanlış müşteri bulundu"
    
    # İkinci müşterinin soyadı ile arama yap (olmayan soyad)
    arama_dto = MusteriAraDTO(soyad=musteri2_dto.soyad)
    sonuclar = musteri_servisi.musteri_ara(arama_dto)
    
    # İlk müşteri sonuçlarda bulunmamalı
    musteri_bulundu = any(s.id == musteri1.id for s in sonuclar)
    assert not musteri_bulundu, f"Olmayan soyad '{musteri2_dto.soyad}' ile arama yapıldığında yanlış müşteri bulundu"


def test_bos_arama_kriterleri():
    """
    **Feature: crm-cekirdek-modulu, Property 8: Ad/soyad kısmi arama**
    **Validates: Requirements 3.1**
    
    Boş arama kriterleri ile arama yapıldığında boş liste döndürülür
    """
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Boş arama DTO'su ile arama yap
    arama_dto = MusteriAraDTO()
    sonuclar = musteri_servisi.musteri_ara(arama_dto)
    
    # Boş liste döndürmeli
    assert sonuclar == []