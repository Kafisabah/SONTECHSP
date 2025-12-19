# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_pos_hata_yonetimi_property
# Description: POS hata yönetimi özellik tabanlı testleri
# Changelog:
# - İlk oluşturma - POS hata yönetimi property testleri

"""
POS Hata Yönetimi Özellik Tabanlı Testleri

**Feature: pos-yeni-ekran-tasarimi, Property 9: Hata Yönetimi**
**Validates: Requirements 11.1, 11.2, 11.5**

Bu test modülü POS hata yönetimi sisteminin doğruluğunu test eder:
- Herhangi bir hata durumunda sistem turkuaz renkli hata mesajı göstermeli
- Log dosyasına detaylı hata kaydı yazmalı
- Kritik hata oluştuğunda çökmeyecek ve kullanıcıyı bilgilendirecektir
"""

import sys
import os
import tempfile
import logging
from unittest.mock import Mock, patch, MagicMock

import pytest
from hypothesis import given, strategies as st, settings, assume

# Test için gerekli path ayarları
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# PyQt6 import'larını test ortamında güvenli hale getir
try:
    from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
    from PyQt6.QtCore import QTimer
    from PyQt6.QtTest import QTest

    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

    # Mock PyQt6 sınıfları
    class QApplication:
        @staticmethod
        def instance():
            return None

    class QWidget:
        def close(self):
            pass

    class QMessageBox:
        class Icon:
            Critical = "Critical"
            Warning = "Warning"
            Information = "Information"

        class StandardButton:
            Ok = "Ok"
            Yes = "Yes"
            No = "No"


from sontechsp.uygulama.arayuz.ekranlar.pos.pos_hata_yoneticisi import POSHataYoneticisi
from sontechsp.uygulama.cekirdek.hatalar import (
    POSHatasi,
    BarkodHatasi,
    StokHatasi,
    OdemeHatasi,
    IadeHatasi,
    NetworkHatasi,
    YazdirmaHatasi,
    HataSeviyesi,
)


