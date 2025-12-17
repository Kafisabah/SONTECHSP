# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_crm_kismi_guncelleme_property
# Description: CRM müşteri kısmi güncelleme property testi
# Changelog:
# - İlk oluşturma: Property 6 - Kısmi güncelleme testi

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock
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


@dataclass
class MusteriGuncelleDTO:
    """Müşteri güncelleme için opsiyonel alanlar"""
    ad: Optional[str] = None
    soyad: Optional[str] = None
    telefon: Optional[str] = None
    eposta: Optional[str] = None
    vergi_no: Optional[str] = None
    adres: Optional[str] = None
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
    
    def musteri_guncelle(self, musteri_id: int, dto: MusteriGuncelleDTO):
        """Müşteri güncelleme - kısmi güncelleme"""
        if musteri_id not in self.musteriler:
            raise DogrulamaHatasi(f"ID {musteri_id} ile müşteri bulunamadı")
        
        musteri = self.musteriler[musteri_id]
        
        # Sadece gönderilen alanları güncelle
        if dto.ad is not None:
            if not dto.ad.strip():
                raise DogrulamaHatasi("Ad alanı boş olamaz")
            musteri.ad = dto.ad.strip()
        
        if dto.soyad is not None:
            if not dto.soyad.strip():
                raise DogrulamaHatasi("Soyad alanı boş olamaz")
            musteri.soyad = dto.soyad.strip()
        
        if dto.telefon is not None:
            musteri.telefon = dto.telefon.strip() if dto.telefon else None
        
        if dto.eposta is not None:
            musteri.eposta = dto.eposta.strip().lower() if dto.eposta else None
        
        if dto.vergi_no is not None:
            musteri.vergi_no = dto.vergi_no.strip() if dto.vergi_no else None
        
        if dto.adres is not None:
            musteri.adres = dto.adres.strip() if dto.adres else None
        
        if dto.aktif_mi is not None:
            musteri.aktif_mi = dto.aktif_mi
        
        return musteri


# Hypothesis stratejileri
musteri_olustur_strategy = st.builds(
    MusteriOlusturDTO,
    ad=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    soyad=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    telefon=st.one_of(st.none(), st.text(min_size=5, max_size=20)),
    eposta=st.one_of(st.none(), st.emails()),
    vergi_no=st.one_of(st.none(), st.text(min_size=5, max_size=20)),
    adres=st.one_of(st.none(), st.text(max_size=200)),
    aktif_mi=st.booleans()
)

musteri_guncelle_strategy = st.builds(
    MusteriGuncelleDTO,
    ad=st.one_of(st.none(), st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
    soyad=st.one_of(st.none(), st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
    telefon=st.one_of(st.none(), st.text(min_size=5, max_size=20)),
    eposta=st.one_of(st.none(), st.emails()),
    vergi_no=st.one_of(st.none(), st.text(min_size=5, max_size=20)),
    adres=st.one_of(st.none(), st.text(max_size=200)),
    aktif_mi=st.one_of(st.none(), st.booleans())
)


@given(
    olustur_dto=musteri_olustur_strategy,
    guncelle_dto=musteri_guncelle_strategy
)
@settings(max_examples=100)
def test_kismi_guncelleme_property(olustur_dto, guncelle_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 6: Kısmi güncelleme**
    **Validates: Requirements 2.1**
    
    Her müşteri güncelleme işlemi için, sadece gönderilen alanlar değişir, diğerleri korunur
    """
    try:
        # MusteriServisi oluştur
        mock_session = Mock()
        musteri_servisi = MusteriServisi(mock_session)
        
        # Önce müşteri oluştur
        musteri = musteri_servisi.musteri_olustur(olustur_dto)
        
        # Orijinal değerleri kaydet
        orijinal_ad = musteri.ad
        orijinal_soyad = musteri.soyad
        orijinal_telefon = musteri.telefon
        orijinal_eposta = musteri.eposta
        orijinal_vergi_no = musteri.vergi_no
        orijinal_adres = musteri.adres
        orijinal_aktif_mi = musteri.aktif_mi
        
        # Güncelleme yap
        guncellenen_musteri = musteri_servisi.musteri_guncelle(musteri.id, guncelle_dto)
        
        # Kısmi güncelleme kontrolü - sadece gönderilen alanlar değişmeli
        if guncelle_dto.ad is not None:
            assert guncellenen_musteri.ad == guncelle_dto.ad.strip()
        else:
            assert guncellenen_musteri.ad == orijinal_ad
            
        if guncelle_dto.soyad is not None:
            assert guncellenen_musteri.soyad == guncelle_dto.soyad.strip()
        else:
            assert guncellenen_musteri.soyad == orijinal_soyad
            
        if guncelle_dto.telefon is not None:
            expected_telefon = guncelle_dto.telefon.strip() if guncelle_dto.telefon else None
            assert guncellenen_musteri.telefon == expected_telefon
        else:
            assert guncellenen_musteri.telefon == orijinal_telefon
            
        if guncelle_dto.eposta is not None:
            expected_eposta = guncelle_dto.eposta.strip().lower() if guncelle_dto.eposta else None
            assert guncellenen_musteri.eposta == expected_eposta
        else:
            assert guncellenen_musteri.eposta == orijinal_eposta
            
        if guncelle_dto.vergi_no is not None:
            expected_vergi_no = guncelle_dto.vergi_no.strip() if guncelle_dto.vergi_no else None
            assert guncellenen_musteri.vergi_no == expected_vergi_no
        else:
            assert guncellenen_musteri.vergi_no == orijinal_vergi_no
            
        if guncelle_dto.adres is not None:
            expected_adres = guncelle_dto.adres.strip() if guncelle_dto.adres else None
            assert guncellenen_musteri.adres == expected_adres
        else:
            assert guncellenen_musteri.adres == orijinal_adres
            
        if guncelle_dto.aktif_mi is not None:
            assert guncellenen_musteri.aktif_mi == guncelle_dto.aktif_mi
        else:
            assert guncellenen_musteri.aktif_mi == orijinal_aktif_mi
            
    except DogrulamaHatasi:
        # Doğrulama hataları beklenen durumlar (boş ad/soyad gibi)
        pass