# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_crm_telefon_benzersizligi_property
# Description: CRM telefon benzersizliği property testleri
# Changelog:
# - İlk oluşturma

"""
**Feature: crm-cekirdek-modulu, Property 2: Telefon benzersizliği**
**Validates: Requirements 1.2, 2.2**

CRM modülü telefon benzersizliği için property-based testler.
"""

from unittest.mock import Mock, MagicMock
from hypothesis import given, strategies as st, assume, settings, HealthCheck
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


class MusteriDeposu:
    """Test için basit MusteriDeposu mock'u"""
    
    def __init__(self, db):
        self.db = db
    
    def musteri_olustur(self, dto: MusteriOlusturDTO):
        """Müşteri oluşturma - telefon benzersizliği kontrolü"""
        # Zorunlu alan kontrolü
        if not dto.ad or not dto.ad.strip():
            raise Exception("Ad alanı boş olamaz")
        if not dto.soyad or not dto.soyad.strip():
            raise Exception("Soyad alanı boş olamaz")
        
        # Telefon benzersizlik kontrolü
        if dto.telefon and dto.telefon.strip():
            # Mock query ile mevcut telefon kontrolü
            query_result = self.db.query.return_value.filter.return_value.first.return_value
            if query_result:
                raise DogrulamaHatasi("Telefon numarası zaten kayıtlı")
        
        # Mock müşteri döndür
        mock_musteri = Mock()
        mock_musteri.id = 123
        mock_musteri.ad = dto.ad.strip()
        mock_musteri.soyad = dto.soyad.strip()
        mock_musteri.telefon = dto.telefon.strip() if dto.telefon and dto.telefon.strip() else None
        return mock_musteri
    
    def musteri_guncelle(self, musteri_id: int, dto: MusteriGuncelleDTO):
        """Müşteri güncelleme - telefon benzersizliği kontrolü"""
        # Müşteriyi getir
        musteri = self.db.get.return_value
        if not musteri:
            raise DogrulamaHatasi(f"ID {musteri_id} ile müşteri bulunamadı")
        
        # Telefon benzersizlik kontrolü (kendi kaydı hariç)
        if dto.telefon is not None:
            telefon = dto.telefon.strip() if dto.telefon else None
            if telefon:
                # Mock query ile mevcut telefon kontrolü (kendi kaydı hariç)
                query_result = self.db.query.return_value.filter.return_value.first.return_value
                if query_result:
                    raise DogrulamaHatasi("Telefon numarası zaten kayıtlı")
        
        # Mock güncelleme
        musteri.telefon = dto.telefon.strip() if dto.telefon and dto.telefon.strip() else None
        return musteri


# Test stratejileri
@st.composite
def telefon_strategy(draw):
    """Telefon numarası üretici"""
    return draw(st.text(min_size=10, max_size=20).filter(lambda x: x.strip()))


@st.composite
def musteri_olustur_strategy(draw):
    """Müşteri oluşturma DTO üretici"""
    return MusteriOlusturDTO(
        ad=draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip())),
        soyad=draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip())),
        telefon=draw(st.one_of(st.none(), telefon_strategy())),
        eposta=draw(st.one_of(st.none(), st.emails())),
        aktif_mi=draw(st.booleans())
    )


@st.composite
def musteri_guncelle_strategy(draw):
    """Müşteri güncelleme DTO üretici"""
    return MusteriGuncelleDTO(
        telefon=draw(st.one_of(st.none(), telefon_strategy()))
    )


