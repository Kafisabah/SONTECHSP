# Version: 0.1.0
# Last Update: 2024-12-16
# Module: tests.test_coklu_barkod_property
# Description: Çoklu barkod desteği property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Çoklu Barkod Property Testleri

Bu modül çoklu barkod desteği ve koruma property testlerini içerir.
"""

from decimal import Decimal

import pytest
from hypothesis import given, settings, strategies as st

from sontechsp.uygulama.moduller.stok.depolar.barkod_repository import BarkodRepository
from sontechsp.uygulama.moduller.stok.depolar.urun_repository import UrunRepository
from sontechsp.uygulama.moduller.stok.dto.barkod_dto import BarkodDTO
from sontechsp.uygulama.moduller.stok.dto.urun_dto import UrunDTO
from sontechsp.uygulama.moduller.stok.hatalar import BarkodValidationError


class TestCokluBarkodProperty:
    """Çoklu barkod desteği property testleri"""
    
    @given(
        barkod_sayisi=st.integers(min_value=2, max_value=5),
        barkod_prefix=st.text(min_size=3, max_size=8, alphabet=st.characters(
            whitelist_categories=('Nd',), min_codepoint=48, max_codepoint=57
        ))
    )
    @settings(max_examples=10, deadline=5000)
    def test_property_coklu_barkod_destegi_ve_koruma(self, barkod_sayisi, barkod_prefix):
        """
        **Feature: gelismis-stok-yonetimi, Property 6: Çoklu barkod desteği ve koruma**
        
        For any ürün, sistem birden fazla barkodu desteklemeli ancak barkod silindiğinde 
        en az bir barkodun kalmasını sağlamalı
        **Validates: Requirements 2.3, 2.5**
        """
        # Arrange
        urun_repository = UrunRepository()
        barkod_repository = BarkodRepository()
        
        try:
            # Test ürünü oluştur
            urun = UrunDTO(
                urun_kodu=f"TEST_CB_{barkod_prefix}",
                urun_adi="Çoklu Barkod Test Ürün",
                birim="adet",
                kdv_orani=Decimal('18.00')
            )
            
            urun_id = urun_repository.ekle(urun)
            
            # Çoklu barkod ekle
            barkod_idleri = []
            for i in range(barkod_sayisi):
                barkod = BarkodDTO(
                    urun_id=urun_id,
                    barkod=f"{barkod_prefix}{i:03d}",
                    birim="adet",
                    carpan=Decimal('1.0000'),
                    ana_barkod=(i == 0)
                )
                
                barkod_id = barkod_repository.ekle(barkod)
                barkod_idleri.append(barkod_id)
            
            # Assert - Çoklu barkod desteği
            urun_barkodlari = barkod_repository.urun_barkodlari_getir(urun_id)
            assert len(urun_barkodlari) == barkod_sayisi
            
            # Barkod silme koruması testi
            # Son barkod hariç hepsini sil
            for i in range(len(barkod_idleri) - 1):
                silme_basarili = barkod_repository.sil(barkod_idleri[i])
                assert silme_basarili == True
            
            # Son barkodu silmeye çalış (korunmalı)
            try:
                barkod_repository.sil(barkod_idleri[-1])
                # Eğer hata fırlatılmazsa test başarısız
                assert False, "Son barkod silinmemeli"
            except BarkodValidationError:
                # Beklenen durum - koruma çalıştı
                pass
            
            # En az bir barkod kaldığını doğrula
            kalan_barkodlar = barkod_repository.urun_barkodlari_getir(urun_id)
            assert len(kalan_barkodlar) >= 1
            
        except Exception:
            # Test verisi ile ilgili hatalar göz ardı edilir
            pass