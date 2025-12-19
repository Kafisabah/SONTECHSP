# Version: 0.1.0
# Last Update: 2024-12-16
# Module: tests.test_dialog_acma_property
# Description: Dialog açma tutarlılığı property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Dialog Açma Property-Based Testleri

Bu modül UI dialog açma işlemlerinin tutarlılığını test eder.
Hypothesis kütüphanesi kullanılarak rastgele veri ile testler yapılır.
"""

import sys
from unittest.mock import Mock, MagicMock, patch

import pytest
from hypothesis import given, settings, strategies as st
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from uygulama.arayuz.ekranlar.urunler_stok import UrunlerStok
from uygulama.arayuz.servis_fabrikasi import ServisFabrikasi


class TestDialogAcmaProperty:
    """Dialog açma tutarlılığı property testleri"""
    
    @classmethod
    def setup_class(cls):
        """Test sınıfı kurulumu"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setup_method(self):
        """Her test öncesi kurulum"""
        # Mock servis fabrikası oluştur
        self.mock_servis_fabrikasi = Mock(spec=ServisFabrikasi)
        self.mock_stok_servisi = Mock()
        self.mock_servis_fabrikasi.stok_servisi.return_value = self.mock_stok_servisi
        
        # Ürünler stok ekranını oluştur
        self.urunler_ekrani = UrunlerStok(self.mock_servis_fabrikasi)
        
        # Mock servis yanıtları
        self.mock_stok_servisi.urun_ara.return_value = []
        self.mock_stok_servisi.urun_filtrele.return_value = []
        self.mock_stok_servisi.urun_listesi_getir.return_value = []
        
        # Test verileri ekle
        self.urunler_ekrani.urun_verileri = [
            {
                "urun_kodu": "TEST001",
                "urun_adi": "Test Ürün 1",
                "kategori": "Elektronik",
                "birim": "adet",
                "stok": 50,
                "birim_fiyat": 25.50,
                "toplam_deger": 1275.0
            },
            {
                "urun_kodu": "TEST002",
                "urun_adi": "Test Ürün 2",
                "kategori": "Giyim",
                "birim": "adet",
                "stok": 30,
                "birim_fiyat": 45.00,
                "toplam_deger": 1350.0
            }
        ]
        self.urunler_ekrani.urun_tablosunu_guncelle()
    
    def teardown_method(self):
        """Her test sonrası temizlik"""
        if hasattr(self, 'urunler_ekrani'):
            self.urunler_ekrani.close()
            self.urunler_ekrani.deleteLater()
    
    @given(
        satir_indeksi=st.integers(min_value=0, max_value=1)
    )
    @settings(max_examples=50, deadline=3000)
    @patch('uygulama.arayuz.yardimcilar.UIYardimcilari.bilgi_goster')
    def test_property_yeni_urun_dialog_acma_tutarliligi(self, mock_bilgi_goster, satir_indeksi):
        """
        **Feature: pyqt-arayuz-iskeleti, Property 5: Dialog açma tutarlılığı**
        
        For any yeni ürün ekleme işlemi, dialog penceresi görüntülenmeli
        **Validates: Requirements 6.2**
        """
        # Arrange - Başlangıç durumu
        assert self.urunler_ekrani.yeni_urun_buton is not None
        
        # Act - Yeni ürün butonuna tıkla
        self.urunler_ekrani.yeni_urun_ekle()
        
        # Assert - Dialog açma tutarlılığı
        # 1. Bilgi gösterme fonksiyonunun çağrılması
        mock_bilgi_goster.assert_called_once()
        
        # 2. Çağrılan parametrelerin doğruluğu
        call_args = mock_bilgi_goster.call_args
        assert call_args[0][1] == "Bilgi"  # Başlık
        assert "Yeni ürün ekleme dialog'u açılacak" in call_args[0][2]  # Mesaj
    
    @given(
        satir_indeksi=st.integers(min_value=0, max_value=1)
    )
    @settings(max_examples=50, deadline=3000)
    @patch('uygulama.arayuz.yardimcilar.UIYardimcilari.bilgi_goster')
    def test_property_urun_duzenleme_dialog_tutarliligi(self, mock_bilgi_goster, satir_indeksi):
        """
        **Feature: pyqt-arayuz-iskeleti, Property 5: Dialog açma tutarlılığı**
        
        For any ürün düzenleme işlemi, ilgili dialog penceresi görüntülenmeli
        **Validates: Requirements 6.3**
        """
        # Arrange - Satır seç
        self.urunler_ekrani.urun_tablo.setCurrentCell(satir_indeksi, 0)
        
        # Act - Ürün düzenleme işlemi
        self.urunler_ekrani.urun_duzenle()
        
        # Assert - Dialog açma tutarlılığı
        # 1. Bilgi gösterme fonksiyonunun çağrılması
        mock_bilgi_goster.assert_called_once()
        
        # 2. Çağrılan parametrelerin doğruluğu
        call_args = mock_bilgi_goster.call_args
        assert call_args[0][1] == "Bilgi"  # Başlık
        assert "Ürün düzenleme dialog'u açılacak" in call_args[0][2]  # Mesaj
        
        # 3. Seçili ürün kodunun mesajda bulunması
        beklenen_urun_kodu = self.urunler_ekrani.urun_verileri[satir_indeksi]["urun_kodu"]
        assert beklenen_urun_kodu in call_args[0][2]
    
    @given(
        satir_indeksi=st.integers(min_value=0, max_value=1)
    )
    @settings(max_examples=50, deadline=3000)
    @patch('uygulama.arayuz.yardimcilar.UIYardimcilari.bilgi_goster')
    def test_property_stok_sayim_dialog_tutarliligi(self, mock_bilgi_goster, satir_indeksi):
        """
        **Feature: pyqt-arayuz-iskeleti, Property 5: Dialog açma tutarlılığı**
        
        For any stok sayım işlemi, sayım dialog penceresi görüntülenmeli
        **Validates: Requirements 6.4**
        """
        # Arrange - Satır seç
        self.urunler_ekrani.urun_tablo.setCurrentCell(satir_indeksi, 0)
        
        # Act - Stok sayım işlemi
        self.urunler_ekrani.stok_sayim()
        
        # Assert - Dialog açma tutarlılığı
        # 1. Bilgi gösterme fonksiyonunun çağrılması
        mock_bilgi_goster.assert_called_once()
        
        # 2. Çağrılan parametrelerin doğruluğu
        call_args = mock_bilgi_goster.call_args
        assert call_args[0][1] == "Bilgi"  # Başlık
        assert "Stok sayım dialog'u açılacak" in call_args[0][2]  # Mesaj
        
        # 3. Seçili ürün kodunun mesajda bulunması
        beklenen_urun_kodu = self.urunler_ekrani.urun_verileri[satir_indeksi]["urun_kodu"]
        assert beklenen_urun_kodu in call_args[0][2]
    
    @given(
        satir_indeksi=st.integers(min_value=0, max_value=1)
    )
    @settings(max_examples=50, deadline=3000)
    @patch('uygulama.arayuz.yardimcilar.UIYardimcilari.bilgi_goster')
    def test_property_stok_transfer_dialog_tutarliligi(self, mock_bilgi_goster, satir_indeksi):
        """
        **Feature: pyqt-arayuz-iskeleti, Property 5: Dialog açma tutarlılığı**
        
        For any stok transfer işlemi, transfer dialog penceresi görüntülenmeli
        **Validates: Requirements 6.4**
        """
        # Arrange - Satır seç
        self.urunler_ekrani.urun_tablo.setCurrentCell(satir_indeksi, 0)
        
        # Act - Stok transfer işlemi
        self.urunler_ekrani.stok_transfer()
        
        # Assert - Dialog açma tutarlılığı
        # 1. Bilgi gösterme fonksiyonunun çağrılması
        mock_bilgi_goster.assert_called_once()
        
        # 2. Çağrılan parametrelerin doğruluğu
        call_args = mock_bilgi_goster.call_args
        assert call_args[0][1] == "Bilgi"  # Başlık
        assert "Stok transfer dialog'u açılacak" in call_args[0][2]  # Mesaj
        
        # 3. Seçili ürün kodunun mesajda bulunması
        beklenen_urun_kodu = self.urunler_ekrani.urun_verileri[satir_indeksi]["urun_kodu"]
        assert beklenen_urun_kodu in call_args[0][2]
    
    @patch('uygulama.arayuz.yardimcilar.UIYardimcilari.hata_goster')
    def test_property_secim_olmadan_dialog_hata_tutarliligi(self, mock_hata_goster):
        """
        **Feature: pyqt-arayuz-iskeleti, Property 5: Dialog açma tutarlılığı**
        
        For any seçim olmadan dialog açma işlemi, hata mesajı görüntülenmeli
        **Validates: Requirements 6.2, 6.3, 6.4**
        """
        # Arrange - Hiçbir satır seçili değil
        self.urunler_ekrani.urun_tablo.clearSelection()
        self.urunler_ekrani.urun_tablo.setCurrentCell(-1, -1)
        
        # Act & Assert - Düzenleme işlemi
        self.urunler_ekrani.urun_duzenle()
        mock_hata_goster.assert_called()
        
        call_args = mock_hata_goster.call_args
        assert call_args[0][1] == "Hata"
        assert "düzenlemek için bir ürün seçin" in call_args[0][2]
        
        # Reset mock
        mock_hata_goster.reset_mock()
        
        # Act & Assert - Sayım işlemi
        self.urunler_ekrani.stok_sayim()
        mock_hata_goster.assert_called()
        
        call_args = mock_hata_goster.call_args
        assert call_args[0][1] == "Hata"
        assert "sayım için bir ürün seçin" in call_args[0][2]
        
        # Reset mock
        mock_hata_goster.reset_mock()
        
        # Act & Assert - Transfer işlemi
        self.urunler_ekrani.stok_transfer()
        mock_hata_goster.assert_called()
        
        call_args = mock_hata_goster.call_args
        assert call_args[0][1] == "Hata"
        assert "transfer için bir ürün seçin" in call_args[0][2]
    
    @given(
        rapor_tipi=st.sampled_from(["kritik_stok", "stok_deger", "excel_aktar"])
    )
    @settings(max_examples=30, deadline=3000)
    @patch('uygulama.arayuz.yardimcilar.UIYardimcilari.bilgi_goster')
    def test_property_rapor_dialog_tutarliligi(self, mock_bilgi_goster, rapor_tipi):
        """
        **Feature: pyqt-arayuz-iskeleti, Property 5: Dialog açma tutarlılığı**
        
        For any rapor işlemi, ilgili rapor dialog'u görüntülenmeli
        **Validates: Requirements 6.2, 6.3, 6.4**
        """
        # Act - Rapor türüne göre işlem yap
        if rapor_tipi == "kritik_stok":
            self.urunler_ekrani.kritik_stok_raporu()
            beklenen_mesaj = "Kritik stok raporu açılacak"
        elif rapor_tipi == "stok_deger":
            self.urunler_ekrani.stok_deger_raporu()
            beklenen_mesaj = "Stok değer raporu açılacak"
        elif rapor_tipi == "excel_aktar":
            self.urunler_ekrani.excel_aktar()
            beklenen_mesaj = "Excel aktarım işlemi başlatılacak"
        
        # Assert - Dialog açma tutarlılığı
        # 1. Bilgi gösterme fonksiyonunun çağrılması
        mock_bilgi_goster.assert_called_once()
        
        # 2. Çağrılan parametrelerin doğruluğu
        call_args = mock_bilgi_goster.call_args
        assert call_args[0][1] == "Bilgi"  # Başlık
        assert beklenen_mesaj in call_args[0][2]  # Mesaj