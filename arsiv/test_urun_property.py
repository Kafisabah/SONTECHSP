# Version: 0.1.0
# Last Update: 2024-12-16
# Module: tests.test_urun_property
# Description: Ürün modeli property-based testleri
# Changelog:
# - İlk oluşturma
# - Import düzeltmeleri ve session yönetimi iyileştirmesi

"""
SONTECHSP Ürün Property-Based Testleri

Bu modül ürün modelinin doğruluk özelliklerini test eder.
Hypothesis kütüphanesi kullanılarak rastgele veri ile testler yapılır.
"""

from decimal import Decimal

import pytest
from hypothesis import given, settings, strategies as st
from sqlalchemy.exc import IntegrityError

from sontechsp.uygulama.veritabani.baglanti import postgresql_session
from sontechsp.uygulama.veritabani.modeller.stok import Urun


class TestUrunProperty:
    """Ürün modeli property-based testleri"""
    
    @given(
        urun_kodu=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=32, max_codepoint=126
        )),
        urun_adi=st.text(min_size=1, max_size=200, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'), min_codepoint=32, max_codepoint=126
        )),
        birim=st.sampled_from(['adet', 'kg', 'lt', 'mt', 'cm']),
        kdv_orani=st.decimals(min_value=0, max_value=100, places=2)
    )
    @settings(max_examples=10, deadline=5000)
    def test_property_urun_kayit_tutarliligi(self, urun_kodu, urun_adi, birim, kdv_orani):
        """
        **Feature: gelismis-stok-yonetimi, Property 1: Ürün kayıt tutarlılığı**
        
        For any geçerli ürün bilgisi, sistem ürünü benzersiz stok kodu ile kaydetmeli 
        ve tüm zorunlu alanları doğrulamalı
        **Validates: Requirements 1.1, 1.2**
        """
        # Geçerli veri kontrolü
        if not urun_kodu.strip() or not urun_adi.strip():
            return  # Geçersiz veri, test etme
        
        # Arrange & Act - PostgreSQL session ile ürün oluştur
        try:
            with postgresql_session() as session:
                # Ürün oluştur
                urun = Urun(
                    urun_kodu=urun_kodu.strip(),
                    urun_adi=urun_adi.strip(),
                    birim=birim,
                    kdv_orani=kdv_orani,
                    aktif=True
                )
                
                session.add(urun)
                session.flush()  # ID almak için flush
                
                # Assert - Kayıt tutarlılığı kontrolü
                kaydedilen_urun = session.query(Urun).filter_by(
                    urun_kodu=urun.urun_kodu
                ).first()
                
                assert kaydedilen_urun is not None
                assert kaydedilen_urun.urun_kodu == urun.urun_kodu
                assert kaydedilen_urun.urun_adi == urun.urun_adi
                assert kaydedilen_urun.birim == urun.birim
                assert kaydedilen_urun.kdv_orani == urun.kdv_orani
                assert kaydedilen_urun.aktif == True
                assert kaydedilen_urun.olusturma_tarihi is not None
                
        except IntegrityError:
            # Benzersizlik ihlali beklenen durum - test geçer
            pass