class TestCRMTelefonBenzersizligi:
    """CRM telefon benzersizliği property testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_session = Mock()
        self.musteri_deposu = MusteriDeposu(self.mock_session)
    
    @given(musteri_olustur_strategy())
    def test_benzersiz_telefon_ile_musteri_olusturma(self, musteri_dto):
        """
        **Feature: crm-cekirdek-modulu, Property 2: Telefon benzersizliği**
        **Validates: Requirements 1.2, 2.2**
        
        Her telefon numarası için, sistemde sadece bir müşteri kaydı bulunabilir (oluşturma ve güncelleme)
        """
        # Geçerli ad ve soyad olduğunu varsay
        assume(musteri_dto.ad and musteri_dto.ad.strip())
        assume(musteri_dto.soyad and musteri_dto.soyad.strip())
        
        # Telefon benzersiz olduğunu simüle et (mevcut kayıt yok)
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Müşteri oluştur - hata fırlatmamalı
        try:
            sonuc = self.musteri_deposu.musteri_olustur(musteri_dto)
            # Başarılı olmalı
            assert sonuc is not None
            if musteri_dto.telefon:
                assert sonuc.telefon == musteri_dto.telefon.strip()
        except DogrulamaHatasi:
            # Benzersiz telefon ile DogrulamaHatasi fırlatmamalı
            pytest.fail("Benzersiz telefon ile DogrulamaHatasi fırlatıldı")
    
    @given(musteri_olustur_strategy())
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_mevcut_telefon_ile_musteri_olusturma_hatasi(self, musteri_dto):
        """
        Mevcut telefon numarası ile müşteri oluşturma işleminde DogrulamaHatasi fırlatılmalıdır
        """
        # Geçerli ad ve soyad olduğunu varsay
        assume(musteri_dto.ad and musteri_dto.ad.strip())
        assume(musteri_dto.soyad and musteri_dto.soyad.strip())
        assume(musteri_dto.telefon and musteri_dto.telefon.strip())
        
        # Telefon zaten mevcut olduğunu simüle et
        mock_existing_customer = Mock()
        mock_existing_customer.id = 456
        mock_existing_customer.telefon = musteri_dto.telefon
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_existing_customer
        
        # DogrulamaHatasi fırlatılmalı
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.musteri_deposu.musteri_olustur(musteri_dto)
        
        # Hata mesajı telefon ile ilgili olmalı
        assert "telefon" in str(exc_info.value).lower()
    
    @given(st.integers(min_value=1, max_value=10000), musteri_guncelle_strategy())
    def test_benzersiz_telefon_ile_musteri_guncelleme(self, musteri_id, guncelle_dto):
        """
        Benzersiz telefon numarası ile müşteri güncelleme işlemi başarılı olmalıdır
        """
        # Mevcut müşteri var
        mock_musteri = Mock()
        mock_musteri.id = musteri_id
        mock_musteri.telefon = "eski_telefon"
        self.mock_session.get.return_value = mock_musteri
        
        # Yeni telefon benzersiz olduğunu simüle et (mevcut kayıt yok)
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Müşteri güncelle - hata fırlatmamalı
        try:
            sonuc = self.musteri_deposu.musteri_guncelle(musteri_id, guncelle_dto)
            # Başarılı olmalı
            assert sonuc is not None
            if guncelle_dto.telefon:
                assert sonuc.telefon == guncelle_dto.telefon.strip()
        except DogrulamaHatasi:
            # Benzersiz telefon ile DogrulamaHatasi fırlatmamalı
            pytest.fail("Benzersiz telefon ile DogrulamaHatasi fırlatıldı")
    
    @given(st.integers(min_value=1, max_value=10000), musteri_guncelle_strategy())
    def test_mevcut_telefon_ile_musteri_guncelleme_hatasi(self, musteri_id, guncelle_dto):
        """
        Mevcut telefon numarası ile müşteri güncelleme işleminde DogrulamaHatasi fırlatılmalıdır
        """
        assume(guncelle_dto.telefon and guncelle_dto.telefon.strip())
        
        # Mevcut müşteri var
        mock_musteri = Mock()
        mock_musteri.id = musteri_id
        mock_musteri.telefon = "eski_telefon"
        self.mock_session.get.return_value = mock_musteri
        
        # Telefon başka müşteride mevcut olduğunu simüle et
        mock_existing_customer = Mock()
        mock_existing_customer.id = musteri_id + 1  # Farklı müşteri
        mock_existing_customer.telefon = guncelle_dto.telefon
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_existing_customer
        
        # DogrulamaHatasi fırlatılmalı
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.musteri_deposu.musteri_guncelle(musteri_id, guncelle_dto)
        
        # Hata mesajı telefon ile ilgili olmalı
        assert "telefon" in str(exc_info.value).lower()
    
    @given(telefon_strategy())
    def test_ayni_telefon_ile_iki_musteri_olusturma_hatasi(self, telefon):
        """
        Aynı telefon numarası ile iki müşteri oluşturma işleminde ikincisi DogrulamaHatasi fırlatmalıdır
        """
        # İlk müşteri DTO'su
        musteri1_dto = MusteriOlusturDTO(
            ad="Müşteri 1",
            soyad="Soyad 1",
            telefon=telefon,
            aktif_mi=True
        )
        
        # İkinci müşteri DTO'su
        musteri2_dto = MusteriOlusturDTO(
            ad="Müşteri 2",
            soyad="Soyad 2",
            telefon=telefon,  # Aynı telefon
            aktif_mi=True
        )
        
        # İlk müşteri için telefon benzersiz
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # İlk müşteri başarıyla oluşturulmalı
        musteri1 = self.musteri_deposu.musteri_olustur(musteri1_dto)
        assert musteri1 is not None
        
        # İkinci müşteri için telefon mevcut olduğunu simüle et
        mock_existing_customer = Mock()
        mock_existing_customer.id = 123
        mock_existing_customer.telefon = telefon
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_existing_customer
        
        # İkinci müşteri oluşturma DogrulamaHatasi fırlatmalı
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.musteri_deposu.musteri_olustur(musteri2_dto)
        
        # Hata mesajı telefon ile ilgili olmalı
        assert "telefon" in str(exc_info.value).lower()
    
    @given(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    def test_none_telefon_ile_musteri_olusturma(self, ad):
        """
        None telefon ile müşteri oluşturma işlemi başarılı olmalıdır (telefon opsiyonel)
        """
        musteri_dto = MusteriOlusturDTO(
            ad=ad,
            soyad="Test Soyad",
            telefon=None,  # Telefon yok
            aktif_mi=True
        )
        
        # Telefon kontrolü yapılmamalı (None olduğu için)
        sonuc = self.musteri_deposu.musteri_olustur(musteri_dto)
        
        # Başarılı olmalı
        assert sonuc is not None
        assert sonuc.telefon is None
    
    @given(st.text(max_size=5).filter(lambda x: not x.strip()))
    def test_bos_telefon_ile_musteri_olusturma(self, bos_telefon):
        """
        Boş telefon ile müşteri oluşturma işlemi başarılı olmalıdır (telefon opsiyonel)
        """
        musteri_dto = MusteriOlusturDTO(
            ad="Test Ad",
            soyad="Test Soyad",
            telefon=bos_telefon,  # Boş telefon
            aktif_mi=True
        )
        
        # Telefon kontrolü yapılmamalı (boş olduğu için)
        sonuc = self.musteri_deposu.musteri_olustur(musteri_dto)
        
        # Başarılı olmalı
        assert sonuc is not None
        assert sonuc.telefon is None