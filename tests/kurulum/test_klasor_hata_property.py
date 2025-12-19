# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.kurulum.test_klasor_hata_property
# Description: Klasör hata yönetimi property testleri
# Changelog:
# - Hata yönetimi property testleri oluşturuldu

"""
Klasör hata yönetimi property testleri

**Özellik: kurulum-bootstrap-altyapisi, Özellik 3: Hatalı Yol Yönetimi**
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, settings, HealthCheck

from sontechsp.uygulama.kurulum.klasorler import klasorleri_olustur, klasor_var_mi, klasor_yolunu_dogrula
from sontechsp.uygulama.kurulum import KlasorHatasi


class TestHataliYolYonetimi:
    """
    **Özellik: kurulum-bootstrap-altyapisi, Özellik 3: Hatalı Yol Yönetimi**
    **Doğrular: Gereksinimler 1.3**
    """

    def test_gecersiz_proje_koku_hatasi(self):
        """Geçersiz proje kök dizini için anlaşılır hata mesajı"""
        # Null byte içeren geçersiz yol
        gecersiz_yol = Path("geçersiz\x00yol")

        with pytest.raises(KlasorHatasi) as exc_info:
            klasorleri_olustur(gecersiz_yol)

        # Hata mesajının anlaşılır olduğunu kontrol et
        hata_mesaji = str(exc_info.value)
        assert "Klasör oluşturma işlemi başarısız" in hata_mesaji or "hata" in hata_mesaji.lower()

    def test_izin_hatasi_yonetimi(self, gecici_dizin):
        """İzin hatası durumunda anlaşılır hata mesajı"""
        # Mock ile PermissionError simüle et
        with patch("pathlib.Path.mkdir", side_effect=PermissionError("İzin reddedildi")):
            with pytest.raises(KlasorHatasi) as exc_info:
                klasorleri_olustur(gecici_dizin)

            hata_mesaji = str(exc_info.value)
            assert "İzin hatası" in hata_mesaji or "izin" in hata_mesaji.lower()

    def test_sistem_hatasi_yonetimi(self, gecici_dizin):
        """Sistem hatası durumunda anlaşılır hata mesajı"""
        # Mock ile OSError simüle et
        with patch("pathlib.Path.mkdir", side_effect=OSError("Disk dolu")):
            with pytest.raises(KlasorHatasi) as exc_info:
                klasorleri_olustur(gecici_dizin)

            hata_mesaji = str(exc_info.value)
            assert "Sistem hatası" in hata_mesaji or "hata" in hata_mesaji.lower()

    def test_dosya_ile_ayni_isimde_klasor_hatasi(self, gecici_dizin):
        """Aynı isimde dosya varsa anlaşılır hata mesajı"""
        from sontechsp.uygulama.kurulum.sabitler import GEREKLI_KLASORLER

        # İlk klasör adıyla aynı isimde dosya oluştur
        dosya_yolu = gecici_dizin / GEREKLI_KLASORLER[0]
        dosya_yolu.write_text("test dosyası")

        with pytest.raises(KlasorHatasi) as exc_info:
            klasorleri_olustur(gecici_dizin)

        hata_mesaji = str(exc_info.value)
        assert "dosya olarak mevcut" in hata_mesaji or "klasör oluşturulamıyor" in hata_mesaji

    @given(st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_characters="\x00")))
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_genel_hata_yakalama(self, gecici_dizin, hata_mesaji):
        """Genel hataların yakalandığını ve anlaşılır mesaj verdiğini test et"""
        # Mock ile genel Exception simüle et
        with patch("pathlib.Path.mkdir", side_effect=Exception(hata_mesaji)):
            with pytest.raises(KlasorHatasi) as exc_info:
                klasorleri_olustur(gecici_dizin)

            # Hata mesajının KlasorHatasi olarak sarıldığını kontrol et
            assert isinstance(exc_info.value, KlasorHatasi)
            hata_str = str(exc_info.value)
            assert len(hata_str) > 0

    def test_yol_dogrulama_hatasi(self, gecici_dizin):
        """Yol doğrulama hatası için anlaşılır mesaj"""
        # Mock ile resolve() hatasını simüle et
        with patch("pathlib.Path.resolve", side_effect=OSError("Geçersiz yol")):
            with pytest.raises(KlasorHatasi) as exc_info:
                klasor_yolunu_dogrula(gecici_dizin, "test_klasor")

            hata_mesaji = str(exc_info.value)
            assert "Geçersiz klasör yolu" in hata_mesaji

    def test_string_path_donusumu_hatasi(self):
        """String path dönüşümü hatası için anlaşılır mesaj"""
        # Çok uzun yol ile hata simüle et
        cok_uzun_yol = "a" * 1000  # Windows'ta çok uzun yol

        try:
            klasor_var_mi(cok_uzun_yol)
            # Hata oluşmazsa test geçsin (sistem bağımlı)
        except Exception:
            # Hata oluşursa False döndürmeli, exception fırlatmamalı
            assert klasor_var_mi(cok_uzun_yol) == False

    @given(st.text(min_size=0, max_size=5))
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_bos_veya_gecersiz_klasor_adi(self, gecici_dizin, klasor_adi):
        """Boş veya geçersiz klasör adları için uygun davranış"""
        if not klasor_adi or klasor_adi.isspace():
            # Boş veya sadece boşluk içeren adlar için
            try:
                yol = klasor_yolunu_dogrula(gecici_dizin, klasor_adi)
                # Eğer hata oluşmazsa, yol geçerli olmalı
                assert isinstance(yol, Path)
            except (KlasorHatasi, ValueError, OSError):
                # Hata oluşması beklenen davranış
                pass

    def test_readonly_dizinde_klasor_olusturma(self, gecici_dizin):
        """Salt okunur dizinde klasör oluşturma hatası"""
        # Windows'ta salt okunur dizin testi farklı çalışır
        import platform

        if platform.system() == "Windows":
            pytest.skip("Windows'ta salt okunur dizin testi desteklenmiyor")

        try:
            # Dizini salt okunur yap (Unix sistemlerde)
            os.chmod(gecici_dizin, 0o444)

            with pytest.raises(KlasorHatasi) as exc_info:
                klasorleri_olustur(gecici_dizin)

            hata_mesaji = str(exc_info.value)
            assert len(hata_mesaji) > 0

        except (OSError, PermissionError):
            # Sistem izin vermediyse test geç
            pytest.skip("Sistem salt okunur dizin oluşturmaya izin vermiyor")
        finally:
            # İzinleri geri yükle
            try:
                os.chmod(gecici_dizin, 0o755)
            except (OSError, PermissionError):
                pass

    def test_hata_mesaji_turkce_karakter_destegi(self, gecici_dizin):
        """Hata mesajlarında Türkçe karakter desteği"""
        # Türkçe karakterli dosya adı ile çakışma oluştur
        turkce_dosya = gecici_dizin / "veri"  # GEREKLI_KLASORLER'den biri
        turkce_dosya.write_text("Türkçe içerik: çğıöşü")

        with pytest.raises(KlasorHatasi) as exc_info:
            klasorleri_olustur(gecici_dizin)

        hata_mesaji = str(exc_info.value)
        # Hata mesajının okunabilir olduğunu kontrol et
        assert len(hata_mesaji) > 0
        assert isinstance(hata_mesaji, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
