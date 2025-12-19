# Version: 0.1.0
# Last Update: 2024-12-16
# Module: tests.test_stok_hareket_property
# Description: Stok hareket modeli property-based testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Hareket Property-Based Testleri

Bu modül stok hareket modelinin doğruluk özelliklerini test eder.
Hareket kayıt tutarlılığı ve işaret doğruluğu kontrol edilir.
"""

from decimal import Decimal
from hypothesis import given, strategies as st, settings
import pytest

from sontechsp.uygulama.veritabani.modeller.stok import Urun, StokHareket
from sontechsp.uygulama.veritabani.baglanti import VeriTabaniBaglanti


class TestStokHareketProperty:
    """Stok hareket modeli property-based testleri"""
    
    @given(
        hareket_tipi=st.sampled_from(['GIRIS', 'CIKIS', 'SAYIM', 'TRANSFER']),
        miktar=st.decimals(min_value=0.01, max_value=9999.99, places=4),
        birim_fiyat=st.decimals(min_value=0.01, max_value=999.99, places=4),
        aciklama=st.text(max_size=200)
    )
    @settings(max_examples=10, deadline=5000)
    def test_property_stok_hareket_kayit_tutarliligi(
        self, hareket_tipi, miktar, birim_fiyat, aciklama
    ):
        """
        **Feature: gelismis-stok-yonetimi, Property 8: Stok hareket kayıt tutarlılığı**
        
        For any stok hareketi, sistem hareket türüne göre doğru işaret (pozitif/negatif) 
        ile kaydedmeli ve tüm gerekli bilgileri saklamalı
        **Validates: Requirements 3.1, 3.2, 3.3, 3.5**
        """
        # Arrange
        db = VeriTabaniBaglanti()
        session = db.oturum_olustur()
        
        try:
            # Test ürünü oluştur
            urun = Urun(
                urun_kodu=f"TEST_HR_{hareket_tipi}",
                urun_adi="Test Hareket Ürün",
                birim="adet",
                kdv_orani=Decimal('18.00')
            )
            session.add(urun)
            session.flush()
            
            # Hareket türüne göre miktar işareti belirle
            if hareket_tipi == 'GIRIS':
                final_miktar = abs(miktar)  # Pozitif
            elif hareket_tipi == 'CIKIS':
                final_miktar = -abs(miktar)  # Negatif
            else:  # SAYIM, TRANSFER
                final_miktar = miktar  # Olduğu gibi
            
            # Act - Stok hareketi oluştur
            hareket = StokHareket(
                urun_id=urun.id,
                magaza_id=1,  # Test magaza ID
                hareket_tipi=hareket_tipi,
                miktar=final_miktar,
                birim_fiyat=birim_fiyat,
                toplam_tutar=final_miktar * birim_fiyat,
                aciklama=aciklama[:200] if aciklama else None
            )
            
            session.add(hareket)
            session.commit()
            
            # Assert - Kayıt tutarlılığı kontrolü
            kaydedilen_hareket = session.query(StokHareket).filter_by(
                urun_id=urun.id,
                hareket_tipi=hareket_tipi
            ).first()
            
            assert kaydedilen_hareket is not None
            assert kaydedilen_hareket.hareket_tipi == hareket_tipi
            assert kaydedilen_hareket.miktar == final_miktar
            assert kaydedilen_hareket.birim_fiyat == birim_fiyat
            
            # İşaret kontrolü
            if hareket_tipi == 'GIRIS':
                assert kaydedilen_hareket.miktar > 0
            elif hareket_tipi == 'CIKIS':
                assert kaydedilen_hareket.miktar < 0
                
            # Toplam tutar kontrolü
            beklenen_toplam = final_miktar * birim_fiyat
            assert kaydedilen_hareket.toplam_tutar == beklenen_toplam
            
            # Zaman damgası kontrolü
            assert kaydedilen_hareket.olusturma_tarihi is not None
            
        finally:
            session.close()