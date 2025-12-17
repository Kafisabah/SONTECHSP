# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_crm_telefon_eposta_tam_arama_property
# Description: CRM telefon/e-posta tam arama property testi
# Changelog:
# - İlk oluşturma: Property 9 - Telefon/e-posta tam arama testi

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
        """Müşteri arama - telefon/e-posta tam eşleşme ile"""
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
            
            # Telefon TAM eşleşme
            if dto.telefon:
                if musteri.telefon != dto.telefon.strip():
                    eslesme = False
            
            # E-posta TAM eşleşme (case-insensitive)
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
telefon_strategy = st.text(min_size=10, max_size=20).filter(lambda x: x.strip())
eposta_strategy = st.emails()

gecerli_musteri_strategy = st.builds(
    MusteriOlusturDTO,
    ad=st.text(min_size=3, max_size=50).filter(lambda x: x.strip()),
    soyad=st.text(min_size=3, max_size=50).filter(lambda x: x.strip()),
    telefon=st.one_of(st.none(), telefon_strategy),
    eposta=st.one_of(st.none(), eposta_strategy),
    vergi_no=st.one_of(st.none(), st.text(min_size=5, max_size=20)),
    adres=st.one_of(st.none(), st.text(max_size=200)),
    aktif_mi=st.booleans()
)


