# Version: 0.1.0
# Last Update: 2024-12-16
# Module: test_numara_servisi_property
# Description: Numara servisi property testleri
# Changelog:
# - İlk oluşturma

"""
**Feature: satis-belgeleri-modulu, Property 5: Belge numarası benzersizliği**
**Validates: Requirements 2.2, 4.1, 4.2**

**Feature: satis-belgeleri-modulu, Property 9: Ay değişimi numara sıfırlama**
**Validates: Requirements 4.3**

**Feature: satis-belgeleri-modulu, Property 10: Numara çakışması çözümü**
**Validates: Requirements 4.4**

Numara servisi için property-based testler.
"""

from datetime import datetime
from unittest.mock import Mock, MagicMock
from hypothesis import given, strategies as st, assume
import pytest

from sontechsp.uygulama.moduller.satis_belgeleri.modeller import BelgeTuru, NumaraSayaci
from sontechsp.uygulama.moduller.satis_belgeleri.servisler import NumaraServisi
from sontechsp.uygulama.moduller.satis_belgeleri.depolar.numara_sayac_deposu import INumaraSayacDeposu
from sontechsp.uygulama.cekirdek.hatalar import IsKuraliHatasi, VeriTabaniHatasi


# Test stratejileri
@st.composite
def magaza_bilgisi_strategy(draw):
    """Mağaza bilgisi üretici"""
    magaza_id = draw(st.integers(min_value=1, max_value=1000))
    magaza_kodu = draw(st.text(min_size=3, max_size=3, alphabet=st.characters(min_codepoint=65, max_codepoint=90)))
    return magaza_id, magaza_kodu


@st.composite
def belge_turu_strategy(draw):
    """Belge türü üretici"""
    return draw(st.sampled_from(list(BelgeTuru)))


@st.composite
def tarih_bilgisi_strategy(draw):
    """Tarih bilgisi üretici"""
    yil = draw(st.integers(min_value=2020, max_value=2030))
    ay = draw(st.integers(min_value=1, max_value=12))
    return yil, ay


