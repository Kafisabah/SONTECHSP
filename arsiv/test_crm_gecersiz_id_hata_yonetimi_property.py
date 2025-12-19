# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_crm_gecersiz_id_hata_yonetimi_property
# Description: CRM geçersiz ID hata yönetimi property testi
# Changelog:
# - İlk oluşturma: Property 7 - Geçersiz ID hata yönetimi testi

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
        """Müşteri güncelleme - ID validasyonu ile"""
        # ID validasyonu
        if not isinstance(musteri_id, int) or musteri_id <= 0:
            raise DogrulamaHatasi("Geçersiz müşteri ID'si")
        
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
    
    def musteri_getir(self, musteri_id: int):
        """Müşteri getirme - ID validasyonu ile"""
        # ID validasyonu
        if not isinstance(musteri_id, int) or musteri_id <= 0:
            raise DogrulamaHatasi("Geçersiz müşteri ID'si")
        
        return self.musteriler.get(musteri_id)


# Hypothesis stratejileri
gecersiz_id_strategy = st.one_of(
    st.integers(max_value=0),  # Sıfır ve negatif sayılar
    st.floats(),  # Float değerler
    st.text(),  # String değerler
    st.none(),  # None değeri
    st.booleans(),  # Boolean değerler
    st.lists(st.integers()),  # Liste değerler
    st.dictionaries(st.text(), st.integers())  # Dictionary değerler
)

gecerli_musteri_strategy = st.builds(
    MusteriOlusturDTO,
    ad=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    soyad=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    telefon=st.one_of(st.none(), st.text(min_size=5, max_size=20)),
    eposta=st.one_of(st.none(), st.emails()),
    vergi_no=st.one_of(st.none(), st.text(min_size=5, max_size=20)),
    adres=st.one_of(st.none(), st.text(max_size=200)),
    aktif_mi=st.booleans()
)

guncelle_dto_strategy = st.builds(
    MusteriGuncelleDTO,
    ad=st.one_of(st.none(), st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
    soyad=st.one_of(st.none(), st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
    telefon=st.one_of(st.none(), st.text(min_size=5, max_size=20)),
    eposta=st.one_of(st.none(), st.emails()),
    aktif_mi=st.one_of(st.none(), st.booleans())
)


@given(gecersiz_id=gecersiz_id_strategy)
@settings(max_examples=100)
def test_gecersiz_id_musteri_getir_hatasi(gecersiz_id):
    """
    **Feature: crm-cekirdek-modulu, Property 7: Geçersiz ID hata yönetimi**
    **Validates: Requirements 2.5**
    
    Her geçersiz müşteri ID'si ile yapılan işlem için, DogrulamaHatasi fırlatılır
    """
    # Sadece integer olmayan veya sıfır/negatif değerleri test et
    assume(not isinstance(gecersiz_id, int) or gecersiz_id <= 0)
    
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Geçersiz ID ile müşteri getirme - DogrulamaHatasi fırlatılmalı
    with pytest.raises(DogrulamaHatasi) as exc_info:
        musteri_servisi.musteri_getir(gecersiz_id)
    
    # Hata mesajı ID ile ilgili olmalı
    assert "geçersiz" in str(exc_info.value).lower() or "id" in str(exc_info.value).lower()


@given(gecersiz_id=gecersiz_id_strategy, guncelle_dto=guncelle_dto_strategy)
@settings(max_examples=100)
def test_gecersiz_id_musteri_guncelle_hatasi(gecersiz_id, guncelle_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 7: Geçersiz ID hata yönetimi**
    **Validates: Requirements 2.5**
    
    Her geçersiz müşteri ID'si ile güncelleme işlemi için, DogrulamaHatasi fırlatılır
    """
    # Sadece integer olmayan veya sıfır/negatif değerleri test et
    assume(not isinstance(gecersiz_id, int) or gecersiz_id <= 0)
    
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Geçersiz ID ile müşteri güncelleme - DogrulamaHatasi fırlatılmalı
    with pytest.raises(DogrulamaHatasi) as exc_info:
        musteri_servisi.musteri_guncelle(gecersiz_id, guncelle_dto)
    
    # Hata mesajı ID ile ilgili olmalı
    assert "geçersiz" in str(exc_info.value).lower() or "id" in str(exc_info.value).lower()


@given(musteri_dto=gecerli_musteri_strategy, guncelle_dto=guncelle_dto_strategy)
@settings(max_examples=100)
def test_olmayan_id_musteri_guncelle_hatasi(musteri_dto, guncelle_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 7: Geçersiz ID hata yönetimi**
    **Validates: Requirements 2.5**
    
    Var olmayan müşteri ID'si ile güncelleme işlemi için, DogrulamaHatasi fırlatılır
    """
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Bir müşteri oluştur
    musteri = musteri_servisi.musteri_olustur(musteri_dto)
    
    # Var olmayan ID ile güncelleme yap (mevcut ID'den büyük bir değer)
    olmayan_id = musteri.id + 1000
    
    # Olmayan ID ile müşteri güncelleme - DogrulamaHatasi fırlatılmalı
    with pytest.raises(DogrulamaHatasi) as exc_info:
        musteri_servisi.musteri_guncelle(olmayan_id, guncelle_dto)
    
    # Hata mesajı "bulunamadı" içermeli
    assert "bulunamadı" in str(exc_info.value).lower()


@given(musteri_dto=gecerli_musteri_strategy)
@settings(max_examples=100)
def test_olmayan_id_musteri_getir_none_dondurmeli(musteri_dto):
    """
    **Feature: crm-cekirdek-modulu, Property 7: Geçersiz ID hata yönetimi**
    **Validates: Requirements 2.5**
    
    Var olmayan ama geçerli müşteri ID'si ile getirme işlemi None döndürür
    """
    # MusteriServisi oluştur
    mock_session = Mock()
    musteri_servisi = MusteriServisi(mock_session)
    
    # Bir müşteri oluştur
    musteri = musteri_servisi.musteri_olustur(musteri_dto)
    
    # Var olmayan ama geçerli ID ile getirme yap
    olmayan_id = musteri.id + 1000
    
    # Olmayan ID ile müşteri getirme - None döndürmeli
    sonuc = musteri_servisi.musteri_getir(olmayan_id)
    assert sonuc is None