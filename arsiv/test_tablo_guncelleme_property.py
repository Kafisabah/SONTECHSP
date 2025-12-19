# Version: 0.1.0
# Last Update: 2024-12-16
# Module: tests.test_tablo_guncelleme_property
# Description: Tablo güncelleme tutarlılığı property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Tablo Güncelleme Property-Based Testleri

Bu modül UI tablo bileşenlerinin güncelleme tutarlılığını test eder.
Hypothesis kütüphanesi kullanılarak rastgele veri ile testler yapılır.
"""

import sys
from decimal import Decimal
from unittest.mock import Mock, MagicMock

import pytest
from hypothesis import given, settings, strategies as st
from PyQt6.QtWidgets import QApplication, QTableWidget
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from uygulama.arayuz.ekranlar.pos_satis import PosSatis
from uygulama.arayuz.servis_fabrikasi import ServisFabrikasi


class TestTabloGuncellemeProperty:
    """Tablo güncelleme tutarlılığı property testleri"""
    
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
        self.mock_pos_servisi = Mock()
        self.mock_servis_fabrikasi.pos_servisi.return_value = self.mock_pos_servisi
        
        # POS satış ekranını oluştur
        self.pos_ekrani = PosSatis(self.mock_servis_fabrikasi)
        
        # Mock servis yanıtları
        self.mock_pos_servisi.barkod_ekle.return_value = True
        self.mock_pos_servisi.odeme_tamamla.return_value = True
        self.mock_pos_servisi.satis_beklet.return_value = True
        self.mock_pos_servisi.satis_iptal.return_value = True
        
        # Sepeti temizle
        self.pos_ekrani.sepeti_temizle()
    
    def teardown_method(self):
        """Her test sonrası temizlik"""
        if hasattr(self, 'pos_ekrani'):
            self.pos_ekrani.close()
            self.pos_ekrani.deleteLater()
    
    @given(
        urun_sayisi=st.integers(min_value=1, max_value=10),
        barkod_prefix=st.text(min_size=3, max_size=8, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=48, max_codepoint=90
        ))
    )
    @settings(max_examples=100, deadline=5000)
    def test_property_tablo_guncelleme_tutarliligi(self, urun_sayisi, barkod_prefix):
        """
        **Feature: pyqt-arayuz-iskeleti, Property 6: Tablo güncelleme tutarlılığı**
        
        For any veri değişikliği, ilgili tablo bileşeni güncellenmiş veriyi göstermeli
        **Validates: Requirements 5.3**
        """
        # Arrange - Sepeti temizle ve başlangıç durumu kontrol et
        self.pos_ekrani.sepeti_temizle()
        assert self.pos_ekrani.sepet_tablo is not None
        assert self.pos_ekrani.sepet_tablo.rowCount() == 0
        assert len(self.pos_ekrani.sepet_verileri) == 0
        
        # Act - Rastgele ürünler ekle
        eklenen_urunler = []
        for i in range(urun_sayisi):
            barkod = f"{barkod_prefix}{i:03d}"
            
            # Barkod input'una yaz ve ekle
            self.pos_ekrani.barkod_input.setText(barkod)
            self.pos_ekrani.ekle_tiklandi()
            
            # Eklenen ürün bilgisini kaydet
            eklenen_urunler.append({
                "barkod": barkod,
                "urun_adi": f"Ürün {barkod}",
                "birim_fiyat": 10.50,
                "miktar": 1,
                "indirim": 0.0,
                "toplam": 10.50
            })
        
        # Assert - Tablo güncelleme tutarlılığı
        # 1. Sepet verilerinin doğru sayıda olması
        assert len(self.pos_ekrani.sepet_verileri) == urun_sayisi
        
        # 2. Tablo satır sayısının sepet verisi ile eşleşmesi
        assert self.pos_ekrani.sepet_tablo.rowCount() == urun_sayisi
        
        # 3. Her satırın doğru veri içermesi
        for row in range(urun_sayisi):
            sepet_verisi = self.pos_ekrani.sepet_verileri[row]
            beklenen_urun = eklenen_urunler[row]
            
            # Sepet verisinin doğruluğu
            assert sepet_verisi["urun_adi"] == beklenen_urun["urun_adi"]
            assert sepet_verisi["birim_fiyat"] == beklenen_urun["birim_fiyat"]
            assert sepet_verisi["miktar"] == beklenen_urun["miktar"]
            assert sepet_verisi["indirim"] == beklenen_urun["indirim"]
            assert sepet_verisi["toplam"] == beklenen_urun["toplam"]
            
            # Tablo hücrelerinin doğruluğu
            urun_adi_item = self.pos_ekrani.sepet_tablo.item(row, 0)
            birim_fiyat_item = self.pos_ekrani.sepet_tablo.item(row, 1)
            miktar_item = self.pos_ekrani.sepet_tablo.item(row, 2)
            indirim_item = self.pos_ekrani.sepet_tablo.item(row, 3)
            toplam_item = self.pos_ekrani.sepet_tablo.item(row, 4)
            
            assert urun_adi_item is not None
            assert urun_adi_item.text() == beklenen_urun["urun_adi"]
            
            assert birim_fiyat_item is not None
            assert "10,50" in birim_fiyat_item.text()  # Para formatı kontrolü
            
            assert miktar_item is not None
            assert miktar_item.text() == "1"
            
            assert indirim_item is not None
            assert "0,00" in indirim_item.text()  # Para formatı kontrolü
            
            assert toplam_item is not None
            assert "10,50" in toplam_item.text()  # Para formatı kontrolü
        
        # 4. Toplam bilgilerinin güncellenmesi
        beklenen_ara_toplam = urun_sayisi * 10.50
        assert "TL" in self.pos_ekrani.ara_toplam_label.text()
        assert "TL" in self.pos_ekrani.genel_toplam_label.text()
        
        # 5. Sepet temizleme sonrası tutarlılık
        self.pos_ekrani.sepeti_temizle()
        
        assert len(self.pos_ekrani.sepet_verileri) == 0
        assert self.pos_ekrani.sepet_tablo.rowCount() == 0
        assert "0,00" in self.pos_ekrani.ara_toplam_label.text()
        assert "0,00" in self.pos_ekrani.genel_toplam_label.text()
    
    @given(
        barkod=st.text(min_size=5, max_size=15, alphabet=st.characters(
            whitelist_categories=('Nd',), min_codepoint=48, max_codepoint=57
        ))
    )
    @settings(max_examples=50, deadline=3000)
    def test_property_tek_urun_ekleme_tutarliligi(self, barkod):
        """
        **Feature: pyqt-arayuz-iskeleti, Property 6: Tablo güncelleme tutarlılığı**
        
        For any tek ürün ekleme işlemi, tablo doğru şekilde güncellenmeli
        **Validates: Requirements 5.3**
        """
        # Arrange - Sepeti temizle ve başlangıç durumu
        self.pos_ekrani.sepeti_temizle()
        baslangic_satir_sayisi = self.pos_ekrani.sepet_tablo.rowCount()
        baslangic_veri_sayisi = len(self.pos_ekrani.sepet_verileri)
        
        # Act - Tek ürün ekle
        self.pos_ekrani.barkod_input.setText(barkod)
        self.pos_ekrani.ekle_tiklandi()
        
        # Assert - Güncelleme tutarlılığı
        # 1. Veri sayısının artması
        assert len(self.pos_ekrani.sepet_verileri) == baslangic_veri_sayisi + 1
        
        # 2. Tablo satır sayısının artması
        assert self.pos_ekrani.sepet_tablo.rowCount() == baslangic_satir_sayisi + 1
        
        # 3. Eklenen verinin doğruluğu
        son_veri = self.pos_ekrani.sepet_verileri[-1]
        assert son_veri["urun_adi"] == f"Ürün {barkod}"
        assert son_veri["birim_fiyat"] == 10.50
        assert son_veri["miktar"] == 1
        assert son_veri["toplam"] == 10.50
        
        # 4. Tablo son satırının doğruluğu
        son_satir = self.pos_ekrani.sepet_tablo.rowCount() - 1
        urun_adi_item = self.pos_ekrani.sepet_tablo.item(son_satir, 0)
        assert urun_adi_item is not None
        assert urun_adi_item.text() == f"Ürün {barkod}"
    
    @given(
        urun_sayisi=st.integers(min_value=2, max_value=5)
    )
    @settings(max_examples=30, deadline=3000)
    def test_property_coklu_islem_tutarliligi(self, urun_sayisi):
        """
        **Feature: pyqt-arayuz-iskeleti, Property 6: Tablo güncelleme tutarlılığı**
        
        For any çoklu ürün ekleme ve temizleme işlemi, tablo tutarlı kalmalı
        **Validates: Requirements 5.3**
        """
        # Arrange - Sepeti temizle (test başında)
        self.pos_ekrani.sepeti_temizle()
        
        # Act - Çoklu ürün ekle
        for i in range(urun_sayisi):
            barkod = f"MULTI{i:04d}"
            self.pos_ekrani.barkod_input.setText(barkod)
            self.pos_ekrani.ekle_tiklandi()
        
        # Assert - Ekleme sonrası tutarlılık
        assert len(self.pos_ekrani.sepet_verileri) == urun_sayisi
        assert self.pos_ekrani.sepet_tablo.rowCount() == urun_sayisi
        
        # Act - Sepeti temizle
        self.pos_ekrani.sepeti_temizle()
        
        # Assert - Temizleme sonrası tutarlılık
        assert len(self.pos_ekrani.sepet_verileri) == 0
        assert self.pos_ekrani.sepet_tablo.rowCount() == 0
        
        # Act - Tekrar ürün ekle
        self.pos_ekrani.barkod_input.setText("FINAL001")
        self.pos_ekrani.ekle_tiklandi()
        
        # Assert - Yeniden ekleme tutarlılığı
        assert len(self.pos_ekrani.sepet_verileri) == 1
        assert self.pos_ekrani.sepet_tablo.rowCount() == 1
        
        son_veri = self.pos_ekrani.sepet_verileri[0]
        assert son_veri["urun_adi"] == "Ürün FINAL001"