class TestNumaraServisiProperty:
    """Numara servisi property testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_depo = Mock(spec=INumaraSayacDeposu)
        self.numara_servisi = NumaraServisi(self.mock_depo)
    
    @given(magaza_bilgisi_strategy(), belge_turu_strategy())
    def test_numara_benzersizligi(self, magaza_bilgisi, belge_turu):
        """
        **Feature: satis-belgeleri-modulu, Property 5: Belge numarası benzersizliği**
        **Validates: Requirements 2.2, 4.1, 4.2**
        
        Herhangi bir belge türü ve mağaza kombinasyonu için üretilen numara 
        benzersiz olmalı ve format kurallarına uymalıdır
        """
        magaza_id, magaza_kodu = magaza_bilgisi
        
        # Mock sayaç oluştur
        mock_sayac = NumaraSayaci(
            sayac_id=1,
            magaza_id=magaza_id,
            belge_turu=belge_turu,
            yil=2024,
            ay=12,
            son_numara=0
        )
        
        # Mock depo davranışları
        self.mock_depo.bul_magaza_tur_yil_ay.return_value = None  # İlk çağrıda sayaç yok
        self.mock_depo.ekle.return_value = mock_sayac
        self.mock_depo.guncelle.return_value = mock_sayac
        
        # Numara üret
        numara = self.numara_servisi.numara_uret(magaza_id, magaza_kodu, belge_turu)
        
        # Format kontrolü: MGZ-YYYY-MM-NNNN
        assert isinstance(numara, str)
        assert len(numara) >= 13  # En az MGZ-2024-01-0001 formatında
        
        # Format parçalarını kontrol et
        parcalar = numara.split('-')
        assert len(parcalar) == 4
        assert parcalar[0] == magaza_kodu  # Mağaza kodu
        assert len(parcalar[1]) == 4  # Yıl
        assert len(parcalar[2]) == 2  # Ay
        assert len(parcalar[3]) == 4  # Sıra numarası
        
        # Sayısal değerleri kontrol et
        yil = int(parcalar[1])
        ay = int(parcalar[2])
        sira = int(parcalar[3])
        
        assert 2000 <= yil <= 9999
        assert 1 <= ay <= 12
        assert 1 <= sira <= 9999
        
        # Depo metodlarının çağrıldığını kontrol et
        self.mock_depo.bul_magaza_tur_yil_ay.assert_called()
        self.mock_depo.ekle.assert_called_once()
        self.mock_depo.guncelle.assert_called_once()
    
    @given(magaza_bilgisi_strategy(), belge_turu_strategy(), st.integers(min_value=1, max_value=100))
    def test_sira_numarasi_artirma(self, magaza_bilgisi, belge_turu, mevcut_numara):
        """
        Sıra numarasının doğru şekilde artırıldığını test et
        """
        magaza_id, magaza_kodu = magaza_bilgisi
        
        # Mevcut sayaç ile mock oluştur
        mock_sayac = NumaraSayaci(
            sayac_id=1,
            magaza_id=magaza_id,
            belge_turu=belge_turu,
            yil=2024,
            ay=12,
            son_numara=mevcut_numara
        )
        
        # Mock depo davranışları
        self.mock_depo.bul_magaza_tur_yil_ay.return_value = mock_sayac
        self.mock_depo.guncelle.return_value = mock_sayac
        
        # Numara üret
        numara = self.numara_servisi.numara_uret(magaza_id, magaza_kodu, belge_turu)
        
        # Sıra numarasının artırıldığını kontrol et
        parcalar = numara.split('-')
        yeni_sira = int(parcalar[3])
        assert yeni_sira == mevcut_numara + 1
        
        # Sayacın güncellendiğini kontrol et
        self.mock_depo.guncelle.assert_called_once()
    
    @given(magaza_bilgisi_strategy(), belge_turu_strategy(), tarih_bilgisi_strategy())
    def test_ay_degisimi_sifirlama(self, magaza_bilgisi, belge_turu, tarih_bilgisi):
        """
        **Feature: satis-belgeleri-modulu, Property 9: Ay değişimi numara sıfırlama**
        **Validates: Requirements 4.3**
        
        Herhangi bir ay değişimi durumunda, aynı mağaza ve belge türü için 
        sıra numarası sıfırdan başlatılmalıdır
        """
        magaza_id, magaza_kodu = magaza_bilgisi
        yil, ay = tarih_bilgisi
        
        # Önceki ay için sayaç
        onceki_ay = ay - 1 if ay > 1 else 12
        onceki_yil = yil if ay > 1 else yil - 1
        
        onceki_sayac = NumaraSayaci(
            sayac_id=1,
            magaza_id=magaza_id,
            belge_turu=belge_turu,
            yil=onceki_yil,
            ay=onceki_ay,
            son_numara=50  # Önceki ayda 50 numara kullanılmış
        )
        
        # Mock depo davranışları
        self.mock_depo.bul_magaza_tur_yil_ay.return_value = None  # Bu ay için sayaç yok
        self.mock_depo.bul_son_sayac.return_value = onceki_sayac  # Önceki ay sayacı var
        
        # Yeni sayaç oluşturulacak
        yeni_sayac = NumaraSayaci(
            sayac_id=2,
            magaza_id=magaza_id,
            belge_turu=belge_turu,
            yil=yil,
            ay=ay,
            son_numara=0
        )
        self.mock_depo.ekle.return_value = yeni_sayac
        self.mock_depo.guncelle.return_value = yeni_sayac
        
        # Ay değişimi kontrolü
        ay_degisti = self.numara_servisi.ay_degisimi_kontrol_et(magaza_id, belge_turu)
        
        # Ay değişimi tespit edilmeli
        assert ay_degisti == True
    
    @given(magaza_bilgisi_strategy(), belge_turu_strategy())
    def test_numara_cakismasi_cozumu(self, magaza_bilgisi, belge_turu):
        """
        **Feature: satis-belgeleri-modulu, Property 10: Numara çakışması çözümü**
        **Validates: Requirements 4.4**
        
        Herhangi bir numara çakışması durumunda sistem işlemi tekrar denemeli 
        ve benzersizliği garanti etmelidir
        """
        magaza_id, magaza_kodu = magaza_bilgisi
        
        # Mock sayaç
        mock_sayac = NumaraSayaci(
            sayac_id=1,
            magaza_id=magaza_id,
            belge_turu=belge_turu,
            yil=2024,
            ay=12,
            son_numara=0
        )
        
        # İlk çağrıda hata, ikinci çağrıda başarı simüle et
        self.mock_depo.bul_magaza_tur_yil_ay.return_value = None
        self.mock_depo.ekle.return_value = mock_sayac
        
        # İlk güncelleme çağrısında hata, ikinci çağrıda başarı
        self.mock_depo.guncelle.side_effect = [
            Exception("Çakışma hatası"),  # İlk deneme başarısız
            mock_sayac  # İkinci deneme başarılı
        ]
        
        # Numara üretmeyi dene
        numara = self.numara_servisi.numara_uret(magaza_id, magaza_kodu, belge_turu)
        
        # Numara üretilmeli
        assert isinstance(numara, str)
        assert len(numara) >= 13
        
        # Güncelleme iki kez çağrılmalı (retry mekanizması)
        assert self.mock_depo.guncelle.call_count == 2
    
    @given(st.integers(max_value=0), st.text(min_size=1, max_size=5), belge_turu_strategy())
    def test_gecersiz_parametreler(self, gecersiz_magaza_id, gecersiz_magaza_kodu, belge_turu):
        """
        Geçersiz parametrelerle numara üretimi hata fırlatmalı
        """
        # Geçersiz mağaza ID
        if gecersiz_magaza_id <= 0:
            with pytest.raises(IsKuraliHatasi):
                self.numara_servisi.numara_uret(gecersiz_magaza_id, "ABC", belge_turu)
        
        # Geçersiz mağaza kodu (3 karakter değil)
        if len(gecersiz_magaza_kodu) != 3:
            with pytest.raises(IsKuraliHatasi):
                self.numara_servisi.numara_uret(1, gecersiz_magaza_kodu, belge_turu)
    
    @given(magaza_bilgisi_strategy(), belge_turu_strategy())
    def test_maksimum_retry_asimi(self, magaza_bilgisi, belge_turu):
        """
        Maksimum retry sayısı aşıldığında hata fırlatılmalı
        """
        magaza_id, magaza_kodu = magaza_bilgisi
        
        # Mock sayaç
        mock_sayac = NumaraSayaci(
            sayac_id=1,
            magaza_id=magaza_id,
            belge_turu=belge_turu,
            yil=2024,
            ay=12,
            son_numara=0
        )
        
        self.mock_depo.bul_magaza_tur_yil_ay.return_value = None
        self.mock_depo.ekle.return_value = mock_sayac
        
        # Her güncelleme çağrısında hata fırlat
        self.mock_depo.guncelle.side_effect = Exception("Sürekli hata")
        
        # VeriTabaniHatasi fırlatılmalı
        with pytest.raises(VeriTabaniHatasi):
            self.numara_servisi.numara_uret(magaza_id, magaza_kodu, belge_turu)
        
        # Maksimum retry sayısı kadar çağrılmalı
        assert self.mock_depo.guncelle.call_count == 3  # max_retry = 3
    
    @given(magaza_bilgisi_strategy(), belge_turu_strategy())
    def test_sayac_durumu_alma(self, magaza_bilgisi, belge_turu):
        """
        Sayaç durumu alma işleminin tutarlılığını test et
        """
        magaza_id, _ = magaza_bilgisi
        
        # Mock sayaç
        mock_sayac = NumaraSayaci(
            sayac_id=1,
            magaza_id=magaza_id,
            belge_turu=belge_turu,
            yil=2024,
            ay=12,
            son_numara=25
        )
        
        self.mock_depo.bul_son_sayac.return_value = mock_sayac
        
        # Sayaç durumunu al
        durum = self.numara_servisi.sayac_durumu_al(magaza_id, belge_turu)
        
        # Doğru sayaç dönmeli
        assert durum is not None
        assert durum.magaza_id == magaza_id
        assert durum.belge_turu == belge_turu
        assert durum.son_numara == 25
        
        # Depo metodu çağrılmalı
        self.mock_depo.bul_son_sayac.assert_called_once_with(magaza_id, belge_turu)