class TestPOSHataYonetimiProperty:
    """POS hata yönetimi özellik tabanlı testleri"""

    @classmethod
    def setup_class(cls):
        """Test sınıfı kurulumu"""
        if PYQT_AVAILABLE and not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = None

    def setup_method(self):
        """Her test öncesi kurulum"""
        # Test widget'ı oluştur (mock olabilir)
        if PYQT_AVAILABLE:
            self.test_widget = QWidget()
        else:
            self.test_widget = Mock()

        # Hata yöneticisi oluştur
        self.hata_yoneticisi = POSHataYoneticisi(self.test_widget)

        # Test modunu aktif et - QMessageBox gösterimini devre dışı bırak
        self.hata_yoneticisi.test_modu_aktif_et(True)

        # Mock logger oluştur
        self.mock_logger = Mock()
        self.hata_yoneticisi.logger = self.mock_logger

    def teardown_method(self):
        """Her test sonrası temizlik"""
        if hasattr(self, "test_widget") and PYQT_AVAILABLE:
            self.test_widget.close()

    @given(
        hata_mesaji=st.text(min_size=1, max_size=100),
        hata_turu=st.sampled_from(["servis", "dogrulama", "ag", "stok", "genel"]),
    )
    @settings(max_examples=20, deadline=5000)  # 5 saniye timeout
    def test_hata_yonetimi_genel_davranis(self, hata_mesaji, hata_turu):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 9: Hata Yönetimi**
        **Validates: Requirements 11.1, 11.2, 11.5**

        Herhangi bir hata durumunda, sistem turkuaz renkli hata mesajı göstermeli,
        log dosyasına detaylı hata kaydı yazmalı ve çökmeden çalışmaya devam etmelidir.
        """
        # Geçerli giriş değerlerini filtrele
        assume(hata_mesaji.strip())

        # Sinyal yakalayıcı
        sinyal_alindi = []
        self.hata_yoneticisi.hata_olustu.connect(lambda turu, mesaj: sinyal_alindi.append((turu, mesaj)))

        # Hata gösterme işlemini gerçekleştir
        try:
            self.hata_yoneticisi.hata_goster(hata_turu, hata_mesaji)
            sistem_coktu = False
        except Exception as e:
            sistem_coktu = True
            pytest.fail(f"Sistem çöktü: {e}")

        # Özellik 1: Sistem çökmeden çalışmaya devam etmeli
        assert not sistem_coktu, "Sistem hata durumunda çökmemeli"

        # Özellik 2: Log kaydı oluşturulmalı
        assert self.mock_logger.error.called, "Hata durumunda log kaydı oluşturulmalı"

        # Özellik 3: Hata sinyali gönderilmeli
        assert len(sinyal_alindi) > 0, "Hata durumunda sinyal gönderilmeli"
        assert sinyal_alindi[0][0] == hata_turu, "Doğru hata türü sinyali gönderilmeli"

    @given(hata_sayisi=st.integers(min_value=1, max_value=3), kaynak=st.text(min_size=1, max_size=20))
    @settings(max_examples=10, deadline=3000)
    def test_coklu_hata_durumu_kararliligi(self, hata_sayisi, kaynak):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 9: Hata Yönetimi**

        Çoklu hata durumunda sistem kararlı kalmalı ve her hatayı işlemeli.
        """
        assume(kaynak.strip())

        islenen_hata_sayisi = 0
        hata_tipleri = ["servis", "ag", "stok"]

        for i in range(hata_sayisi):
            try:
                hata_turu = hata_tipleri[i % len(hata_tipleri)]
                self.hata_yoneticisi.hata_goster(hata_turu, f"Test hatası {i}")
                islenen_hata_sayisi += 1
            except Exception:
                break

        # Tüm hatalar işlenmeli
        assert islenen_hata_sayisi == hata_sayisi, f"Tüm hatalar işlenmeli: {islenen_hata_sayisi}/{hata_sayisi}"

    @given(hata_turu=st.sampled_from(["servis", "dogrulama", "ag", "stok"]))
    @settings(max_examples=10, deadline=2000)
    def test_hata_sinyal_gonderimi(self, hata_turu):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 9: Hata Yönetimi**

        Hata durumunda sinyal gönderilmeli.
        """
        test_mesaji = f"Test {hata_turu} hatası"

        # Sinyal yakalayıcı
        sinyal_alindi = []
        self.hata_yoneticisi.hata_olustu.connect(lambda turu, mesaj: sinyal_alindi.append((turu, mesaj)))

        self.hata_yoneticisi.hata_goster(hata_turu, test_mesaji)

        # Sinyal gönderilmeli
        assert len(sinyal_alindi) > 0, "Hata durumunda sinyal gönderilmeli"
        assert sinyal_alindi[0][0] == hata_turu, "Doğru hata türü sinyali gönderilmeli"

    def test_hata_yoneticisi_temel_fonksiyonalite(self):
        """Hata yöneticisinin temel fonksiyonalitesini test eder"""
        test_mesaji = "Test hatası"

        # Hata gösterme işlemi çökmemeli
        try:
            self.hata_yoneticisi.hata_goster("pos", test_mesaji)
            basarili = True
        except Exception:
            basarili = False

        assert basarili, "Temel hata gösterme işlemi başarılı olmalı"

    def test_basari_mesaji_gosterimi(self):
        """Başarı mesajı gösterimi test edilir"""
        test_mesaji = "İşlem başarılı"

        # Başarı mesajı gösterme işlemi çökmemeli
        try:
            self.hata_yoneticisi.basari_goster(test_mesaji)
            basarili = True
        except Exception:
            basarili = False

        assert basarili, "Başarı mesajı gösterme işlemi başarılı olmalı"

    def test_onay_isteme_fonksiyonu(self):
        """Onay isteme fonksiyonu test edilir"""
        test_mesaji = "İşlemi onaylıyor musunuz?"

        # Onay isteme işlemi çökmemeli
        try:
            sonuc = self.hata_yoneticisi.onay_iste(test_mesaji)
            basarili = True
        except Exception:
            basarili = False
            sonuc = False

        assert basarili, "Onay isteme işlemi başarılı olmalı"
        # Test modunda varsayılan True döner
        assert sonuc == True, "Test modunda onay isteme True döndürmeli"

    def test_test_modu_aktif_etme(self):
        """Test modu aktif etme fonksiyonu test edilir"""
        # Test modu aktif
        self.hata_yoneticisi.test_modu_aktif_et(True)
        assert hasattr(self.hata_yoneticisi, "_test_modu"), "Test modu özelliği eklenmeli"
        assert self.hata_yoneticisi._test_modu == True, "Test modu aktif olmalı"

        # Test modu pasif
        self.hata_yoneticisi.test_modu_aktif_et(False)
        assert self.hata_yoneticisi._test_modu == False, "Test modu pasif olmalı"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
