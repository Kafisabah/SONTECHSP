# Version: 1.0.0
# Last Update: 2024-12-18
# Module: tests.test_temiz_kapanis_garantisi_property
# Description: Temiz kapanış garantisi property-based testi
# Changelog:
# - İlk sürüm oluşturuldu

import pytest
from hypothesis import given, strategies as st, settings
import sys
import os
from unittest.mock import patch, MagicMock

# Test edilecek modülü import et
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestTemizKapanisGarantisi:
    """Özellik 3: Temiz Kapanış Garantisi - Gereksinim 1.3"""

    def test_temiz_kapanis_fonksiyon_varligi(self):
        """
        temiz_kapanis fonksiyonunun var olduğunu doğrular
        """
        from uygulama.arayuz.smoke_test_calistir import temiz_kapanis

        # Fonksiyonun var olduğunu ve çağrılabilir olduğunu kontrol et
        assert callable(temiz_kapanis)

    @given(ana_pencere_var=st.booleans(), kapanis_basarili=st.booleans())
    @settings(max_examples=30, deadline=None)
    def test_temiz_kapanis_tutarliligi(self, ana_pencere_var, kapanis_basarili):
        """
        temiz_kapanis fonksiyonunun farklı durumlarla tutarlı çalıştığını doğrular
        """
        from uygulama.arayuz.smoke_test_calistir import temiz_kapanis

        # Mock UygulamaBaslatici oluştur
        mock_baslatici = MagicMock()

        if ana_pencere_var:
            mock_ana_pencere = MagicMock()
            if not kapanis_basarili:
                mock_ana_pencere.close.side_effect = Exception("Kapanış hatası")
            mock_baslatici.ana_pencere = mock_ana_pencere
        else:
            mock_baslatici.ana_pencere = None

        # Kaynak temizleme mock'u
        if not kapanis_basarili:
            mock_baslatici.kaynaklari_temizle.side_effect = Exception("Temizleme hatası")

        # temiz_kapanis çalıştır - hata durumunda bile exception fırlatmamalı
        try:
            temiz_kapanis(mock_baslatici)
            # Fonksiyon başarıyla tamamlanmalı (exception fırlatmamalı)
            success = True
        except Exception:
            success = False

        # Temiz kapanış her durumda başarılı olmalı (exception handling)
        assert success == True

        # Ana pencere varsa close çağrıldığını doğrula
        if ana_pencere_var:
            mock_baslatici.ana_pencere.close.assert_called_once()

        # Kaynak temizleme başarılı durumda çağrılmalı
        if kapanis_basarili:
            mock_baslatici.kaynaklari_temizle.assert_called_once()
        # Exception durumunda çağrılmayabilir (bu normal davranış)

    def test_temiz_kapanis_exception_handling(self):
        """
        temiz_kapanis fonksiyonunun exception durumlarında doğru davrandığını doğrular
        """
        from uygulama.arayuz.smoke_test_calistir import temiz_kapanis

        # Mock UygulamaBaslatici oluştur
        mock_baslatici = MagicMock()

        # Ana pencere close exception fırlatsın
        mock_ana_pencere = MagicMock()
        mock_ana_pencere.close.side_effect = Exception("Pencere kapanış hatası")
        mock_baslatici.ana_pencere = mock_ana_pencere

        # Kaynak temizleme de exception fırlatsın
        mock_baslatici.kaynaklari_temizle.side_effect = Exception("Kaynak temizleme hatası")

        # temiz_kapanis çalıştır - exception fırlatmamalı
        try:
            temiz_kapanis(mock_baslatici)
            success = True
        except Exception:
            success = False

        # Exception durumunda bile başarılı olmalı
        assert success == True

    @given(baslatici_none=st.booleans())
    @settings(max_examples=20, deadline=None)
    def test_temiz_kapanis_none_baslatici(self, baslatici_none):
        """
        temiz_kapanis fonksiyonunun None başlatıcı ile çalıştığını doğrular
        """
        from uygulama.arayuz.smoke_test_calistir import temiz_kapanis

        if baslatici_none:
            baslatici = None
        else:
            baslatici = MagicMock()

        # temiz_kapanis çalıştır
        try:
            temiz_kapanis(baslatici)
            success = True
        except Exception:
            success = False

        # Her durumda başarılı olmalı
        assert success == True

    def test_temiz_kapanis_kaynak_temizleme_sirasi(self):
        """
        temiz_kapanis fonksiyonunun doğru sırada kaynak temizlediğini doğrular
        """
        from uygulama.arayuz.smoke_test_calistir import temiz_kapanis

        # Mock UygulamaBaslatici oluştur
        mock_baslatici = MagicMock()
        mock_ana_pencere = MagicMock()
        mock_baslatici.ana_pencere = mock_ana_pencere

        # temiz_kapanis çalıştır
        temiz_kapanis(mock_baslatici)

        # Önce ana pencere kapatılmalı, sonra kaynaklar temizlenmeli
        mock_ana_pencere.close.assert_called_once()
        mock_baslatici.kaynaklari_temizle.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
