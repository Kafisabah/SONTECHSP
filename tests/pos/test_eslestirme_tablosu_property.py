# Version: 0.1.0
# Last Update: 2024-12-18
# Module: test_eslestirme_tablosu_property
# Description: Eşleştirme tablosu özellik tabanlı testleri
# Changelog:
# - İlk oluşturma - Eşleştirme tablosu property testleri

"""
Eşleştirme Tablosu Özellik Testleri

**Feature: pos-arayuz-entegrasyonu, Property 9: Eşleştirme Tablosu**

**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

Herhangi bir eşleştirme tablosu işleminde, sistem buton-handler-servis ilişkilerini göstermeli,
otomatik güncellemeli ve CSV dışa aktarımını desteklemelidir.
"""

import os
import tempfile
import csv
from datetime import datetime
from typing import Dict, List, Any
from unittest.mock import Mock, patch, MagicMock

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QApplication, QTableWidget, QDialog
from PyQt6.QtTest import QTest

from sontechsp.uygulama.moduller.pos.ui.bilesenler.eslestirme_dialog import EslestirmeDialog


class TestEslestirmeTablosuProperty:
    """Eşleştirme tablosu özellik tabanlı testleri"""

    @pytest.fixture
    def mock_kayitlar(self):
        """Mock eşleştirme kayıtları"""
        return [
            {
                "ekran_adi": "POS Ana Ekran",
                "buton_adi": "EKLE",
                "handler_adi": "barkod_ekle_handler",
                "servis_metodu": "stok_service.urun_bul",
                "kayit_zamani": "2024-12-18T10:30:00Z",
                "cagrilma_sayisi": 5,
            },
            {
                "ekran_adi": "Ödeme Paneli",
                "buton_adi": "NAKİT",
                "handler_adi": "nakit_odeme_handler",
                "servis_metodu": "odeme_service.nakit_isle",
                "kayit_zamani": "2024-12-18T10:31:00Z",
                "cagrilma_sayisi": 3,
            },
            {
                "ekran_adi": "Sepet Tablosu",
                "buton_adi": "SİL",
                "handler_adi": "sepet_satir_sil_handler",
                "servis_metodu": None,  # Servis hazır değil durumu
                "kayit_zamani": "2024-12-18T10:32:00Z",
                "cagrilma_sayisi": 1,
            },
        ]

    @pytest.fixture
    def eslestirme_dialog(self, qtbot, mock_kayitlar):
        """EslestirmeDialog fixture'ı"""
        with patch("sontechsp.uygulama.moduller.pos.ui.bilesenler.eslestirme_dialog.kayitlari_listele") as mock_listele:
            mock_listele.return_value = mock_kayitlar

            dialog = EslestirmeDialog()
            qtbot.addWidget(dialog)

            # Timer'ı durdur test sırasında
            dialog.guncelleme_durdur()

            return dialog

    # Eşleştirme kayıtları için strateji
    eslestirme_kaydi_strategy = st.fixed_dictionaries(
        {
            "ekran_adi": st.text(
                min_size=1,
                max_size=50,
                alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc", "Pd", "Zs")),
            ),
            "buton_adi": st.text(
                min_size=1,
                max_size=30,
                alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc", "Pd", "Zs")),
            ),
            "handler_adi": st.text(
                min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc", "Pd"))
            ),
            "servis_metodu": st.one_of(
                st.none(),
                st.text(
                    min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc", "Pd"))
                ),
            ),
            "kayit_zamani": st.datetimes(min_value=datetime(2024, 1, 1), max_value=datetime(2024, 12, 31)).map(
                lambda dt: dt.isoformat() + "Z"
            ),
            "cagrilma_sayisi": st.integers(min_value=0, max_value=1000),
        }
    )

    @given(kayitlar=st.lists(eslestirme_kaydi_strategy, min_size=0, max_size=20))
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_eslestirme_tablosu_kayit_gosterimi_property(self, qtbot, kayitlar):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 9: Eşleştirme Tablosu**

        **Validates: Requirements 8.1, 8.2**

        Herhangi bir eşleştirme tablosu açılışında, sistem tüm kayıtları doğru formatta göstermelidir.
        """
        with patch("sontechsp.uygulama.moduller.pos.ui.bilesenler.eslestirme_dialog.kayitlari_listele") as mock_listele:
            mock_listele.return_value = kayitlar

            dialog = EslestirmeDialog()
            qtbot.addWidget(dialog)
            dialog.guncelleme_durdur()

            # Tabloyu manuel güncelle
            dialog._tabloyu_guncelle()

            # Tablo satır sayısı kayıt sayısına eşit olmalı
            assert dialog.tablo.rowCount() == len(kayitlar)

            # Kayıt sayısı etiketi doğru olmalı
            beklenen_metin = f"Kayıt: {len(kayitlar)}"
            assert dialog.kayit_sayisi_etiketi.text() == beklenen_metin

            # Her kayıt için tablo verilerini kontrol et
            for satir, kayit in enumerate(kayitlar):
                # Ekran adı
                ekran_item = dialog.tablo.item(satir, 0)
                assert ekran_item is not None
                assert ekran_item.text() == kayit["ekran_adi"]

                # Buton adı
                buton_item = dialog.tablo.item(satir, 1)
                assert buton_item is not None
                assert buton_item.text() == kayit["buton_adi"]

                # Handler adı
                handler_item = dialog.tablo.item(satir, 2)
                assert handler_item is not None
                assert handler_item.text() == kayit["handler_adi"]

                # Servis metodu (None ise "Servis hazır değil" göstermeli)
                servis_item = dialog.tablo.item(satir, 3)
                assert servis_item is not None
                beklenen_servis = kayit["servis_metodu"] or "Servis hazır değil"
                assert servis_item.text() == beklenen_servis

    @given(
        kayitlar=st.lists(eslestirme_kaydi_strategy, min_size=1, max_size=10),
        arama_metni=st.text(
            min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs"))
        ),
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_eslestirme_tablosu_arama_filtreleme_property(self, qtbot, kayitlar, arama_metni):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 9: Eşleştirme Tablosu**

        **Validates: Requirements 8.2**

        Herhangi bir arama metni girişinde, sistem kayıtları filtrelemeli ve eşleşenleri göstermelidir.
        """
        with patch("sontechsp.uygulama.moduller.pos.ui.bilesenler.eslestirme_dialog.kayitlari_listele") as mock_listele:
            mock_listele.return_value = kayitlar

            dialog = EslestirmeDialog()
            qtbot.addWidget(dialog)
            dialog.guncelleme_durdur()

            # Arama metnini gir
            dialog.arama_alani.setText(arama_metni)

            # Filtrelenmiş kayıtları hesapla
            arama_lower = arama_metni.lower()
            beklenen_kayitlar = []
            for kayit in kayitlar:
                if (
                    arama_lower in kayit["ekran_adi"].lower()
                    or arama_lower in kayit["buton_adi"].lower()
                    or arama_lower in kayit["handler_adi"].lower()
                    or arama_lower in (kayit["servis_metodu"] or "").lower()
                ):
                    beklenen_kayitlar.append(kayit)

            # Tablo satır sayısı filtrelenmiş kayıt sayısına eşit olmalı
            assert dialog.tablo.rowCount() == len(beklenen_kayitlar)

            # Kayıt sayısı etiketi filtrelenmiş sayıyı göstermeli
            beklenen_metin = f"Kayıt: {len(beklenen_kayitlar)}"
            assert dialog.kayit_sayisi_etiketi.text() == beklenen_metin

    @given(kayitlar=st.lists(eslestirme_kaydi_strategy, min_size=1, max_size=5))
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_eslestirme_tablosu_csv_disari_aktarim_property(self, qtbot, kayitlar):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 9: Eşleştirme Tablosu**

        **Validates: Requirements 8.4**

        Herhangi bir CSV dışa aktarım işleminde, sistem dosyayı başarıyla oluşturmalıdır.
        """
        with patch("sontechsp.uygulama.moduller.pos.ui.bilesenler.eslestirme_dialog.kayitlari_listele") as mock_listele:
            mock_listele.return_value = kayitlar

            # Geçici dosya oluştur
            with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as temp_file:
                temp_path = temp_file.name

            try:
                with patch(
                    "sontechsp.uygulama.moduller.pos.ui.bilesenler.eslestirme_dialog.csv_dosyasina_kaydet"
                ) as mock_csv:
                    mock_csv.return_value = True

                    dialog = EslestirmeDialog()
                    qtbot.addWidget(dialog)
                    dialog.guncelleme_durdur()

                    # CSV dışa aktarım butonunu test et
                    with patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName") as mock_dialog:
                        mock_dialog.return_value = (temp_path, "CSV Dosyaları (*.csv)")

                        # CSV butonuna tıkla
                        qtbot.mouseClick(dialog.csv_buton, Qt.MouseButton.LeftButton)

                        # csv_dosyasina_kaydet fonksiyonu çağrılmalı
                        mock_csv.assert_called_once_with(temp_path)

                        # Sinyal emit edilmeli
                        # Not: Sinyal testini mock ile yapıyoruz çünkü gerçek dosya işlemi mock'lanmış

            finally:
                # Geçici dosyayı temizle
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

    @given(kayitlar=st.lists(eslestirme_kaydi_strategy, min_size=0, max_size=10))
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_eslestirme_tablosu_otomatik_guncelleme_property(self, qtbot, kayitlar):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 9: Eşleştirme Tablosu**

        **Validates: Requirements 8.3**

        Herhangi bir otomatik güncelleme döngüsünde, sistem tabloyu güncel verilerle yenilemelidir.
        """
        with patch("sontechsp.uygulama.moduller.pos.ui.bilesenler.eslestirme_dialog.kayitlari_listele") as mock_listele:
            # İlk kayıtlar
            mock_listele.return_value = kayitlar

            dialog = EslestirmeDialog()
            qtbot.addWidget(dialog)

            # İlk güncelleme
            dialog._tabloyu_guncelle()
            ilk_satir_sayisi = dialog.tablo.rowCount()

            # Kayıtları değiştir
            yeni_kayitlar = (
                kayitlar
                + [
                    {
                        "ekran_adi": "Yeni Ekran",
                        "buton_adi": "YENİ",
                        "handler_adi": "yeni_handler",
                        "servis_metodu": "yeni_service.metod",
                        "kayit_zamani": "2024-12-18T11:00:00Z",
                        "cagrilma_sayisi": 0,
                    }
                ]
                if kayitlar
                else [
                    {
                        "ekran_adi": "İlk Ekran",
                        "buton_adi": "İLK",
                        "handler_adi": "ilk_handler",
                        "servis_metodu": "ilk_service.metod",
                        "kayit_zamani": "2024-12-18T11:00:00Z",
                        "cagrilma_sayisi": 1,
                    }
                ]
            )

            mock_listele.return_value = yeni_kayitlar

            # İkinci güncelleme
            dialog._tabloyu_guncelle()
            yeni_satir_sayisi = dialog.tablo.rowCount()

            # Satır sayısı değişmeli
            assert yeni_satir_sayisi == len(yeni_kayitlar)
            assert yeni_satir_sayisi != ilk_satir_sayisi or len(kayitlar) == 0

    def test_eslestirme_tablosu_servis_hazir_degil_durumu_property(self, qtbot):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 9: Eşleştirme Tablosu**

        **Validates: Requirements 8.5**

        Herhangi bir servis metodu mevcut olmadığında, sistem "Servis hazır değil" mesajını göstermeli.
        """
        kayitlar = [
            {
                "ekran_adi": "Test Ekran",
                "buton_adi": "TEST",
                "handler_adi": "test_handler",
                "servis_metodu": None,  # Servis hazır değil
                "kayit_zamani": "2024-12-18T10:30:00Z",
                "cagrilma_sayisi": 0,
            }
        ]

        with patch("sontechsp.uygulama.moduller.pos.ui.bilesenler.eslestirme_dialog.kayitlari_listele") as mock_listele:
            mock_listele.return_value = kayitlar

            dialog = EslestirmeDialog()
            qtbot.addWidget(dialog)
            dialog.guncelleme_durdur()

            # Tabloyu güncelle
            dialog._tabloyu_guncelle()

            # Servis metodu kolonunu kontrol et
            servis_item = dialog.tablo.item(0, 3)
            assert servis_item is not None
            assert servis_item.text() == "Servis hazır değil"

    def test_eslestirme_tablosu_dialog_acilma_kapanma_property(self, qtbot):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 9: Eşleştirme Tablosu**

        **Validates: Requirements 8.1**

        Herhangi bir dialog açılma/kapanma işleminde, sistem kaynak yönetimini doğru yapmalıdır.
        """
        kayitlar = []

        with patch("sontechsp.uygulama.moduller.pos.ui.bilesenler.eslestirme_dialog.kayitlari_listele") as mock_listele:
            mock_listele.return_value = kayitlar

            dialog = EslestirmeDialog()
            qtbot.addWidget(dialog)

            # Dialog açık olmalı
            assert dialog.isVisible() == False  # Henüz show() çağrılmadı

            # Dialog'u göster
            dialog.show()
            qtbot.waitForWindowShown(dialog)
            assert dialog.isVisible() == True

            # Timer çalışıyor olmalı
            assert dialog._guncelleme_timer is not None

            # Dialog'u kapat
            dialog.close()
            qtbot.waitUntil(lambda: not dialog.isVisible(), timeout=1000)

            # Timer durdurulmuş olmalı
            assert not dialog._guncelleme_timer.isActive()
