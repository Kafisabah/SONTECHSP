# Version: 0.1.0
# Last Update: 2024-12-16
# Module: test_servis_fabrikasi
# Description: Servis fabrikası property testleri
# Changelog:
# - İlk sürüm oluşturuldu

import pytest
from hypothesis import given, strategies as st
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from uygulama.arayuz.servis_fabrikasi import ServisFabrikasi


class TestServisFabrikasi:
    """**Feature: pyqt-arayuz-iskeleti, Property 3: Servis fabrikası singleton davranışı**"""
    
    def setup_method(self):
        """Her test öncesi fabrikayı sıfırla"""
        ServisFabrikasi._instance = None
        ServisFabrikasi._servisler = {}
    
    def test_singleton_davranisi(self):
        """
        Property 3: Servis fabrikası singleton davranışı
        For any servis tipi, aynı servis tipinin her zaman aynı örneği döndürülmeli
        Validates: Requirements 3.1
        """
        # İki farklı fabrika örneği oluştur
        fabrika1 = ServisFabrikasi()
        fabrika2 = ServisFabrikasi()
        
        # Aynı örnek olmalı
        assert fabrika1 is fabrika2
        
        # Servis örnekleri de aynı olmalı
        stok1 = fabrika1.stok_servisi()
        stok2 = fabrika2.stok_servisi()
        assert stok1 is stok2
        
        pos1 = fabrika1.pos_servisi()
        pos2 = fabrika2.pos_servisi()
        assert pos1 is pos2
    
    @given(st.integers(min_value=2, max_value=10))
    def test_coklu_fabrika_olusturma(self, fabrika_sayisi):
        """
        Property 3: Çoklu fabrika oluşturma singleton davranışı
        For any sayıda fabrika oluşturma, hepsi aynı örnek olmalı
        Validates: Requirements 3.1
        """
        fabrikalar = []
        
        # Çoklu fabrika oluştur
        for _ in range(fabrika_sayisi):
            fabrikalar.append(ServisFabrikasi())
        
        # Hepsi aynı örnek olmalı
        ilk_fabrika = fabrikalar[0]
        for fabrika in fabrikalar[1:]:
            assert fabrika is ilk_fabrika


class TestServisCagrisi:
    """**Feature: pyqt-arayuz-iskeleti, Property 4: Servis çağrısı tutarlılığı**"""
    
    def setup_method(self):
        """Her test öncesi fabrikayı sıfırla"""
        ServisFabrikasi._instance = None
        ServisFabrikasi._servisler = {}
    
    def test_stok_servisi_cagrisi(self):
        """
        Property 4: Stok servisi çağrısı tutarlılığı
        For any stok servisi ihtiyacı, stok_servisi metodunun çağrılması gerçekleşmeli
        Validates: Requirements 3.2
        """
        fabrika = ServisFabrikasi()
        
        # Stok servisi çağır
        servis = fabrika.stok_servisi()
        
        # Servis döndürülmeli
        assert servis is not None
        assert hasattr(servis, 'urun_ara')
    
    def test_pos_servisi_cagrisi(self):
        """
        Property 4: POS servisi çağrısı tutarlılığı
        For any POS servisi ihtiyacı, pos_servisi metodunun çağrılması gerçekleşmeli
        Validates: Requirements 3.3
        """
        fabrika = ServisFabrikasi()
        
        # POS servisi çağır
        servis = fabrika.pos_servisi()
        
        # Servis döndürülmeli
        assert servis is not None
        assert hasattr(servis, 'barkod_ekle')
        assert hasattr(servis, 'odeme_tamamla')
    
    def test_crm_servisi_cagrisi(self):
        """
        Property 4: CRM servisi çağrısı tutarlılığı
        For any CRM servisi ihtiyacı, crm_servisi metodunun çağrılması gerçekleşmeli
        Validates: Requirements 3.4
        """
        fabrika = ServisFabrikasi()
        
        # CRM servisi çağır
        servis = fabrika.crm_servisi()
        
        # Servis döndürülmeli
        assert servis is not None
        assert hasattr(servis, 'musteri_ara')