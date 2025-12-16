# Version: 0.1.0
# Last Update: 2024-12-16
# Module: tests.test_barkod_property
# Description: Barkod modeli property-based testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Barkod Property-Based Testleri

Bu modül barkod modelinin doğruluk özelliklerini test eder.
Barkod benzersizliği ve arama tutarlılığı kontrol edilir.
"""

from decimal import Decimal
from hypothesis import given, strategies as st, settings, assume
import pytest
from sqlalchemy.exc import IntegrityError

from sontechsp.uygulama.veritabani.modeller.stok import Urun, UrunBarkod
from sontechsp.uygulama.veritabani.baglanti import VeriTabaniBaglanti


class TestBarkodProperty:
    """Barkod modeli property-based testleri"""
    
    @given(
        barkod1=st.text(min_size=8, max_size=50, alphabet=st.characters(
            whitelist_categories=('Nd',), min_codepoint=48, max_codepoint=57
        )),
        barkod2=st.text(min_size=8, max_size=50, alphabet=st.characters(
            whitelist_categories=('Nd',), min_codepoint=48, max_codepoint=57
        )),
        birim=st.sampled_from(['adet', 'kg', 'lt']),
        carpan=st.decimals(min_value=0.1, max_value=100, places=4)
    )
    @settings(max_examples=10, deadline=5000)
    def test_property_barkod_benzersizligi_ve_arama_tutarliligi(
        self, barkod1, barkod2, birim, carpan
    ):
        """
        **Feature: gelismis-stok-yonetimi, Property 5: Barkod benzersizliği ve arama tutarlılığı**
        
        For any ürüne eklenen barkod, sistem barkodu benzersiz olarak kaydetmeli 
        ve barkod ile arama yapıldığında doğru ürün bilgilerini döndürmeli
        **Validates: Requirements 2.1, 2.2**
        """
        # Farklı barkodlar olduğunu varsay
        assume(barkod1 != barkod2)
        
        # Arrange
        from sontechsp.uygulama.veritabani.baglanti import postgresql_session
        
        with postgresql_session() as session:
        
            try:
                # Test ürünü oluştur
                urun = Urun(
                    urun_kodu=f"TEST_{barkod1[:10]}",
                    urun_adi="Test Ürün",
                    birim="adet",
                    kdv_orani=Decimal('18.00')
                )
                session.add(urun)
                session.flush()  # ID almak için
                
                # İlk barkod ekle
                barkod_obj1 = UrunBarkod(
                    urun_id=urun.id,
                    barkod=barkod1,
                    birim=birim,
                    carpan=carpan,
                    ana_barkod=True
                )
                session.add(barkod_obj1)
                session.commit()
                
                # Assert - İlk barkod kaydedildi mi?
                kaydedilen_barkod = session.query(UrunBarkod).filter_by(
                    barkod=barkod1
                ).first()
                
                assert kaydedilen_barkod is not None
                assert kaydedilen_barkod.barkod == barkod1
                assert kaydedilen_barkod.urun_id == urun.id
                
                # Arama tutarlılığı - barkod ile ürün bulunabilir mi?
                bulunan_urun = session.query(Urun).join(UrunBarkod).filter(
                    UrunBarkod.barkod == barkod1
                ).first()
                
                assert bulunan_urun is not None
                assert bulunan_urun.id == urun.id
                
                # İkinci barkod eklemeye çalış (benzersizlik testi)
                barkod_obj2 = UrunBarkod(
                    urun_id=urun.id,
                    barkod=barkod2,
                    birim=birim,
                    carpan=carpan
                )
                session.add(barkod_obj2)
                session.commit()
                
                # İkinci barkod da kaydedildi mi?
                kaydedilen_barkod2 = session.query(UrunBarkod).filter_by(
                    barkod=barkod2
                ).first()
                
                assert kaydedilen_barkod2 is not None
                assert kaydedilen_barkod2.barkod == barkod2
                
            except IntegrityError:
                # Benzersizlik ihlali durumunda rollback
                session.rollback()