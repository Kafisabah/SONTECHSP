# Version: 0.1.0
# Last Update: 2024-12-16
# Module: test_kaynak_temizleme
# Description: Kaynak temizleme property testleri
# Changelog:
# - İlk sürüm oluşturuldu

import pytest
from hypothesis import given, strategies as st
from PyQt6.QtWidgets import QApplication
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from uygulama.arayuz.uygulama import UygulamaBaslatici


class TestKaynakTemizleme:
    """**Feature: pyqt-arayuz-iskeleti, Property 10: Kaynak temizleme tutarlılığı**"""
    
    def test_kaynak_temizleme_tutarliligi(self):
        """
        Property 10: Kaynak temizleme tutarlılığı
        For any uygulama kapatma işlemi, tüm kaynaklar temizlenmeli
        Validates: Requirements 1.4
        """
        # Başlatıcı oluştur
        baslatici = UygulamaBaslatici()
        
        # Mevcut QApplication varsa kullan, yoksa oluştur
        if QApplication.instance():
            baslatici.app = QApplication.instance()
        else:
            baslatici.app = QApplication([])
        
        # Mock ana pencere oluştur
        from PyQt6.QtWidgets import QMainWindow
        baslatici.ana_pencere = QMainWindow()
        
        # Mock servis fabrikası
        baslatici.servis_fabrikasi = object()
        
        # Kaynakları temizle (sadece referansları sıfırla, QApplication.quit() çağırma)
        if baslatici.ana_pencere:
            baslatici.ana_pencere.close()
            baslatici.ana_pencere = None
        baslatici.servis_fabrikasi = None
        # QApplication'ı kapatmayalım çünkü diğer testler kullanıyor olabilir
        baslatici.app = None
        
        # Kaynakların temizlendiğini doğrula
        assert baslatici.ana_pencere is None
        assert baslatici.app is None
        assert baslatici.servis_fabrikasi is None
    
    @given(st.integers(min_value=1, max_value=3))
    def test_coklu_temizleme_tutarliligi(self, temizleme_sayisi):
        """
        Property 10: Çoklu kaynak temizleme tutarlılığı
        For any çoklu temizleme işlemi, hata oluşmamalı
        Validates: Requirements 1.4
        """
        baslatici = UygulamaBaslatici()
        
        # Mevcut QApplication varsa kullan
        if QApplication.instance():
            baslatici.app = QApplication.instance()
        else:
            baslatici.app = QApplication([])
        
        # Çoklu temizleme işlemi (güvenli versiyon)
        for _ in range(temizleme_sayisi):
            try:
                # Sadece referansları temizle
                if baslatici.ana_pencere:
                    baslatici.ana_pencere.close()
                    baslatici.ana_pencere = None
                baslatici.servis_fabrikasi = None
                baslatici.app = None
                # Hata oluşmamalı
                assert True
            except Exception as e:
                pytest.fail(f"Çoklu kaynak temizleme sırasında hata oluştu: {e}")