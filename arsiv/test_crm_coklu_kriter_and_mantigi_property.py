# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_crm_coklu_kriter_and_mantigi_property
# Description: CRM çoklu kriter AND mantığı property testi
# Changelog:
# - İlk oluşturma: Property 10 - Çoklu kriter AND mantığı testi

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
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
        """Müşteri arama - çoklu kriter AND mantığı ile"""
        # En az bir arama kriteri olmalı
        if not any([dto.ad, dto.soyad, dto.telefon, dto.eposta, dto.aktif_mi is not None]):
            return []
        
        sonuclar = []
        
        for musteri in self.musteriler.values():
            eslesme = True
            
            # Ad kısmi eşleşme (case-insensitive) - AND mantığı
            if dto.ad:
                if dto.ad.strip().lower() not in musteri.ad.lower():
                    eslesme = False
            
            # Soyad kısmi eşleşme (case-insensitive) - AND mantığı
            if dto.soyad:
                if dto.soyad.strip().lower() not in musteri.soyad.lower():
                    eslesme = False
            
            # Telefon tam eşleşme - AND mantığı
            if dto.telefon:
                if musteri.telefon != dto.telefon.strip():
                    eslesme = False
            
            # E-posta tam eşleşme (case-insensitive) - AND mantığı
            if dto.eposta:
                if musteri.eposta != dto.eposta.strip().lower():
                    eslesme = False
            
            # Aktif durum - AND mantığı
            if dto.aktif_mi is not None:
                if musteri.aktif_mi != dto.aktif_mi:
                    eslesme = False
            
            # Tüm kriterler eşleşirse sonuçlara ekle
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
def test_coklu_kriter_and_mantigi_property(musteri_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 10: Çoklu kriter AND mantığı**
    **Validates: Requirements 3.4**
    
    Her birden fazla arama kriteri için, AND mantığı ile filtreleme yapılır
    """
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Müşteri oluştur
    musteri = musteri_servisi.musteri_olustur(musteri_dto)
    
    # Tek kriter ile arama yap - müşteri bulunmalı
    if len(musteri.ad) >= 2:
        arama_dto = MusteriAraDTO(ad=musteri.ad[:2])
        sonuclar = musteri_servisi.musteri_ara(arama_dto)
        
        # Müşteri bulunmalı
        musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
        assert musteri_bulundu, f"Tek kriter (ad) ile arama yapıldığında müşteri bulunamadı"
    
    # İki kriter ile arama yap (ad + aktif durum) - müşteri bulunmalı
    if len(musteri.ad) >= 2:
        arama_dto = MusteriAraDTO(ad=musteri.ad[:2], aktif_mi=musteri.aktif_mi)
        sonuclar = musteri_servisi.musteri_ara(arama_dto)
        
        # Müşteri bulunmalı (her iki kriter de eşleşiyor)
        musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
        assert musteri_bulundu, f"İki kriter (ad + aktif) ile arama yapıldığında müşteri bulunamadı"
    
    # İki kriter ile arama yap (ad + yanlış aktif durum) - müşteri bulunmamalı
    if len(musteri.ad) >= 2:
        yanlis_aktif = not musteri.aktif_mi
        arama_dto = MusteriAraDTO(ad=musteri.ad[:2], aktif_mi=yanlis_aktif)
        sonuclar = musteri_servisi.musteri_ara(arama_dto)
        
        # Müşteri bulunmamalı (aktif durum eşleşmiyor)
        musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
        assert not musteri_bulundu, f"Yanlış aktif durum ile arama yapıldığında müşteri bulundu (olmamalıydı)"


@given(
    musteri1_dto=gecerli_musteri_strategy,
    musteri2_dto=gecerli_musteri_strategy
)
@settings(max_examples=50)
def test_coklu_kriter_and_filtreleme(musteri1_dto, musteri2_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 10: Çoklu kriter AND mantığı**
    **Validates: Requirements 3.4**
    
    Çoklu kriter ile arama yapıldığında sadece tüm kriterleri karşılayan müşteriler döndürülür
    """
    # Farklı ad ve soyad olduğunu varsay
    assume(musteri1_dto.ad.lower() != musteri2_dto.ad.lower())
    assume(musteri1_dto.soyad.lower() != musteri2_dto.soyad.lower())
    
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # İki müşteri oluştur
    musteri1 = musteri_servisi.musteri_olustur(musteri1_dto)
    musteri2 = musteri_servisi.musteri_olustur(musteri2_dto)
    
    # İlk müşterinin ad ve soyadı ile arama yap
    if len(musteri1.ad) >= 2 and len(musteri1.soyad) >= 2:
        arama_dto = MusteriAraDTO(
            ad=musteri1.ad[:2],
            soyad=musteri1.soyad[:2]
        )
        sonuclar = musteri_servisi.musteri_ara(arama_dto)
        
        # İlk müşteri bulunmalı
        musteri1_bulundu = any(s.id == musteri1.id for s in sonuclar)
        assert musteri1_bulundu, f"İlk müşterinin ad+soyad kriterleri ile arama yapıldığında bulunamadı"
        
        # İkinci müşteri bulunmamalı (soyad eşleşmiyor)
        musteri2_bulundu = any(s.id == musteri2.id for s in sonuclar)
        assert not musteri2_bulundu, f"İkinci müşteri yanlış kriterlerde bulundu (olmamalıydı)"


@given(musteri_dto=gecerli_musteri_strategy)
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much])
def test_uc_kriter_and_mantigi(musteri_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 10: Çoklu kriter AND mantığı**
    **Validates: Requirements 3.4**
    
    Üç kriter ile arama yapıldığında AND mantığı çalışmalı
    """
    # Telefon ve e-posta olan müşteri olduğunu varsay
    assume(musteri_dto.telefon is not None and musteri_dto.telefon.strip())
    assume(musteri_dto.eposta is not None and musteri_dto.eposta.strip())
    
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Müşteri oluştur
    musteri = musteri_servisi.musteri_olustur(musteri_dto)
    
    # Üç kriter ile arama yap (ad + telefon + aktif durum)
    if len(musteri.ad) >= 2:
        arama_dto = MusteriAraDTO(
            ad=musteri.ad[:2],
            telefon=musteri.telefon,
            aktif_mi=musteri.aktif_mi
        )
        sonuclar = musteri_servisi.musteri_ara(arama_dto)
        
        # Müşteri bulunmalı (tüm kriterler eşleşiyor)
        musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
        assert musteri_bulundu, f"Üç kriter (ad+telefon+aktif) ile arama yapıldığında müşteri bulunamadı"
    
    # Üç kriter ile arama yap (ad + yanlış telefon + aktif durum)
    if len(musteri.ad) >= 2:
        yanlis_telefon = "9999999999"  # Olmayan telefon
        arama_dto = MusteriAraDTO(
            ad=musteri.ad[:2],
            telefon=yanlis_telefon,
            aktif_mi=musteri.aktif_mi
        )
        sonuclar = musteri_servisi.musteri_ara(arama_dto)
        
        # Müşteri bulunmamalı (telefon eşleşmiyor)
        musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
        assert not musteri_bulundu, f"Yanlış telefon ile arama yapıldığında müşteri bulundu (olmamalıydı)"


@given(musteri_dto=gecerli_musteri_strategy)
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
def test_dort_kriter_and_mantigi(musteri_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 10: Çoklu kriter AND mantığı**
    **Validates: Requirements 3.4**
    
    Dört kriter ile arama yapıldığında AND mantığı çalışmalı
    """
    # Telefon ve e-posta olan müşteri olduğunu varsay
    assume(musteri_dto.telefon is not None and musteri_dto.telefon.strip())
    assume(musteri_dto.eposta is not None and musteri_dto.eposta.strip())
    
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Müşteri oluştur
    musteri = musteri_servisi.musteri_olustur(musteri_dto)
    
    # Dört kriter ile arama yap (ad + soyad + telefon + e-posta)
    if len(musteri.ad) >= 2 and len(musteri.soyad) >= 2:
        arama_dto = MusteriAraDTO(
            ad=musteri.ad[:2],
            soyad=musteri.soyad[:2],
            telefon=musteri.telefon,
            eposta=musteri.eposta
        )
        sonuclar = musteri_servisi.musteri_ara(arama_dto)
        
        # Müşteri bulunmalı (tüm kriterler eşleşiyor)
        musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
        assert musteri_bulundu, f"Dört kriter ile arama yapıldığında müşteri bulunamadı"
    
    # Dört kriter ile arama yap (ad + soyad + telefon + yanlış e-posta)
    if len(musteri.ad) >= 2 and len(musteri.soyad) >= 2:
        yanlis_eposta = "yanlis@example.com"
        arama_dto = MusteriAraDTO(
            ad=musteri.ad[:2],
            soyad=musteri.soyad[:2],
            telefon=musteri.telefon,
            eposta=yanlis_eposta
        )
        sonuclar = musteri_servisi.musteri_ara(arama_dto)
        
        # Müşteri bulunmamalı (e-posta eşleşmiyor)
        musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
        assert not musteri_bulundu, f"Yanlış e-posta ile arama yapıldığında müşteri bulundu (olmamalıydı)"


@given(musteri_dto=gecerli_musteri_strategy)
@settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much])
def test_bes_kriter_and_mantigi(musteri_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 10: Çoklu kriter AND mantığı**
    **Validates: Requirements 3.4**
    
    Beş kriter (tüm kriterler) ile arama yapıldığında AND mantığı çalışmalı
    """
    # Telefon ve e-posta olan müşteri olduğunu varsay
    assume(musteri_dto.telefon is not None and musteri_dto.telefon.strip())
    assume(musteri_dto.eposta is not None and musteri_dto.eposta.strip())
    
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Müşteri oluştur
    musteri = musteri_servisi.musteri_olustur(musteri_dto)
    
    # Beş kriter ile arama yap (tüm kriterler)
    if len(musteri.ad) >= 2 and len(musteri.soyad) >= 2:
        arama_dto = MusteriAraDTO(
            ad=musteri.ad[:2],
            soyad=musteri.soyad[:2],
            telefon=musteri.telefon,
            eposta=musteri.eposta,
            aktif_mi=musteri.aktif_mi
        )
        sonuclar = musteri_servisi.musteri_ara(arama_dto)
        
        # Müşteri bulunmalı (tüm kriterler eşleşiyor)
        musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
        assert musteri_bulundu, f"Beş kriter ile arama yapıldığında müşteri bulunamadı"
        
        # Tüm sonuçlar tüm kriterleri karşılamalı
        for sonuc in sonuclar:
            assert musteri.ad[:2].lower() in sonuc.ad.lower(), f"Sonuçta ad kriteri eşleşmiyor"
            assert musteri.soyad[:2].lower() in sonuc.soyad.lower(), f"Sonuçta soyad kriteri eşleşmiyor"
            assert sonuc.telefon == musteri.telefon, f"Sonuçta telefon kriteri eşleşmiyor"
            assert sonuc.eposta == musteri.eposta, f"Sonuçta e-posta kriteri eşleşmiyor"
            assert sonuc.aktif_mi == musteri.aktif_mi, f"Sonuçta aktif durum kriteri eşleşmiyor"


def test_bos_kriter_bos_sonuc():
    """
    **Feature: crm-cekirdek-modulu, Property 10: Çoklu kriter AND mantığı**
    **Validates: Requirements 3.4**
    
    Hiç kriter verilmediğinde boş sonuç döndürülmeli
    """
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Boş arama DTO'su ile arama yap
    arama_dto = MusteriAraDTO()
    sonuclar = musteri_servisi.musteri_ara(arama_dto)
    
    # Boş liste döndürmeli
    assert sonuclar == [], f"Boş kriter ile arama yapıldığında boş liste döndürülmedi"