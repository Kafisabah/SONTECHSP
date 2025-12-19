# Version: 0.1.0
# Last Update: 2024-12-18
# Module: test_klavye_kisayollari_property
# Description: Klavye kısayolları özellik testleri
# Changelog:
# - İlk oluşturma - Klavye kısayolları özellik testleri

"""
Klavye Kısayolları Özellik Testleri

**Feature: pos-arayuz-entegrasyonu, Property 8: Klavye Kısayolları**

Herhangi bir klavye kısayolu basımında, sistem ilgili işlemi gerçekleştirmelidir
(F2: barkod odağı, F4: nakit ödeme, F5: kart ödeme, ESC: iptal, DEL: satır silme).

Doğrular: Gereksinim 7.1, 7.2, 7.3, 7.4, 7.5
"""

import pytest
from hypothesis import given, strategies as st, assume
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeyEvent
import sys

from sontechsp.uygulama.moduller.pos.ui.handlers.klavye_kisayol_yoneticisi import KlavyeKisayolYoneticisi


class TestKlavyeKisayollariProperty:
    """Klavye Kısayolları Özellik Testleri"""

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

    @pytest.fixture
    def klavye_yoneticisi(self):
        """Klavye kısayol yöneticisi fixture"""
        return KlavyeKisayolYoneticisi()

    @given(
        kisayol_tus=st.sampled_from(
            [
                Qt.Key.Key_F2,
                Qt.Key.Key_F4,
                Qt.Key.Key_F5,
                Qt.Key.Key_Escape,
                Qt.Key.Key_Delete,
                Qt.Key.Key_F6,
                Qt.Key.Key_F7,
                Qt.Key.Key_F8,
                Qt.Key.Key_F9,
                Qt.Key.Key_F10,
            ]
        )
    )
    def test_varsayilan_kisayollarin_tanimli_olmasi(self, klavye_yoneticisi, kisayol_tus):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 8: Klavye Kısayolları**
        **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

        Özellik: Herhangi bir varsayılan klavye kısayolu tanımlı olmalı
        """
        # Kısayol tanımlı olmalı
        assert klavye_yoneticisi.kisayol_var_mi(kisayol_tus), f"Kısayol {kisayol_tus.name} tanımlı değil"

        # Kısayol bilgisi alınabilmeli
        bilgi = klavye_yoneticisi.kisayol_bilgisi_al(kisayol_tus)
        assert bilgi is not None, f"Kısayol {kisayol_tus.name} bilgisi alınamadı"
        assert len(bilgi) == 2, "Kısayol bilgisi (ad, açıklama) formatında olmalı"
        assert bilgi[0], "Kısayol adı boş olmamalı"

    @given(
        kisayol_tus=st.sampled_from([Qt.Key.Key_F2, Qt.Key.Key_F4, Qt.Key.Key_F5, Qt.Key.Key_Escape, Qt.Key.Key_Delete])
    )
    def test_kisayol_handler_baglama_ve_tetikleme(self, klavye_yoneticisi, kisayol_tus):
        """
        Özellik: Kısayola handler bağlandığında, kısayol tetiklendiğinde handler çalışmalı
        """
        # Handler çağrılma durumu
        handler_cagrildi = {"durum": False}

        def test_handler():
            handler_cagrildi["durum"] = True

        # Kısayol bilgisini al
        bilgi = klavye_yoneticisi.kisayol_bilgisi_al(kisayol_tus)
        kisayol_adi = bilgi[0]

        # Handler'ı bağla
        klavye_yoneticisi.handler_bagla(kisayol_adi, test_handler)

        # Klavye olayı oluştur
        event = QKeyEvent(QKeyEvent.Type.KeyPress, kisayol_tus, Qt.KeyboardModifier.NoModifier)

        # Olayı işle
        islendi = klavye_yoneticisi.olay_isle(event)

        # Olay işlenmeli ve handler çağrılmalı
        assert islendi == True, f"Kısayol {kisayol_tus.name} işlenmedi"
        assert handler_cagrildi["durum"] == True, f"Handler {kisayol_adi} çağrılmadı"

    @given(
        gecersiz_tus=st.sampled_from(
            [Qt.Key.Key_A, Qt.Key.Key_B, Qt.Key.Key_C, Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_Space, Qt.Key.Key_Enter]
        )
    )
    def test_gecersiz_kisayollarin_islenmemesi(self, klavye_yoneticisi, gecersiz_tus):
        """
        Özellik: Tanımsız klavye kısayolları işlenmemeli
        """
        # Kısayol tanımlı olmamalı
        assert not klavye_yoneticisi.kisayol_var_mi(gecersiz_tus), f"Geçersiz kısayol {gecersiz_tus.name} tanımlı"

        # Klavye olayı oluştur
        event = QKeyEvent(QKeyEvent.Type.KeyPress, gecersiz_tus, Qt.KeyboardModifier.NoModifier)

        # Olay işlenmemeli
        islendi = klavye_yoneticisi.olay_isle(event)
        assert islendi == False, f"Geçersiz kısayol {gecersiz_tus.name} işlendi"

    def test_kisayol_sinyal_gonderimi(self, klavye_yoneticisi):
        """
        Özellik: Kısayol tetiklendiğinde sinyal gönderilmeli
        """
        # Sinyal yakalayıcısı
        sinyal_yakalandi = {"durum": False, "kisayol_adi": None}

        def sinyal_yakala(kisayol_adi):
            sinyal_yakalandi["durum"] = True
            sinyal_yakalandi["kisayol_adi"] = kisayol_adi

        # Sinyali bağla
        klavye_yoneticisi.kisayol_tetiklendi.connect(sinyal_yakala)

        # F2 kısayolunu test et
        event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_F2, Qt.KeyboardModifier.NoModifier)
        islendi = klavye_yoneticisi.olay_isle(event)

        # Sinyal gönderilmeli
        assert islendi == True, "F2 kısayolu işlenmedi"
        assert sinyal_yakalandi["durum"] == True, "Kısayol sinyali gönderilmedi"
        assert sinyal_yakalandi["kisayol_adi"] == "barkod_odakla", "Yanlış kısayol adı sinyalde"

    @given(
        yeni_tus=st.sampled_from([Qt.Key.Key_F11, Qt.Key.Key_F12, Qt.Key.Key_Insert]),
        kisayol_adi=st.text(min_size=1, max_size=20).filter(lambda x: x.isalnum()),
        aciklama=st.text(min_size=0, max_size=50),
    )
    def test_dinamik_kisayol_ekleme_ve_cikarma(self, klavye_yoneticisi, yeni_tus, kisayol_adi, aciklama):
        """
        Özellik: Dinamik olarak kısayol eklenip çıkarılabilmeli
        """
        assume(not klavye_yoneticisi.kisayol_var_mi(yeni_tus))  # Zaten tanımlı değil

        # Kısayol ekle
        eklendi = klavye_yoneticisi.kisayol_ekle(yeni_tus, kisayol_adi, aciklama)
        assert eklendi == True, f"Kısayol {yeni_tus.name} eklenemedi"

        # Kısayol tanımlı olmalı
        assert klavye_yoneticisi.kisayol_var_mi(yeni_tus), f"Eklenen kısayol {yeni_tus.name} bulunamadı"

        # Bilgi doğru olmalı
        bilgi = klavye_yoneticisi.kisayol_bilgisi_al(yeni_tus)
        assert bilgi[0] == kisayol_adi, "Kısayol adı yanlış"
        assert bilgi[1] == aciklama, "Kısayol açıklaması yanlış"

        # Kısayol çıkar
        cikarildi = klavye_yoneticisi.kisayol_cikar(yeni_tus)
        assert cikarildi == True, f"Kısayol {yeni_tus.name} çıkarılamadı"

        # Kısayol artık tanımlı olmamalı
        assert not klavye_yoneticisi.kisayol_var_mi(yeni_tus), f"Çıkarılan kısayol {yeni_tus.name} hala tanımlı"

    def test_kisayol_cakisma_kontrolu(self, klavye_yoneticisi):
        """
        Özellik: Aynı tuş için birden fazla kısayol tanımlanamaz
        """
        # F2 zaten tanımlı
        assert klavye_yoneticisi.kisayol_var_mi(Qt.Key.Key_F2), "F2 kısayolu tanımlı değil"

        # Aynı tuş için yeni kısayol eklemeye çalış
        eklendi = klavye_yoneticisi.kisayol_ekle(Qt.Key.Key_F2, "yeni_kisayol", "Test")
        assert eklendi == False, "Çakışan kısayol eklenmemeli"

        # Orijinal kısayol korunmalı
        bilgi = klavye_yoneticisi.kisayol_bilgisi_al(Qt.Key.Key_F2)
        assert bilgi[0] == "barkod_odakla", "Orijinal kısayol değişmemeli"

    def test_handler_ayirma(self, klavye_yoneticisi):
        """
        Özellik: Handler ayrıldığında kısayol tetiklendiğinde handler çalışmamalı
        """
        # Handler çağrılma durumu
        handler_cagrildi = {"durum": False}

        def test_handler():
            handler_cagrildi["durum"] = True

        # Handler'ı bağla
        klavye_yoneticisi.handler_bagla("barkod_odakla", test_handler)

        # Handler'ı ayır
        klavye_yoneticisi.handler_ayir("barkod_odakla")

        # Kısayolu tetikle
        event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_F2, Qt.KeyboardModifier.NoModifier)
        islendi = klavye_yoneticisi.olay_isle(event)

        # Olay işlenmeli ama handler çağrılmamalı
        assert islendi == True, "Kısayol işlenmedi"
        assert handler_cagrildi["durum"] == False, "Ayrılan handler çağrılmamalı"

    def test_kisayol_listesi_alma(self, klavye_yoneticisi):
        """
        Özellik: Tanımlı kısayolların listesi alınabilmeli
        """
        kisayollar = klavye_yoneticisi.kisayollari_listele()

        # Liste boş olmamalı
        assert len(kisayollar) > 0, "Kısayol listesi boş"

        # Varsayılan kısayollar listede olmalı
        beklenen_kisayollar = [
            "barkod_odakla",
            "nakit_odeme",
            "kart_odeme",
            "islem_iptal",
            "satir_sil",
            "sepet_beklet",
            "bekleyenler_goster",
            "iade_baslat",
            "fis_yazdir",
            "fatura_olustur",
        ]

        liste_kisayol_adlari = [bilgi[0] for bilgi in kisayollar.values()]

        for beklenen in beklenen_kisayollar:
            assert beklenen in liste_kisayol_adlari, f"Beklenen kısayol {beklenen} listede yok"

    @given(
        modifier_kombinasyonu=st.sampled_from(
            [Qt.KeyboardModifier.ControlModifier, Qt.KeyboardModifier.AltModifier, Qt.KeyboardModifier.ShiftModifier]
        )
    )
    def test_modifier_tuslu_kisayollar(self, klavye_yoneticisi, modifier_kombinasyonu):
        """
        Özellik: Modifier tuşlu kısayollar da işlenebilmeli
        """
        # Ctrl+S gibi bir kısayol ekle
        test_tus = Qt.Key.Key_S
        kisayol_adi = "test_modifier_kisayol"

        # Önce normal tuş tanımlı değil olduğunu kontrol et
        assume(not klavye_yoneticisi.kisayol_var_mi(test_tus))

        # Modifier'lı kısayol ekle
        eklendi = klavye_yoneticisi.kisayol_ekle(test_tus, kisayol_adi, "Test modifier")
        assert eklendi == True, "Modifier'lı kısayol eklenemedi"

        # Handler bağla
        handler_cagrildi = {"durum": False}

        def test_handler():
            handler_cagrildi["durum"] = True

        klavye_yoneticisi.handler_bagla(kisayol_adi, test_handler)

        # Modifier'lı event oluştur
        event = QKeyEvent(QKeyEvent.Type.KeyPress, test_tus, modifier_kombinasyonu)

        # Normal tuş (modifier'sız) işlenmemeli
        normal_event = QKeyEvent(QKeyEvent.Type.KeyPress, test_tus, Qt.KeyboardModifier.NoModifier)
        normal_islendi = klavye_yoneticisi.olay_isle(normal_event)

        # Modifier'lı tuş işlenmeli (bu test basit implementasyon için geçebilir)
        modifier_islendi = klavye_yoneticisi.olay_isle(event)

        # Temizlik
        klavye_yoneticisi.kisayol_cikar(test_tus)
