# Version: 1.0.0
# Last Update: 2024-12-18
# Module: tests.test_standart_giris_noktasi_tutarliligi_property
# Description: Standart giriş noktası tutarlılığı property-based testi
# Changelog:
# - İlk sürüm oluşturuldu

"""
UI Smoke Test Altyapısı - Standart Giriş Noktası Tutarlılığı Property-Based Testleri

Bu modül smoke test sisteminin standart giriş noktası tutarlılığını test eder.
"""

import pytest
from hypothesis import given, strategies as st, settings
import sys
import os
from unittest.mock import patch, MagicMock

# Test edilecek modülü import et
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestStandartGirisNoktasiTutarliligi:
    """Özellik 12: Standart Giriş Noktası Tutarlılığı - Gereksinim 4.1"""

    def test_standart_giris_noktasi_varligi(self):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 12: Standart Giriş Noktası Tutarlılığı**
        **Doğrular: Gereksinim 4.1**

        Herhangi bir uygulama başlatıldığında, sistem UI başlatma için
        standartlaştırılmış giriş noktası sağlamalıdır
        """
        # Smoke test modülünün import edilebilirliğini kontrol et
        import uygulama.arayuz.smoke_test_calistir as smoke_module

        # Standart giriş noktası fonksiyonlarının varlığını doğrula
        assert hasattr(smoke_module, "main"), "main() fonksiyonu bulunamadı"
        assert callable(smoke_module.main), "main() çağrılabilir değil"

        # __main__ bloğunun varlığını kontrol et
        with open(smoke_module.__file__, "r", encoding="utf-8") as f:
            content = f.read()
            assert 'if __name__ == "__main__":' in content, "__main__ bloğu bulunamadı"
            assert "sys.exit(main())" in content, "sys.exit(main()) çağrısı bulunamadı"

    def test_uygulama_baslatici_standart_giris(self):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 12: Standart Giriş Noktası Tutarlılığı**
        **Doğrular: Gereksinim 4.1, 4.3**

        Herhangi bir giriş noktası çağrıldığında, sistem UI bileşenlerini
        düzgün şekilde başlatmalıdır
        """
        # UygulamaBaslatici modülünü import et
        from uygulama.arayuz.uygulama import UygulamaBaslatici

        # UygulamaBaslatici sınıfının varlığını doğrula
        assert UygulamaBaslatici is not None

        # Gerekli metodların varlığını kontrol et
        baslatici = UygulamaBaslatici()
        assert hasattr(baslatici, "tema_yukle"), "tema_yukle() metodu bulunamadı"
        assert hasattr(baslatici, "kaynaklari_temizle"), "kaynaklari_temizle() metodu bulunamadı"

    @given(
        komut_satiri_argumanlari=st.lists(
            st.sampled_from(["--quiet", "-q", "--version", "-v"]), min_size=0, max_size=2, unique=True
        )
    )
    @settings(max_examples=50, deadline=None)
    def test_main_fonksiyon_standart_giris_tutarliligi(self, komut_satiri_argumanlari):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 12: Standart Giriş Noktası Tutarlılığı**
        **Doğrular: Gereksinim 4.1, 4.2**

        Herhangi bir komut satırı argümanı ile çağrıldığında, main() fonksiyonu
        standart giriş noktası olarak tutarlı çalışmalıdır
        """
        from uygulama.arayuz.smoke_test_calistir import main

        # Version argümanı varsa özel işlem
        if "--version" in komut_satiri_argumanlari or "-v" in komut_satiri_argumanlari:
            with patch("sys.argv", ["smoke_test_calistir.py"] + komut_satiri_argumanlari):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                # Version çıkışı 0 olmalı
                assert exc_info.value.code == 0
        else:
            # Normal argümanlar için mock ile test et
            with patch("sys.argv", ["smoke_test_calistir.py"] + komut_satiri_argumanlari):
                with patch("uygulama.arayuz.smoke_test_calistir.smoke_test_calistir") as mock_smoke:
                    mock_smoke.return_value = 0

                    result = main()

                    # Sonuç integer olmalı
                    assert isinstance(result, int), f"main() {type(result)} döndürdü, int beklendi"

                    # Başarılı durumda 0 dönmeli
                    assert result == 0, f"main() {result} döndürdü, 0 beklendi"

                    # smoke_test_calistir çağrıldığını doğrula
                    mock_smoke.assert_called_once()

    def test_coklu_giris_noktasi_en_uygun_secim(self):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 12: Standart Giriş Noktası Tutarlılığı**
        **Doğrular: Gereksinim 4.4**

        Herhangi bir birden fazla giriş metodu varsa, sistem en uygun standart
        metodu kullanmalıdır
        """
        # Smoke test modülünün standart giriş noktası olduğunu doğrula
        import uygulama.arayuz.smoke_test_calistir as smoke_module

        # main() fonksiyonunun en üst seviye giriş noktası olduğunu doğrula
        assert hasattr(smoke_module, "main")
        assert hasattr(smoke_module, "smoke_test_calistir")

        # main() fonksiyonu smoke_test_calistir() fonksiyonunu çağırmalı
        import inspect

        main_source = inspect.getsource(smoke_module.main)
        assert "smoke_test_calistir" in main_source, "main() smoke_test_calistir() çağırmıyor"

    @given(hata_kodu=st.integers(min_value=1, max_value=255))
    @settings(max_examples=30, deadline=None)
    def test_standart_giris_hata_yonetimi(self, hata_kodu):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 12: Standart Giriş Noktası Tutarlılığı**
        **Doğrular: Gereksinim 4.1, 4.3**

        Herhangi bir hata durumunda, standart giriş noktası uygun hata kodu döndürmelidir
        """
        from uygulama.arayuz.smoke_test_calistir import main

        with patch("sys.argv", ["smoke_test_calistir.py"]):
            with patch("uygulama.arayuz.smoke_test_calistir.smoke_test_calistir") as mock_smoke:
                # Hata kodu döndür
                mock_smoke.return_value = hata_kodu

                result = main()

                # Sonuç hata kodu ile eşleşmeli
                assert result == hata_kodu, f"main() {result} döndürdü, {hata_kodu} beklendi"

    def test_standart_giris_keyboard_interrupt(self):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 12: Standart Giriş Noktası Tutarlılığı**
        **Doğrular: Gereksinim 4.1, 4.3**

        Herhangi bir KeyboardInterrupt durumunda, standart giriş noktası
        düzgün şekilde sonlanmalıdır
        """
        from uygulama.arayuz.smoke_test_calistir import main

        with patch("sys.argv", ["smoke_test_calistir.py"]):
            with patch("uygulama.arayuz.smoke_test_calistir.smoke_test_calistir") as mock_smoke:
                # KeyboardInterrupt fırlat
                mock_smoke.side_effect = KeyboardInterrupt()

                result = main()

                # KeyboardInterrupt için standart çıkış kodu 130
                assert result == 130, f"main() {result} döndürdü, 130 beklendi"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
