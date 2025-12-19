# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_pos_klavye_kisayollari_property
# Description: POS klavye kısayolları özellik tabanlı testleri
# Changelog:
# - İlk oluşturma

"""
POS Klavye Kısayolları Özellik Tabanlı Testleri

**Feature: pos-yeni-ekran-tasarimi, Property 6: Klavye Kısayolları**
**Validates: Requirements 2.3, 8.5**
"""

import pytest
from hypothesis import given, strategies as st, assume
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtTest import QTest

from sontechsp.uygulama.arayuz.ekranlar.pos.klavye_kisayol_yoneticisi import KlavyeKisayolYoneticisi
from sontechsp.uygulama.arayuz.ekranlar.pos.pos_satis_ekrani import POSSatisEkrani


class TestPOSKlavyeKisayollariProperty:
    """POS klavye kısayolları özellik testleri"""

    @pytest.fixture
    def pos_ekrani(self, qtbot):
        """POS ekranı fixture'ı"""
        ekran = POSSatisEkrani()
        qtbot.addWidget(ekran)
        return ekran

    @given(
        kisayol_turu=st.sampled_from(
            [
                "barkod_odakla",
                "nakit_odeme",
                "kart_odeme",
                "parcali_odeme",
                "acik_hesap_odeme",
                "sepet_beklet",
                "bekleyenler_goster",
                "iade_islemi",
                "islem_iptal",
                "satir_sil",
            ]
        )
    )
    def test_klavye_kisayolu_tetikleme_property(self, pos_ekrani, qtbot, kisayol_turu):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 6: Klavye Kısayolları**

        Herhangi bir klavye kısayolu basımında (F2: barkod odağı, F4-F7: ödeme türleri,
        F8-F10: işlem kısayolları, ESC: iptal, +/-: adet değiştir),
        sistem ilgili işlemi gerçekleştirmelidir

        **Validates: Requirements 2.3, 8.5**
        """
        # Kısayol - tuş eşleştirmesi
        kisayol_tus_map = {
            "barkod_odakla": Qt.Key.Key_F2,
            "nakit_odeme": Qt.Key.Key_F4,
            "kart_odeme": Qt.Key.Key_F5,
            "parcali_odeme": Qt.Key.Key_F6,
            "acik_hesap_odeme": Qt.Key.Key_F7,
            "sepet_beklet": Qt.Key.Key_F8,
            "bekleyenler_goster": Qt.Key.Key_F9,
            "iade_islemi": Qt.Key.Key_F10,
            "islem_iptal": Qt.Key.Key_Escape,
            "satir_sil": Qt.Key.Key_Delete,
        }

        tus = kisayol_tus_map[kisayol_turu]

        # Sinyal yakalayıcı
        tetiklenen_kisayollar = []
        pos_ekrani.klavye_yoneticisi.kisayol_tetiklendi.connect(lambda k: tetiklenen_kisayollar.append(k))

        # Tuş olayı oluştur ve gönder
        key_event = QKeyEvent(QKeyEvent.Type.KeyPress, tus, Qt.KeyboardModifier.NoModifier)
        pos_ekrani.keyPressEvent(key_event)

        # Kısayolun tetiklendiğini doğrula
        assert len(tetiklenen_kisayollar) == 1
        assert tetiklenen_kisayollar[0] == kisayol_turu

    @given(
        gecersiz_tus=st.sampled_from(
            [Qt.Key.Key_A, Qt.Key.Key_B, Qt.Key.Key_C, Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_Space, Qt.Key.Key_Enter]
        )
    )
    def test_gecersiz_klavye_tusu_property(self, pos_ekrani, qtbot, gecersiz_tus):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 6: Klavye Kısayolları**

        Tanımlı olmayan tuşlar basıldığında sistem kısayol tetiklememeli

        **Validates: Requirements 2.3, 8.5**
        """
        # Sinyal yakalayıcı
        tetiklenen_kisayollar = []
        pos_ekrani.klavye_yoneticisi.kisayol_tetiklendi.connect(lambda k: tetiklenen_kisayollar.append(k))

        # Geçersiz tuş olayı oluştur ve gönder
        key_event = QKeyEvent(QKeyEvent.Type.KeyPress, gecersiz_tus, Qt.KeyboardModifier.NoModifier)
        pos_ekrani.keyPressEvent(key_event)

        # Hiçbir kısayolun tetiklenmediğini doğrula
        assert len(tetiklenen_kisayollar) == 0

    @given(
        modifier=st.sampled_from(
            [Qt.KeyboardModifier.ControlModifier, Qt.KeyboardModifier.AltModifier, Qt.KeyboardModifier.ShiftModifier]
        ),
        tus=st.sampled_from(
            [
                Qt.Key.Key_F2,
                Qt.Key.Key_F4,
                Qt.Key.Key_F5,
                Qt.Key.Key_F6,
                Qt.Key.Key_F7,
                Qt.Key.Key_F8,
                Qt.Key.Key_F9,
                Qt.Key.Key_F10,
            ]
        ),
    )
    def test_modifier_tuslu_kisayol_property(self, pos_ekrani, qtbot, modifier, tus):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 6: Klavye Kısayolları**

        Modifier tuşları (Ctrl, Alt, Shift) ile birlikte basılan tuşlar
        kısayol tetiklememeli

        **Validates: Requirements 2.3, 8.5**
        """
        # Sinyal yakalayıcı
        tetiklenen_kisayollar = []
        pos_ekrani.klavye_yoneticisi.kisayol_tetiklendi.connect(lambda k: tetiklenen_kisayollar.append(k))

        # Modifier'lı tuş olayı oluştur ve gönder
        key_event = QKeyEvent(QKeyEvent.Type.KeyPress, tus, modifier)
        pos_ekrani.keyPressEvent(key_event)

        # Hiçbir kısayolun tetiklenmediğini doğrula
        assert len(tetiklenen_kisayollar) == 0

    def test_f2_barkod_odaklama_property(self, pos_ekrani, qtbot):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 6: Klavye Kısayolları**

        F2 tuşu basıldığında barkod alanına odak verilmeli

        **Validates: Requirements 2.3**
        """
        # Başlangıçta barkod alanının odakta olmadığından emin ol
        pos_ekrani.ust_bar.urun_arama_combo.setFocus()
        assert not pos_ekrani.ust_bar.barkod_edit.hasFocus()

        # F2 tuşunu bas
        key_event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_F2, Qt.KeyboardModifier.NoModifier)
        pos_ekrani.keyPressEvent(key_event)

        # Barkod alanının odakta olduğunu doğrula
        assert pos_ekrani.ust_bar.barkod_edit.hasFocus()

    @given(adet_degisim=st.sampled_from([1, -1]))  # + veya - tuşu
    def test_adet_degistirme_kisayolu_property(self, pos_ekrani, qtbot, adet_degisim):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 6: Klavye Kısayolları**

        +/- tuşları basıldığında seçili ürünün adeti değişmeli

        **Validates: Requirements 8.5**
        """
        # Sepete ürün ekle
        from sontechsp.uygulama.arayuz.ekranlar.pos.sepet_modeli import SepetOgesi
        from decimal import Decimal

        urun = SepetOgesi(
            barkod="123456", urun_adi="Test Ürün", adet=5, birim_fiyat=Decimal("10.00"), toplam_fiyat=Decimal("50.00")
        )
        pos_ekrani.sepet_modeli.oge_ekle(urun)

        # İlk satırı seç
        pos_ekrani.sepet_tablo.selectRow(0)

        baslangic_adet = pos_ekrani.sepet_modeli.sepet_ogeleri[0].adet

        # Adet değiştirme tuşunu bas
        if adet_degisim == 1:
            tus = Qt.Key.Key_Plus
        else:
            tus = Qt.Key.Key_Minus

        key_event = QKeyEvent(QKeyEvent.Type.KeyPress, tus, Qt.KeyboardModifier.NoModifier)
        pos_ekrani.keyPressEvent(key_event)

        # Adetin değiştiğini doğrula
        if baslangic_adet + adet_degisim > 0:
            # Adet pozitif kalıyorsa güncellenmeli
            assert pos_ekrani.sepet_modeli.sepet_ogeleri[0].adet == baslangic_adet + adet_degisim
        else:
            # Adet 0 veya negatif olursa ürün silinmeli
            assert len(pos_ekrani.sepet_modeli.sepet_ogeleri) == 0

    def test_kisayol_yoneticisi_bagimsizlik_property(self, qtbot):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 6: Klavye Kısayolları**

        Klavye kısayol yöneticisi bağımsız olarak çalışabilmeli

        **Validates: Requirements 2.3, 8.5**
        """
        from PyQt6.QtWidgets import QWidget

        # Bağımsız widget oluştur
        widget = QWidget()
        qtbot.addWidget(widget)

        # Kısayol yöneticisi oluştur
        yonetici = KlavyeKisayolYoneticisi(widget)

        # Kısayolların tanımlı olduğunu doğrula
        kisayollar = yonetici.kisayollari_listele()
        assert len(kisayollar) > 0

        # F2 kısayolunun var olduğunu doğrula
        assert yonetici.kisayol_var_mi(Qt.Key.Key_F2)

        # Geçersiz tuşun olmadığını doğrula
        assert not yonetici.kisayol_var_mi(Qt.Key.Key_A)
