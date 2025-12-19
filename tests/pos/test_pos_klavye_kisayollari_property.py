# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_pos_klavye_kisayollari_property
# Description: POS yeni ekran klavye kısayolları özellik testleri
# Changelog:
# - İlk oluşturma - POS yeni ekran klavye kısayolları özellik testleri

"""
POS Yeni Ekran Klavye Kısayolları Özellik Testleri

**Feature: pos-yeni-ekran-tasarimi, Property 6: Klavye Kısayolları**

Herhangi bir klavye kısayolu basımında (F2: barkod odağı, F4-F7: ödeme türleri,
F8-F10: işlem kısayolları, ESC: iptal, +/-: adet değiştir), sistem ilgili işlemi gerçekleştirmelidir.

Doğrular: Gereksinim 2.3, 8.5
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeyEvent
import sys
from unittest.mock import Mock, patch

from sontechsp.uygulama.arayuz.ekranlar.pos.pos_satis_ekrani import POSSatisEkrani


class TestPOSKlavyeKisayollariProperty:
    """POS Yeni Ekran Klavye Kısayolları Özellik Testleri"""

    @pytest.fixture(autouse=True)
    def setup_qt(self):
        """Qt uygulamasını kurar"""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        yield
        # Test sonrası temizlik
        QTimer.singleShot(0, self.app.quit)

    def _pos_ekrani_olustur(self):
        """POS satış ekranı oluşturur"""
        with patch("sontechsp.uygulama.arayuz.ekranlar.pos.pos_satis_ekrani.POSHataYoneticisi"):
            ekran = POSSatisEkrani()
            return ekran

    @given(barkod_odak_tus=st.just(Qt.Key.Key_F2))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_barkod_odak_kisayolu(self, barkod_odak_tus):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 6: Klavye Kısayolları**
        **Validates: Requirements 2.3, 8.5**

        Özellik: F2 tuşuna basıldığında barkod alanına odak verilmeli
        """
        pos_ekrani = self._pos_ekrani_olustur()

        # Mock barkod odağı verme fonksiyonu
        pos_ekrani.ust_bar.barkod_odagini_ver = Mock()

        # F2 klavye olayı oluştur
        event = QKeyEvent(QKeyEvent.Type.KeyPress, barkod_odak_tus, Qt.KeyboardModifier.NoModifier)

        # Olayı işle
        pos_ekrani.keyPressEvent(event)

        # Barkod odağı verilmeli
        pos_ekrani.ust_bar.barkod_odagini_ver.assert_called_once()

    @given(
        odeme_turu_tus=st.sampled_from(
            [Qt.Key.Key_F4, Qt.Key.Key_F5, Qt.Key.Key_F6, Qt.Key.Key_F7]  # Nakit  # Kart  # Parçalı  # Açık hesap
        )
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_odeme_turu_kisayollari(self, odeme_turu_tus):
        """
        Özellik: F4-F7 tuşlarına basıldığında ilgili ödeme türü işlemi başlatılmalı
        """
        pos_ekrani = self._pos_ekrani_olustur()

        # Mock ödeme fonksiyonları
        pos_ekrani.nakit_odeme = Mock()
        pos_ekrani.kart_odeme = Mock()
        pos_ekrani.parcali_odeme = Mock()
        pos_ekrani.acik_hesap_odeme = Mock()

        # Klavye olayı oluştur
        event = QKeyEvent(QKeyEvent.Type.KeyPress, odeme_turu_tus, Qt.KeyboardModifier.NoModifier)

        # Olayı işle
        pos_ekrani.keyPressEvent(event)

        # İlgili ödeme fonksiyonu çağrılmalı
        if odeme_turu_tus == Qt.Key.Key_F4:
            pos_ekrani.nakit_odeme.assert_called_once()
        elif odeme_turu_tus == Qt.Key.Key_F5:
            pos_ekrani.kart_odeme.assert_called_once()
        elif odeme_turu_tus == Qt.Key.Key_F6:
            pos_ekrani.parcali_odeme.assert_called_once()
        elif odeme_turu_tus == Qt.Key.Key_F7:
            pos_ekrani.acik_hesap_odeme.assert_called_once()

    @given(islem_tus=st.sampled_from([Qt.Key.Key_F8, Qt.Key.Key_F9, Qt.Key.Key_F10]))  # Beklet  # Bekleyenler  # İade
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_islem_kisayollari(self, islem_tus):
        """
        Özellik: F8-F10 tuşlarına basıldığında ilgili işlem başlatılmalı
        """
        pos_ekrani = self._pos_ekrani_olustur()

        # Mock işlem fonksiyonları
        pos_ekrani.sepet_beklet = Mock()
        pos_ekrani.bekleyenler_goster = Mock()
        pos_ekrani.iade_islemi = Mock()

        # Klavye olayı oluştur
        event = QKeyEvent(QKeyEvent.Type.KeyPress, islem_tus, Qt.KeyboardModifier.NoModifier)

        # Olayı işle
        pos_ekrani.keyPressEvent(event)

        # İlgili işlem fonksiyonu çağrılmalı
        if islem_tus == Qt.Key.Key_F8:
            pos_ekrani.sepet_beklet.assert_called_once()
        elif islem_tus == Qt.Key.Key_F9:
            pos_ekrani.bekleyenler_goster.assert_called_once()
        elif islem_tus == Qt.Key.Key_F10:
            pos_ekrani.iade_islemi.assert_called_once()

    @given(iptal_tus=st.just(Qt.Key.Key_Escape))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_iptal_kisayolu(self, iptal_tus):
        """
        Özellik: ESC tuşuna basıldığında işlem iptal edilmeli
        """
        pos_ekrani = self._pos_ekrani_olustur()

        # Mock iptal fonksiyonu
        pos_ekrani.islem_iptal = Mock()

        # ESC klavye olayı oluştur
        event = QKeyEvent(QKeyEvent.Type.KeyPress, iptal_tus, Qt.KeyboardModifier.NoModifier)

        # Olayı işle
        pos_ekrani.keyPressEvent(event)

        # İptal fonksiyonu çağrılmalı
        pos_ekrani.islem_iptal.assert_called_once()

    @given(sil_tus=st.just(Qt.Key.Key_Delete))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_satir_silme_kisayolu(self, sil_tus):
        """
        Özellik: DEL tuşuna basıldığında seçili ürün silinmeli
        """
        pos_ekrani = self._pos_ekrani_olustur()

        # Mock silme fonksiyonu
        pos_ekrani.secili_urunu_sil = Mock()

        # DEL klavye olayı oluştur
        event = QKeyEvent(QKeyEvent.Type.KeyPress, sil_tus, Qt.KeyboardModifier.NoModifier)

        # Olayı işle
        pos_ekrani.keyPressEvent(event)

        # Silme fonksiyonu çağrılmalı
        pos_ekrani.secili_urunu_sil.assert_called_once()

    @given(
        gecersiz_tus=st.sampled_from(
            [
                Qt.Key.Key_A,
                Qt.Key.Key_B,
                Qt.Key.Key_C,
                Qt.Key.Key_1,
                Qt.Key.Key_2,
                Qt.Key.Key_3,
                Qt.Key.Key_Space,
                Qt.Key.Key_Enter,
                Qt.Key.Key_Tab,
            ]
        )
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_gecersiz_kisayollarin_islenmemesi(self, gecersiz_tus):
        """
        Özellik: Tanımsız klavye kısayolları işlenmemeli, parent'a iletilmeli
        """
        pos_ekrani = self._pos_ekrani_olustur()

        # Parent keyPressEvent'i mock'la
        with patch.object(QWidget, "keyPressEvent") as mock_parent:
            # Geçersiz tuş olayı oluştur
            event = QKeyEvent(QKeyEvent.Type.KeyPress, gecersiz_tus, Qt.KeyboardModifier.NoModifier)

            # Olayı işle
            pos_ekrani.keyPressEvent(event)

            # Parent'ın keyPressEvent'i çağrılmalı
            mock_parent.assert_called_once_with(event)

    def test_tum_kisayollarin_tanimli_olmasi(self):
        """
        Özellik: Tüm gerekli klavye kısayolları tanımlı olmalı
        """
        pos_ekrani = self._pos_ekrani_olustur()

        # Gerekli kısayollar
        gerekli_kisayollar = [
            Qt.Key.Key_F2,  # Barkod odağı
            Qt.Key.Key_F4,  # Nakit ödeme
            Qt.Key.Key_F5,  # Kart ödeme
            Qt.Key.Key_F6,  # Parçalı ödeme
            Qt.Key.Key_F7,  # Açık hesap
            Qt.Key.Key_F8,  # Beklet
            Qt.Key.Key_F9,  # Bekleyenler
            Qt.Key.Key_F10,  # İade
            Qt.Key.Key_Escape,  # İptal
            Qt.Key.Key_Delete,  # Satır sil
        ]

        # Her kısayol için test et
        for tus in gerekli_kisayollar:
            # Mock fonksiyonları hazırla
            pos_ekrani.ust_bar.barkod_odagini_ver = Mock()
            pos_ekrani.nakit_odeme = Mock()
            pos_ekrani.kart_odeme = Mock()
            pos_ekrani.parcali_odeme = Mock()
            pos_ekrani.acik_hesap_odeme = Mock()
            pos_ekrani.sepet_beklet = Mock()
            pos_ekrani.bekleyenler_goster = Mock()
            pos_ekrani.iade_islemi = Mock()
            pos_ekrani.islem_iptal = Mock()
            pos_ekrani.secili_urunu_sil = Mock()

            # Klavye olayı oluştur
            event = QKeyEvent(QKeyEvent.Type.KeyPress, tus, Qt.KeyboardModifier.NoModifier)

            # Olayı işle - hata vermemeli
            try:
                pos_ekrani.keyPressEvent(event)
                # Başarılı işlem
                assert True, f"Kısayol {tus.name} başarıyla işlendi"
            except Exception as e:
                pytest.fail(f"Kısayol {tus.name} işlenirken hata: {e}")

    def test_klavye_olayi_yakalama_mekanizmasi(self):
        """
        Özellik: POS ekranı klavye olaylarını yakalayabilmeli
        """
        pos_ekrani = self._pos_ekrani_olustur()

        # keyPressEvent metodunun var olduğunu kontrol et
        assert hasattr(pos_ekrani, "keyPressEvent"), "keyPressEvent metodu tanımlı değil"
        assert callable(getattr(pos_ekrani, "keyPressEvent")), "keyPressEvent çağrılabilir değil"

        # Test olayı oluştur
        test_event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_F2, Qt.KeyboardModifier.NoModifier)

        # Metod çağrılabilmeli
        try:
            pos_ekrani.keyPressEvent(test_event)
            assert True, "keyPressEvent başarıyla çağrıldı"
        except Exception as e:
            pytest.fail(f"keyPressEvent çağrılırken hata: {e}")

    @given(
        modifier_tus=st.sampled_from(
            [Qt.KeyboardModifier.ControlModifier, Qt.KeyboardModifier.AltModifier, Qt.KeyboardModifier.ShiftModifier]
        ),
        ana_tus=st.sampled_from([Qt.Key.Key_F4, Qt.Key.Key_F5, Qt.Key.Key_F6]),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_modifier_tuslu_kisayollarin_islenmemesi(self, modifier_tus, ana_tus):
        """
        Özellik: Modifier tuşlu kombinasyonlar (Ctrl+F4 gibi) işlenmemeli, parent'a iletilmeli
        """
        pos_ekrani = self._pos_ekrani_olustur()

        # Parent keyPressEvent'i mock'la
        with patch.object(QWidget, "keyPressEvent") as mock_parent:
            # Modifier'lı olay oluştur
            event = QKeyEvent(QKeyEvent.Type.KeyPress, ana_tus, modifier_tus)

            # Olayı işle
            pos_ekrani.keyPressEvent(event)

            # Parent'ın keyPressEvent'i çağrılmalı (modifier'lı olaylar işlenmez)
            mock_parent.assert_called_once_with(event)
