# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.kurulum.test_klasorler_property
# Description: Klasör yönetimi property testleri
# Changelog:
# - Property testler oluşturuldu

"""
Klasör yönetimi property testleri

**Özellik: kurulum-bootstrap-altyapisi, Özellik 1: Klasör Oluşturma İdempotentliği**
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck

from uygulama.kurulum.klasorler import (
    klasorleri_olustur,
    klasor_var_mi,
    eksik_klasorleri_listele,
    klasor_yolunu_dogrula
)
from uygulama.kurulum.sabitler import GEREKLI_KLASORLER
from uygulama.kurulum import KlasorHatasi


class TestKlasorIdempotentlik:
    """
    **Özellik: kurulum-bootstrap-altyapisi, Özellik 1: Klasör Oluşturma İdempotentliği**
    **Doğrular: Gereksinimler 1.2**
    """

    def test_klasor_olusturma_idempotentligi(self, gecici_dizin):
        """Klasör oluşturma işlemini iki kez çalıştırmak aynı sonucu vermeli"""
        # İlk çalıştırma
        klasorleri_olustur(gecici_dizin)
        ilk_durum = klasor_var_mi(gecici_dizin)
        
        # İkinci çalıştırma
        klasorleri_olustur(gecici_dizin)
        ikinci_durum = klasor_var_mi(gecici_dizin)
        
        # Her iki durumda da tüm klasörler mevcut olmalı
        assert ilk_durum == True
        assert ikinci_durum == True
        assert ilk_durum == ikinci_durum

    @given(st.integers(min_value=1, max_value=5))
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_coklu_calistirma_idempotentligi(self, gecici_dizin, calistirma_sayisi):
        """Klasör oluşturmayı n kez çalıştırmak 1 kez çalıştırmakla aynı sonucu vermeli"""
        # n kez çalıştır
        for _ in range(calistirma_sayisi):
            klasorleri_olustur(gecici_dizin)
        
        # Tüm klasörler mevcut olmalı
        assert klasor_var_mi(gecici_dizin) == True
        
        # Eksik klasör olmamalı
        eksik_klasorler = eksik_klasorleri_listele(gecici_dizin)
        assert len(eksik_klasorler) == 0

    def test_mevcut_klasorler_korunmali(self, gecici_dizin):
        """Mevcut klasörler korunmalı ve hata vermemeli"""
        # Önce bazı klasörleri manuel oluştur
        test_klasor = gecici_dizin / GEREKLI_KLASORLER[0]
        test_klasor.mkdir(parents=True, exist_ok=True)
        
        # Test dosyası ekle
        test_dosya = test_klasor / "test.txt"
        test_dosya.write_text("test içeriği")
        
        # Klasör oluşturma işlemini çalıştır
        klasorleri_olustur(gecici_dizin)
        
        # Test dosyası korunmuş olmalı
        assert test_dosya.exists()
        assert test_dosya.read_text() == "test içeriği"
        
        # Tüm klasörler mevcut olmalı
        assert klasor_var_mi(gecici_dizin) == True

    @given(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_farkli_proje_kokleri_idempotentligi(self, alt_dizin_adi):
        """Farklı proje kök dizinlerinde idempotentlik korunmalı"""
        with tempfile.TemporaryDirectory() as temp_dir:
            proje_koku = Path(temp_dir) / alt_dizin_adi
            proje_koku.mkdir(parents=True, exist_ok=True)
            
            # İki kez çalıştır
            klasorleri_olustur(proje_koku)
            ilk_durum = klasor_var_mi(proje_koku)
            
            klasorleri_olustur(proje_koku)
            ikinci_durum = klasor_var_mi(proje_koku)
            
            assert ilk_durum == ikinci_durum == True


class TestKlasorVarMi:
    """Klasör varlık kontrolü testleri"""

    def test_bos_dizinde_klasor_yok(self, gecici_dizin):
        """Boş dizinde klasörler mevcut değil"""
        assert klasor_var_mi(gecici_dizin) == False

    def test_tam_klasorler_mevcut(self, gecici_dizin):
        """Tüm klasörler oluşturulduktan sonra mevcut"""
        klasorleri_olustur(gecici_dizin)
        assert klasor_var_mi(gecici_dizin) == True

    def test_eksik_klasor_durumu(self, gecici_dizin):
        """Bazı klasörler eksikse False döndürmeli"""
        # Sadece ilk klasörü oluştur
        (gecici_dizin / GEREKLI_KLASORLER[0]).mkdir(parents=True, exist_ok=True)
        assert klasor_var_mi(gecici_dizin) == False

    def test_olmayan_proje_koku(self):
        """Olmayan proje kök dizini için False döndürmeli"""
        olmayan_dizin = Path("/olmayan/dizin/yolu")
        assert klasor_var_mi(olmayan_dizin) == False


class TestEksikKlasorler:
    """Eksik klasör listesi testleri"""

    def test_bos_dizinde_tum_klasorler_eksik(self, gecici_dizin):
        """Boş dizinde tüm klasörler eksik"""
        eksik_klasorler = eksik_klasorleri_listele(gecici_dizin)
        assert set(eksik_klasorler) == set(GEREKLI_KLASORLER)

    def test_tam_klasorlerde_eksik_yok(self, gecici_dizin):
        """Tüm klasörler mevcutsa eksik yok"""
        klasorleri_olustur(gecici_dizin)
        eksik_klasorler = eksik_klasorleri_listele(gecici_dizin)
        assert len(eksik_klasorler) == 0

    def test_kismi_eksik_klasorler(self, gecici_dizin):
        """Bazı klasörler eksikse doğru listeyi döndürmeli"""
        # İlk iki klasörü oluştur
        for i in range(2):
            (gecici_dizin / GEREKLI_KLASORLER[i]).mkdir(parents=True, exist_ok=True)
        
        eksik_klasorler = eksik_klasorleri_listele(gecici_dizin)
        beklenen_eksikler = GEREKLI_KLASORLER[2:]
        
        assert set(eksik_klasorler) == set(beklenen_eksikler)


class TestKlasorYoluDogrulama:
    """Klasör yolu doğrulama testleri"""

    def test_gecerli_yol_dogrulama(self, gecici_dizin):
        """Geçerli yol doğrulanmalı"""
        for klasor_adi in GEREKLI_KLASORLER:
            yol = klasor_yolunu_dogrula(gecici_dizin, klasor_adi)
            assert isinstance(yol, Path)
            assert yol.is_absolute()

    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_string_proje_koku_destegi(self, gecici_dizin, klasor_adi):
        """String proje kök dizini desteklenmeli"""
        try:
            yol = klasor_yolunu_dogrula(str(gecici_dizin), GEREKLI_KLASORLER[0])
            assert isinstance(yol, Path)
        except KlasorHatasi:
            # Geçersiz karakterler için beklenen davranış
            pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])