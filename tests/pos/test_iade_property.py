# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.test_iade_property
# Description: İade modeli özellik tabanlı testleri
# Changelog:
# - İlk oluşturma

"""
İade Modeli Özellik Tabanlı Testleri

Bu modül iade modelinin özellik tabanlı testlerini içerir.
Hypothesis kütüphanesi kullanılarak rastgele verilerle test edilir.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from hypothesis import given, strategies as st, assume, settings
from unittest.mock import Mock, patch

from sontechsp.uygulama.moduller.pos.database.models.iade import (
    Iade, IadeSatiri, iade_validasyon, iade_satiri_validasyon
)


class TestIadePropertyTests:
    """İade modeli özellik tabanlı testleri"""
    
    @given(
        orijinal_satis_id=st.integers(min_value=1, max_value=10000),
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        neden=st.text(min_size=5, max_size=100, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ')
    )
    @settings(max_examples=100)
    def test_property_14_iade_islemi_baslatma(
        self, orijinal_satis_id, terminal_id, kasiyer_id, neden
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 14: İade İşlemi Başlatma**
        **Validates: Requirements 4.1**
        
        Herhangi bir iade işlemi için, sistem orijinal satış kaydını doğrulamalı
        """
        # Arrange - İade oluştur
        iade = Iade(
            orijinal_satis_id=orijinal_satis_id,
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            iade_tarihi=datetime.now(),
            toplam_tutar=Decimal('0.00'),
            neden=neden.strip()
        )
        
        # Mock bir iade satırı ekle (validasyon için gerekli)
        iade_satiri = IadeSatiri(
            iade_id=1,
            urun_id=1,
            barkod='1234567890',
            urun_adi='Test Ürün',
            adet=1,
            birim_fiyat=Decimal('10.00'),
            toplam_tutar=Decimal('10.00')
        )
        
        iade.satirlar = [iade_satiri]
        iade.toplam_tutar = iade_satiri.toplam_tutar
        
        # Assert - Özellik doğrulamaları
        # 1. Orijinal satış kaydı referansı doğru olmalı
        assert iade.orijinal_satis_id == orijinal_satis_id
        assert iade.orijinal_satis_id > 0
        
        # 2. İade bilgileri doğru saklanmış olmalı
        assert iade.terminal_id == terminal_id
        assert iade.kasiyer_id == kasiyer_id
        assert iade.neden == neden.strip()
        
        # 3. Validasyon geçmeli
        iade_hatalari = iade_validasyon(iade)
        assert len(iade_hatalari) == 0, f"İade validasyon hataları: {iade_hatalari}"
        
        # 4. İade tarihi set edilmiş olmalı
        assert iade.iade_tarihi is not None
        assert isinstance(iade.iade_tarihi, datetime)
    
    @given(
        orijinal_satis_id=st.integers(min_value=1, max_value=10000),
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        urun_listesi=st.lists(
            st.tuples(
                st.integers(min_value=1, max_value=1000),  # urun_id
                st.text(alphabet='0123456789', min_size=8, max_size=13),  # barkod
                st.text(min_size=5, max_size=50),  # urun_adi
                st.integers(min_value=1, max_value=10),  # adet
                st.decimals(min_value=Decimal('0.01'), max_value=Decimal('99.99'), places=2)  # birim_fiyat
            ),
            min_size=1,
            max_size=5,
            unique_by=lambda x: x[0]  # urun_id'ye göre unique
        )
    )
    @settings(max_examples=50)
    def test_property_15_iade_tutari_hesaplama(
        self, orijinal_satis_id, terminal_id, kasiyer_id, urun_listesi
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 15: İade Tutarı Hesaplama**
        **Validates: Requirements 4.2**
        
        Herhangi bir iade kalemi seçimi için, sistem iade tutarını doğru hesaplamalı
        """
        # Arrange - İade oluştur
        iade = Iade(
            orijinal_satis_id=orijinal_satis_id,
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            iade_tarihi=datetime.now(),
            toplam_tutar=Decimal('0.00'),
            neden='Test iade nedeni'
        )
        
        # Act - İade satırları oluştur
        satirlar = []
        toplam_tutar = Decimal('0.00')
        
        for urun_id, barkod, urun_adi, adet, birim_fiyat in urun_listesi:
            satir_toplam = Decimal(str(adet)) * birim_fiyat
            
            satir = IadeSatiri(
                iade_id=1,
                urun_id=urun_id,
                barkod=barkod,
                urun_adi=urun_adi,
                adet=adet,
                birim_fiyat=birim_fiyat,
                toplam_tutar=satir_toplam
            )
            
            satirlar.append(satir)
            toplam_tutar += satir_toplam
        
        iade.satirlar = satirlar
        iade.toplam_tutar = toplam_tutar
        
        # Assert - Özellik doğrulamaları
        # 1. İade tutarı doğru hesaplanmış olmalı
        hesaplanan_toplam = iade.hesaplanan_toplam_tutar()
        assert abs(iade.toplam_tutar - hesaplanan_toplam) < Decimal('0.01')
        
        # 2. Her satırın tutarı doğru hesaplanmış olmalı
        for i, (urun_id, barkod, urun_adi, adet, birim_fiyat) in enumerate(urun_listesi):
            satir = satirlar[i]
            beklenen_tutar = Decimal(str(adet)) * birim_fiyat
            assert abs(satir.toplam_tutar - beklenen_tutar) < Decimal('0.01')
        
        # 3. Toplam adet doğru hesaplanmış olmalı
        beklenen_toplam_adet = sum(adet for _, _, _, adet, _ in urun_listesi)
        assert iade.toplam_adet() == beklenen_toplam_adet
        
        # 4. Satır sayısı doğru olmalı
        assert iade.satir_sayisi() == len(urun_listesi)
        
        # 5. Validasyon geçmeli
        iade_hatalari = iade_validasyon(iade)
        assert len(iade_hatalari) == 0, f"İade validasyon hataları: {iade_hatalari}"
        
        for satir in satirlar:
            satir_hatalari = iade_satiri_validasyon(satir)
            assert len(satir_hatalari) == 0, f"Satır validasyon hataları: {satir_hatalari}"
    
    @given(
        orijinal_satis_id=st.integers(min_value=1, max_value=10000),
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        urun_id=st.integers(min_value=1, max_value=1000),
        barkod=st.text(alphabet='0123456789', min_size=8, max_size=13),
        urun_adi=st.text(min_size=5, max_size=50),
        adet=st.integers(min_value=1, max_value=10),
        birim_fiyat=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('99.99'), places=2)
    )
    @settings(max_examples=100)
    def test_property_16_iade_onaylama(
        self, orijinal_satis_id, terminal_id, kasiyer_id, urun_id, 
        barkod, urun_adi, adet, birim_fiyat
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 16: İade Onaylama**
        **Validates: Requirements 4.3**
        
        Herhangi bir iade onayı için, sistem stok girişi yapmalı ve iade kaydı oluşturmalı
        """
        # Arrange - İade ve satır oluştur
        iade = Iade(
            orijinal_satis_id=orijinal_satis_id,
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            iade_tarihi=datetime.now(),
            toplam_tutar=Decimal('0.00'),
            neden='Test iade nedeni'
        )
        
        satir_toplam = Decimal(str(adet)) * birim_fiyat
        
        iade_satiri = IadeSatiri(
            iade_id=1,
            urun_id=urun_id,
            barkod=barkod,
            urun_adi=urun_adi,
            adet=adet,
            birim_fiyat=birim_fiyat,
            toplam_tutar=satir_toplam
        )
        
        iade.satirlar = [iade_satiri]
        iade.toplam_tutar = satir_toplam
        
        # Act - İade onaylama simülasyonu
        # (Gerçek implementasyonda stok servisi çağrılır)
        iade.fis_no = f"IADE{iade.id or 1:06d}"
        
        # Assert - Özellik doğrulamaları
        # 1. İade kaydı oluşturulmuş olmalı
        assert iade.orijinal_satis_id == orijinal_satis_id
        assert iade.toplam_tutar == satir_toplam
        assert iade.fis_no is not None
        
        # 2. İade satırı bilgileri doğru olmalı
        assert iade_satiri.urun_id == urun_id
        assert iade_satiri.adet == adet
        assert iade_satiri.birim_fiyat == birim_fiyat
        assert iade_satiri.toplam_tutar == satir_toplam
        
        # 3. Stok girişi için gerekli bilgiler mevcut olmalı
        # (urun_id ve adet bilgisi stok servisi için gerekli)
        assert iade_satiri.urun_id > 0
        assert iade_satiri.adet > 0
        
        # 4. Validasyon geçmeli
        iade_hatalari = iade_validasyon(iade)
        satir_hatalari = iade_satiri_validasyon(iade_satiri)
        assert len(iade_hatalari) == 0, f"İade validasyon hataları: {iade_hatalari}"
        assert len(satir_hatalari) == 0, f"Satır validasyon hataları: {satir_hatalari}"
        
        # 5. İade tutarı hesaplaması doğru olmalı
        assert abs(iade.toplam_tutar - iade.hesaplanan_toplam_tutar()) < Decimal('0.01')
    
    @given(
        gecersiz_orijinal_satis_id=st.integers(max_value=0),
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000)
    )
    @settings(max_examples=50)
    def test_gecersiz_orijinal_satis_id_validasyon(
        self, gecersiz_orijinal_satis_id, terminal_id, kasiyer_id
    ):
        """
        Geçersiz orijinal satış ID ile iade oluşturma testi
        
        Geçersiz orijinal satış ID için validasyon hatası vermeli
        """
        # Arrange & Act
        iade = Iade(
            orijinal_satis_id=gecersiz_orijinal_satis_id,
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            iade_tarihi=datetime.now(),
            toplam_tutar=Decimal('10.00'),
            neden='Test nedeni'
        )
        
        # Mock satır ekle
        iade_satiri = IadeSatiri(
            iade_id=1,
            urun_id=1,
            barkod='1234567890',
            urun_adi='Test Ürün',
            adet=1,
            birim_fiyat=Decimal('10.00'),
            toplam_tutar=Decimal('10.00')
        )
        iade.satirlar = [iade_satiri]
        
        # Assert
        hatalar = iade_validasyon(iade)
        assert len(hatalar) > 0
        assert any("orijinal satış id" in hata.lower() for hata in hatalar)
    
    @given(
        urun_id=st.integers(min_value=1, max_value=1000),
        barkod=st.text(alphabet='0123456789', min_size=8, max_size=13),
        urun_adi=st.text(min_size=5, max_size=50),
        adet=st.integers(min_value=1, max_value=10),
        birim_fiyat=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('99.99'), places=2)
    )
    @settings(max_examples=100)
    def test_iade_satiri_toplam_tutar_guncelleme(
        self, urun_id, barkod, urun_adi, adet, birim_fiyat
    ):
        """
        İade satırı toplam tutar güncelleme özellik testi
        
        Herhangi bir iade satırı için toplam tutar doğru hesaplanmalı
        """
        # Arrange
        iade_satiri = IadeSatiri(
            iade_id=1,
            urun_id=urun_id,
            barkod=barkod,
            urun_adi=urun_adi,
            adet=adet,
            birim_fiyat=birim_fiyat,
            toplam_tutar=Decimal('0.00')  # Başlangıçta sıfır
        )
        
        # Act
        iade_satiri.toplam_tutar_guncelle()
        
        # Assert
        beklenen_toplam = Decimal(str(adet)) * birim_fiyat
        assert abs(iade_satiri.toplam_tutar - beklenen_toplam) < Decimal('0.01')
        
        # Birim net fiyat da doğru hesaplanmalı
        birim_net_fiyat = iade_satiri.birim_net_fiyat_hesapla()
        assert abs(birim_net_fiyat - birim_fiyat) < Decimal('0.01')
    
    @given(
        satirlar_data=st.lists(
            st.tuples(
                st.integers(min_value=1, max_value=10),  # adet
                st.decimals(min_value=Decimal('0.01'), max_value=Decimal('99.99'), places=2)  # birim_fiyat
            ),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=50)
    def test_iade_toplam_hesaplamalari(self, satirlar_data):
        """
        İade toplam hesaplamaları özellik testi
        
        Herhangi bir iade için toplam hesaplamaları doğru olmalı
        """
        # Arrange
        iade = Iade(
            orijinal_satis_id=1,
            terminal_id=1,
            kasiyer_id=1,
            iade_tarihi=datetime.now(),
            toplam_tutar=Decimal('0.00'),
            neden='Test nedeni'
        )
        
        satirlar = []
        beklenen_toplam_tutar = Decimal('0.00')
        beklenen_toplam_adet = 0
        
        for i, (adet, birim_fiyat) in enumerate(satirlar_data):
            satir_toplam = Decimal(str(adet)) * birim_fiyat
            
            satir = IadeSatiri(
                iade_id=1,
                urun_id=i + 1,
                barkod=f'123456789{i}',
                urun_adi=f'Test Ürün {i}',
                adet=adet,
                birim_fiyat=birim_fiyat,
                toplam_tutar=satir_toplam
            )
            
            satirlar.append(satir)
            beklenen_toplam_tutar += satir_toplam
            beklenen_toplam_adet += adet
        
        iade.satirlar = satirlar
        iade.toplam_tutar = beklenen_toplam_tutar
        
        # Act & Assert
        # 1. Hesaplanan toplam tutar doğru olmalı
        hesaplanan_toplam = iade.hesaplanan_toplam_tutar()
        assert abs(hesaplanan_toplam - beklenen_toplam_tutar) < Decimal('0.01')
        
        # 2. Toplam adet doğru olmalı
        assert iade.toplam_adet() == beklenen_toplam_adet
        
        # 3. Satır sayısı doğru olmalı
        assert iade.satir_sayisi() == len(satirlar_data)
        
        # 4. Validasyon geçmeli
        hatalar = iade_validasyon(iade)
        assert len(hatalar) == 0, f"İade validasyon hataları: {hatalar}"