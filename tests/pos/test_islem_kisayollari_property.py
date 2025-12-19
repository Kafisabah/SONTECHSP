# Version: 0.1.0
# Last Update: 2024-12-18
# Module: test_islem_kisayollari_property
# Description: İşlem kısayolları özellik testleri
# Changelog:
# - İlk oluşturma - İşlem kısayolları özellik testleri

"""
İşlem Kısayolları Özellik Testleri

**Feature: pos-arayuz-entegrasyonu, Property 7: İşlem Kısayolları**

Herhangi bir işlem kısayolu kullanımında, sistem ilgili işlemi gerçekleştirmeli
(bekletme, iade dialog, fiş yazdırma).

Doğrular: Gereksinim 6.2, 6.3, 6.4, 6.5
"""

import pytest
from hypothesis import given, strategies as st, assume
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
import sys

from sontechsp.uygulama.moduller.pos.ui.bilesenler.islem_kisayollari import IslemKisayollari


class TestIslemKisayollariProperty:
    """İşlem Kısayolları Özellik Testleri"""

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
    def islem_kisayollari(self):
        """İşlem kısayolları paneli fixture"""
        panel = IslemKisayollari()
        panel.baslat()
        return panel

    @given(sepet_bos=st.booleans(), satis_tamamlandi=st.booleans())
    def test_buton_durumlarinin_dogru_ayarlanmasi(self, islem_kisayollari, sepet_bos, satis_tamamlandi):
        """
        Özellik 7.1: Buton durumları sepet ve satış durumuna göre doğru ayarlanmalı
        """
        # Durum güncelle
        islem_kisayollari.guncelle({"sepet_bos": sepet_bos, "satis_tamamlandi": satis_tamamlandi})

        # BEKLET butonu: Sepet boş değilse aktif olmalı
        assert islem_kisayollari.buton_aktif_mi("beklet") == (not sepet_bos)

        # BEKLEYENLER butonu: Her zaman aktif olmalı
        assert islem_kisayollari.buton_aktif_mi("bekleyenler") == True

        # İADE butonu: Her zaman aktif olmalı
        assert islem_kisayollari.buton_aktif_mi("iade") == True

        # İPTAL butonu: Sepet boş değilse aktif olmalı
        assert islem_kisayollari.buton_aktif_mi("iptal") == (not sepet_bos)

        # FİŞ YAZDIR butonu: Satış tamamlandıysa aktif olmalı
        assert islem_kisayollari.buton_aktif_mi("fis_yazdir") == satis_tamamlandi

        # FATURA butonu: Satış tamamlandıysa aktif olmalı
        assert islem_kisayollari.buton_aktif_mi("fatura") == satis_tamamlandi

    @given(kisayol=st.sampled_from(["F6", "F7", "F8", "Escape", "F9", "F10"]))
    def test_klavye_kisayollarinin_dogru_islenmesi(self, islem_kisayollari, kisayol):
        """
        Özellik 7.2: Klavye kısayolları doğru butonları tetiklemeli
        """
        # Tüm butonları aktif hale getir
        islem_kisayollari.guncelle({"sepet_bos": False, "satis_tamamlandi": True})

        # Sinyal yakalayıcıları
        sinyal_yakalandi = {"durum": False}

        def sinyal_yakala():
            sinyal_yakalandi["durum"] = True

        # Kısayola göre sinyal bağla
        if kisayol == "F6":
            islem_kisayollari.beklet_tiklandi.connect(sinyal_yakala)
        elif kisayol == "F7":
            islem_kisayollari.bekleyenler_tiklandi.connect(sinyal_yakala)
        elif kisayol == "F8":
            islem_kisayollari.iade_tiklandi.connect(sinyal_yakala)
        elif kisayol == "Escape":
            islem_kisayollari.iptal_tiklandi.connect(sinyal_yakala)
        elif kisayol == "F9":
            islem_kisayollari.fis_yazdir_tiklandi.connect(sinyal_yakala)
        elif kisayol == "F10":
            islem_kisayollari.fatura_tiklandi.connect(sinyal_yakala)

        # Kısayolu işle
        islendi = islem_kisayollari.klavye_kisayolu_isle(kisayol)

        # Kısayol işlenmeli ve sinyal gönderilmeli
        assert islendi == True
        assert sinyal_yakalandi["durum"] == True

    @given(buton_adi=st.sampled_from(["beklet", "bekleyenler", "iade", "iptal", "fis_yazdir", "fatura"]))
    def test_buton_tiklama_sinyallerinin_gonderilmesi(self, islem_kisayollari, buton_adi):
        """
        Özellik 7.3: Buton tıklamaları doğru sinyalleri göndermeli
        """
        # Tüm butonları aktif hale getir
        islem_kisayollari.guncelle({"sepet_bos": False, "satis_tamamlandi": True})

        # Sinyal yakalayıcısı
        sinyal_yakalandi = {"durum": False}

        def sinyal_yakala():
            sinyal_yakalandi["durum"] = True

        # Butona göre sinyal bağla
        if buton_adi == "beklet":
            islem_kisayollari.beklet_tiklandi.connect(sinyal_yakala)
        elif buton_adi == "bekleyenler":
            islem_kisayollari.bekleyenler_tiklandi.connect(sinyal_yakala)
        elif buton_adi == "iade":
            islem_kisayollari.iade_tiklandi.connect(sinyal_yakala)
        elif buton_adi == "iptal":
            islem_kisayollari.iptal_tiklandi.connect(sinyal_yakala)
        elif buton_adi == "fis_yazdir":
            islem_kisayollari.fis_yazdir_tiklandi.connect(sinyal_yakala)
        elif buton_adi == "fatura":
            islem_kisayollari.fatura_tiklandi.connect(sinyal_yakala)

        # Butonu tıkla
        buton = islem_kisayollari.buton_al(buton_adi)
        assert buton is not None

        if buton.isEnabled():
            buton.click()
            # Sinyal gönderilmeli
            assert sinyal_yakalandi["durum"] == True

    def test_baslangic_durumunda_buton_durumlarinin_dogru_olmasi(self, islem_kisayollari):
        """
        Özellik 7.4: Başlangıç durumunda buton durumları doğru olmalı
        """
        # Başlangıç durumunda sepet boş, satış tamamlanmamış
        assert islem_kisayollari.buton_aktif_mi("beklet") == False  # Sepet boş
        assert islem_kisayollari.buton_aktif_mi("bekleyenler") == True  # Her zaman aktif
        assert islem_kisayollari.buton_aktif_mi("iade") == True  # Her zaman aktif
        assert islem_kisayollari.buton_aktif_mi("iptal") == False  # Sepet boş
        assert islem_kisayollari.buton_aktif_mi("fis_yazdir") == False  # Satış tamamlanmamış
        assert islem_kisayollari.buton_aktif_mi("fatura") == False  # Satış tamamlanmamış

    @given(gecersiz_kisayol=st.text().filter(lambda x: x not in ["F6", "F7", "F8", "Escape", "F9", "F10"]))
    def test_gecersiz_klavye_kisayollarinin_islenmemesi(self, islem_kisayollari, gecersiz_kisayol):
        """
        Özellik 7.5: Geçersiz klavye kısayolları işlenmemeli
        """
        assume(len(gecersiz_kisayol) > 0)  # Boş string hariç

        # Geçersiz kısayol işlenmemeli
        islendi = islem_kisayollari.klavye_kisayolu_isle(gecersiz_kisayol)
        assert islendi == False

    def test_temizleme_sonrasi_baslangic_durumuna_donmesi(self, islem_kisayollari):
        """
        Özellik 7.6: Temizleme sonrası başlangıç durumuna dönmeli
        """
        # Durumu değiştir
        islem_kisayollari.guncelle({"sepet_bos": False, "satis_tamamlandi": True})

        # Temizle
        islem_kisayollari.temizle()

        # Başlangıç durumuna dönmeli
        assert islem_kisayollari.buton_aktif_mi("beklet") == False
        assert islem_kisayollari.buton_aktif_mi("fis_yazdir") == False
        assert islem_kisayollari.buton_aktif_mi("fatura") == False

    @given(sepet_durumu_degisiklikleri=st.lists(st.booleans(), min_size=1, max_size=10))
    def test_sepet_durumu_degisikliklerinin_butonlara_yansimasi(self, islem_kisayollari, sepet_durumu_degisiklikleri):
        """
        Özellik 7.7: Sepet durumu değişiklikleri butonlara doğru yansımalı
        """
        for sepet_bos in sepet_durumu_degisiklikleri:
            islem_kisayollari.sepet_durumu_ayarla(sepet_bos)

            # Sepet durumuna bağlı butonlar doğru durumda olmalı
            assert islem_kisayollari.buton_aktif_mi("beklet") == (not sepet_bos)
            assert islem_kisayollari.buton_aktif_mi("iptal") == (not sepet_bos)

    @given(satis_durumu_degisiklikleri=st.lists(st.booleans(), min_size=1, max_size=10))
    def test_satis_durumu_degisikliklerinin_butonlara_yansimasi(self, islem_kisayollari, satis_durumu_degisiklikleri):
        """
        Özellik 7.8: Satış durumu değişiklikleri butonlara doğru yansımalı
        """
        for satis_tamamlandi in satis_durumu_degisiklikleri:
            islem_kisayollari.satis_durumu_ayarla(satis_tamamlandi)

            # Satış durumuna bağlı butonlar doğru durumda olmalı
            assert islem_kisayollari.buton_aktif_mi("fis_yazdir") == satis_tamamlandi
            assert islem_kisayollari.buton_aktif_mi("fatura") == satis_tamamlandi
