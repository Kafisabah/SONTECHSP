# Version: 1.0.0
# Last Update: 2024-12-18
# Module: tests.test_ekran_gecis_erisilebilirligi_property
# Description: Ekran geçiş erişilebilirliği property-based testi
# Changelog:
# - İlk sürüm oluşturuldu

import pytest
from hypothesis import given, strategies as st, settings
import sys
import os
from unittest.mock import patch, MagicMock

# Test edilecek modülü import et
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestEkranGecisErisilebilirligi:
    """Özellik 2: Ekran Geçiş Erişilebilirliği - Gereksinim 1.2"""

    def test_ekran_gecis_testi_fonksiyon_varligi(self):
        """
        ekran_gecis_testi fonksiyonunun var olduğunu doğrular
        """
        from uygulama.arayuz.smoke_test_calistir import ekran_gecis_testi

        # Fonksiyonun var olduğunu ve çağrılabilir olduğunu kontrol et
        assert callable(ekran_gecis_testi)

    @given(
        ekran_sayisi=st.integers(min_value=1, max_value=5),
        app_process_events_calls=st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=30, deadline=None)
    def test_ekran_gecis_testi_tutarliligi(self, ekran_sayisi, app_process_events_calls):
        """
        ekran_gecis_testi fonksiyonunun farklı ekran sayılarıyla tutarlı çalıştığını doğrular
        """
        from uygulama.arayuz.smoke_test_calistir import ekran_gecis_testi

        # Mock ekran listesi oluştur
        ekranlar = [f"ekran_{i}" for i in range(ekran_sayisi)]

        # Mock pencere ve app oluştur
        mock_pencere = MagicMock()
        mock_app = MagicMock()

        # Mock pencere ekranları
        mock_pencere.ekranlar.keys.return_value = ekranlar
        mock_pencere.icerik_alani.currentWidget.return_value = MagicMock()  # Widget var

        # Ekran geçiş testi çalıştır
        with patch("time.sleep"):  # Sleep'i hızlandır
            result = ekran_gecis_testi(mock_pencere, mock_app, ekranlar)

        # Sonucun boolean olduğunu doğrula
        assert isinstance(result, bool)
        # Başarılı durumda True dönmeli
        assert result == True

        # Tüm ekranlar için ekran_degistir çağrıldığını doğrula
        assert mock_pencere.ekran_degistir.call_count == ekran_sayisi

        # processEvents çağrıldığını doğrula
        assert mock_app.processEvents.call_count == ekran_sayisi

    @given(ekran_sayisi=st.integers(min_value=1, max_value=3))
    @settings(max_examples=20, deadline=None)
    def test_ekran_gecis_testi_hata_durumu(self, ekran_sayisi):
        """
        ekran_gecis_testi fonksiyonunun hata durumlarında doğru davrandığını doğrular
        """
        from uygulama.arayuz.smoke_test_calistir import ekran_gecis_testi

        # Mock ekran listesi oluştur
        ekranlar = [f"ekran_{i}" for i in range(ekran_sayisi)]

        # Mock pencere ve app oluştur
        mock_pencere = MagicMock()
        mock_app = MagicMock()

        # Mock pencere ekranları
        mock_pencere.ekranlar.keys.return_value = ekranlar
        mock_pencere.icerik_alani.currentWidget.return_value = None  # Widget yok (hata durumu)

        # Ekran geçiş testi çalıştır
        with patch("time.sleep"):  # Sleep'i hızlandır
            result = ekran_gecis_testi(mock_pencere, mock_app, ekranlar)

        # Hata durumunda False dönmeli
        assert isinstance(result, bool)
        assert result == False

    def test_ekran_gecis_testi_exception_handling(self):
        """
        ekran_gecis_testi fonksiyonunun exception durumlarında doğru davrandığını doğrular
        """
        from uygulama.arayuz.smoke_test_calistir import ekran_gecis_testi

        # Mock pencere ve app oluştur
        mock_pencere = MagicMock()
        mock_app = MagicMock()

        # Exception fırlat
        mock_pencere.ekran_degistir.side_effect = Exception("Test hatası")

        # Ekran geçiş testi çalıştır
        result = ekran_gecis_testi(mock_pencere, mock_app, ["test_ekran"])

        # Exception durumunda False dönmeli
        assert isinstance(result, bool)
        assert result == False

    @given(
        ekran_isimleri=st.lists(
            st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"))),
            min_size=1,
            max_size=5,
            unique=True,
        )
    )
    @settings(max_examples=20, deadline=None)
    def test_ekran_gecis_testi_farkli_ekran_isimleri(self, ekran_isimleri):
        """
        ekran_gecis_testi fonksiyonunun farklı ekran isimleriyle çalıştığını doğrular
        """
        from uygulama.arayuz.smoke_test_calistir import ekran_gecis_testi

        # Mock pencere ve app oluştur
        mock_pencere = MagicMock()
        mock_app = MagicMock()

        # Mock pencere ekranları
        mock_pencere.ekranlar.keys.return_value = ekran_isimleri
        mock_pencere.icerik_alani.currentWidget.return_value = MagicMock()

        # Ekran geçiş testi çalıştır
        with patch("time.sleep"):
            result = ekran_gecis_testi(mock_pencere, mock_app, ekran_isimleri)

        # Başarılı olmalı
        assert result == True

        # Her ekran için ekran_degistir çağrıldığını doğrula
        from unittest.mock import call

        expected_calls = [call(ekran) for ekran in ekran_isimleri]
        mock_pencere.ekran_degistir.assert_has_calls(expected_calls, any_order=False)


if __name__ == "__main__":
    pytest.main([__file__])
