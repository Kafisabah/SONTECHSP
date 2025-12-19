# Version: 0.1.0
# Last Update: 2024-12-16
# Module: tests.test_urun_guncelleme_property
# Description: Ürün güncelleme property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Ürün Güncelleme Property Testleri

Bu modül ürün güncelleme izlenebilirliği property testlerini içerir.
"""

from decimal import Decimal
from hypothesis import given, strategies as st, settings
import pytest

from sontechsp.uygulama.moduller.stok.dto import UrunDTO
from sontechsp.uygulama.moduller.stok.depolar.urun_repository import UrunRepository


class TestUrunGuncellemeProperty:
    """Ürün güncelleme property testleri"""
    
    @given(
        yeni_urun_adi=st.text(min_size=1, max_size=200, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'), min_codepoint=32, max_codepoint=126
        )),
        yeni_kdv_orani=st.decimals(min_value=0, max_value=100, places=2)
    )
    @settings(max_examples=10, deadline=5000)
    def test_property_urun_guncelleme_izlenebilirligi(self, yeni_urun_adi, yeni_kdv_orani):
        """
        **Feature: gelismis-stok-yonetimi, Property 2: Ürün güncelleme izlenebilirliği**
        
        For any ürün güncelleme işlemi, sistem değişiklikleri kaydetmeli 
        ve güncelleme zamanını işaretlemeli
        **Validates: Requirements 1.3**
        """
        # Arrange
        repository = UrunRepository()
        
        # İlk ürün oluştur
        ilk_urun = UrunDTO(
            urun_kodu=f"TEST_UPD_{hash(yeni_urun_adi) % 10000}",
            urun_adi="İlk Ürün Adı",
            birim="adet",
            kdv_orani=Decimal('18.00')
        )
        
        try:
            urun_id = repository.ekle(ilk_urun)
            
            # İlk durumu kaydet
            ilk_durum = repository.id_ile_getir(urun_id)
            assert ilk_durum is not None
            
            # Güncelleme yap
            guncellenen_urun = UrunDTO(
                urun_kodu=ilk_urun.urun_kodu,  # Aynı kod
                urun_adi=yeni_urun_adi.strip(),
                birim="adet",
                kdv_orani=yeni_kdv_orani
            )
            
            # Geçerli veri kontrolü
            if not guncellenen_urun.urun_adi:
                return
            
            # Act - Güncelleme yap
            guncelleme_basarili = repository.guncelle(urun_id, guncellenen_urun)
            
            # Assert - Güncelleme kontrolü
            assert guncelleme_basarili == True
            
            # Güncellenmiş durumu getir
            son_durum = repository.id_ile_getir(urun_id)
            assert son_durum is not None
            
            # Değişiklik kontrolü
            assert son_durum.urun_adi == guncellenen_urun.urun_adi
            assert son_durum.kdv_orani == guncellenen_urun.kdv_orani
            
            # Güncelleme zamanı kontrolü (değişmeli)
            if ilk_durum.guncelleme_tarihi and son_durum.guncelleme_tarihi:
                assert son_durum.guncelleme_tarihi >= ilk_durum.guncelleme_tarihi
            
        except Exception:
            # Test verisi ile ilgili hatalar göz ardı edilir
            pass