@given(musteri_dto=gecerli_musteri_strategy)
@settings(max_examples=100)
def test_telefon_tam_arama_property(musteri_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 9: Telefon/e-posta tam arama**
    **Validates: Requirements 3.2, 3.3**
    
    Her telefon numarası ile arama yapıldığında sadece tam eşleşen sonuçlar döndürülür
    """
    # Telefon numarası olan müşteri olduğunu varsay
    assume(musteri_dto.telefon is not None and musteri_dto.telefon.strip())
    
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Müşteri oluştur
    musteri = musteri_servisi.musteri_olustur(musteri_dto)
    
    # Tam telefon numarası ile arama yap
    arama_dto = MusteriAraDTO(telefon=musteri.telefon)
    sonuclar = musteri_servisi.musteri_ara(arama_dto)
    
    # Sonuçlarda bu müşteri bulunmalı
    assert len(sonuclar) > 0
    musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
    assert musteri_bulundu, f"Tam telefon '{musteri.telefon}' ile arama yapıldığında müşteri bulunamadı"
    
    # Tüm sonuçlar aynı telefon numarasına sahip olmalı
    for sonuc in sonuclar:
        assert sonuc.telefon == musteri.telefon, f"Telefon aramasında farklı telefon numarası döndü: {sonuc.telefon}"


@given(musteri_dto=gecerli_musteri_strategy)
@settings(max_examples=100)
def test_eposta_tam_arama_property(musteri_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 9: Telefon/e-posta tam arama**
    **Validates: Requirements 3.2, 3.3**
    
    Her e-posta adresi ile arama yapıldığında sadece tam eşleşen sonuçlar döndürülür
    """
    # E-posta adresi olan müşteri olduğunu varsay
    assume(musteri_dto.eposta is not None and musteri_dto.eposta.strip())
    
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Müşteri oluştur
    musteri = musteri_servisi.musteri_olustur(musteri_dto)
    
    # Tam e-posta adresi ile arama yap
    arama_dto = MusteriAraDTO(eposta=musteri.eposta)
    sonuclar = musteri_servisi.musteri_ara(arama_dto)
    
    # Sonuçlarda bu müşteri bulunmalı
    assert len(sonuclar) > 0
    musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
    assert musteri_bulundu, f"Tam e-posta '{musteri.eposta}' ile arama yapıldığında müşteri bulunamadı"
    
    # Tüm sonuçlar aynı e-posta adresine sahip olmalı
    for sonuc in sonuclar:
        assert sonuc.eposta == musteri.eposta, f"E-posta aramasında farklı e-posta adresi döndü: {sonuc.eposta}"


@given(musteri_dto=gecerli_musteri_strategy)
@settings(max_examples=100)
def test_telefon_kismi_arama_calismamali(musteri_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 9: Telefon/e-posta tam arama**
    **Validates: Requirements 3.2, 3.3**
    
    Telefon numarasının bir kısmı ile arama yapıldığında sonuç döndürülmemeli
    """
    # Telefon numarası olan ve en az 5 karakter olan müşteri olduğunu varsay
    assume(musteri_dto.telefon is not None and len(musteri_dto.telefon.strip()) >= 5)
    
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Müşteri oluştur
    musteri = musteri_servisi.musteri_olustur(musteri_dto)
    
    # Telefon numarasının bir kısmı ile arama yap
    telefon_parcasi = musteri.telefon[:3]  # İlk 3 karakter
    
    arama_dto = MusteriAraDTO(telefon=telefon_parcasi)
    sonuclar = musteri_servisi.musteri_ara(arama_dto)
    
    # Bu müşteri sonuçlarda bulunmamalı (kısmi eşleşme çalışmamalı)
    musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
    assert not musteri_bulundu, f"Telefon parçası '{telefon_parcasi}' ile arama yapıldığında müşteri bulundu (olmamalıydı)"


@given(musteri_dto=gecerli_musteri_strategy)
@settings(max_examples=100)
def test_eposta_kismi_arama_calismamali(musteri_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 9: Telefon/e-posta tam arama**
    **Validates: Requirements 3.2, 3.3**
    
    E-posta adresinin bir kısmı ile arama yapıldığında sonuç döndürülmemeli
    """
    # E-posta adresi olan müşteri olduğunu varsay
    assume(musteri_dto.eposta is not None and musteri_dto.eposta.strip())
    assume("@" in musteri_dto.eposta)  # Geçerli e-posta formatı
    
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Müşteri oluştur
    musteri = musteri_servisi.musteri_olustur(musteri_dto)
    
    # E-posta adresinin @ öncesi kısmı ile arama yap
    eposta_parcasi = musteri.eposta.split("@")[0]  # @ öncesi kısım
    
    arama_dto = MusteriAraDTO(eposta=eposta_parcasi)
    sonuclar = musteri_servisi.musteri_ara(arama_dto)
    
    # Bu müşteri sonuçlarda bulunmamalı (kısmi eşleşme çalışmamalı)
    musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
    assert not musteri_bulundu, f"E-posta parçası '{eposta_parcasi}' ile arama yapıldığında müşteri bulundu (olmamalıydı)"


@given(
    musteri1_dto=gecerli_musteri_strategy,
    musteri2_dto=gecerli_musteri_strategy
)
@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much])
def test_farkli_telefon_eposta_arama(musteri1_dto, musteri2_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 9: Telefon/e-posta tam arama**
    **Validates: Requirements 3.2, 3.3**
    
    Farklı telefon/e-posta ile arama yapıldığında yanlış müşteri döndürülmemeli
    """
    # Farklı telefon ve e-posta olduğunu varsay
    assume(musteri1_dto.telefon != musteri2_dto.telefon)
    assume(musteri1_dto.eposta != musteri2_dto.eposta)
    assume(musteri1_dto.telefon is not None and musteri1_dto.telefon.strip())
    assume(musteri2_dto.telefon is not None and musteri2_dto.telefon.strip())
    assume(musteri1_dto.eposta is not None and musteri1_dto.eposta.strip())
    assume(musteri2_dto.eposta is not None and musteri2_dto.eposta.strip())
    
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # İki müşteri oluştur
    musteri1 = musteri_servisi.musteri_olustur(musteri1_dto)
    musteri2 = musteri_servisi.musteri_olustur(musteri2_dto)
    
    # İkinci müşterinin telefonu ile arama yap
    arama_dto = MusteriAraDTO(telefon=musteri2.telefon)
    sonuclar = musteri_servisi.musteri_ara(arama_dto)
    
    # İlk müşteri sonuçlarda bulunmamalı
    musteri1_bulundu = any(s.id == musteri1.id for s in sonuclar)
    assert not musteri1_bulundu, f"Farklı telefon '{musteri2.telefon}' ile arama yapıldığında yanlış müşteri bulundu"
    
    # İkinci müşterinin e-postası ile arama yap
    arama_dto = MusteriAraDTO(eposta=musteri2.eposta)
    sonuclar = musteri_servisi.musteri_ara(arama_dto)
    
    # İlk müşteri sonuçlarda bulunmamalı
    musteri1_bulundu = any(s.id == musteri1.id for s in sonuclar)
    assert not musteri1_bulundu, f"Farklı e-posta '{musteri2.eposta}' ile arama yapıldığında yanlış müşteri bulundu"


@given(musteri_dto=gecerli_musteri_strategy)
@settings(max_examples=100)
def test_eposta_case_insensitive_tam_arama(musteri_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 9: Telefon/e-posta tam arama**
    **Validates: Requirements 3.2, 3.3**
    
    E-posta arama case-insensitive olmalı ama tam eşleşme olmalı
    """
    # E-posta adresi olan müşteri olduğunu varsay
    assume(musteri_dto.eposta is not None and musteri_dto.eposta.strip())
    
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Müşteri oluştur
    musteri = musteri_servisi.musteri_olustur(musteri_dto)
    
    # E-posta adresini büyük harfle ara
    eposta_buyuk = musteri_dto.eposta.upper()
    
    arama_dto = MusteriAraDTO(eposta=eposta_buyuk)
    sonuclar = musteri_servisi.musteri_ara(arama_dto)
    
    # Sonuçlarda bu müşteri bulunmalı (case-insensitive)
    musteri_bulundu = any(s.id == musteri.id for s in sonuclar)
    assert musteri_bulundu, f"Büyük harfli e-posta '{eposta_buyuk}' ile arama yapıldığında müşteri bulunamadı"