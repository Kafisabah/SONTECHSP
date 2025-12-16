# Version: 0.1.0
# Last Update: 2024-12-16
# Module: tests.test_negatif_stok_property
# Description: SONTECHSP negatif stok kontrol property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Negatif Stok Kontrol Property Testleri

Bu modül negatif stok kontrol kuralları için property-based testleri içerir.
Hypothesis kütüphanesi kullanılarak yazılmıştır.
"""

import pytest
from decimal import Decimal
from hypothesis import given, strategies as st, settings, assume

from sontechsp.uygulama.moduller.stok.servisler.negatif_stok_kontrol import NegatifStokKontrol
from sontechsp.uygulama.moduller.stok.hatalar.stok_hatalari import NegatifStokError


class TestNegatifStokKontrolProperty:
    """Negatif stok kontrol kuralları property testleri"""
    
    @given(
        mevcut_stok=st.decimals(min_value=Decimal('-10'), max_value=Decimal('100'), places=4),
        talep_miktar=st.decimals(min_value=Decimal('0.0001'), max_value=Decimal('50'), places=4)
    )
    @settings(max_examples=10, deadline=5000)
    def test_property_negatif_stok_kontrol_kurallari(self, mevcut_stok, talep_miktar):
        """
        **Feature: gelismis-stok-yonetimi, Property 10: Negatif stok kontrol kuralları**
        
        For any stock level and demand quantity, negative stock control should follow business rules:
        - 0: warning only
        - -1 to -5: warning + allow
        - < -5: block operation
        """
        kontrol = NegatifStokKontrol()
        
        # Sonuç stok seviyesini hesapla
        sonuc_stok = mevcut_stok - talep_miktar
        
        try:
            # Kontrol yap
            izin_verildi = kontrol.kontrol_yap(
                urun_id=1,
                talep_miktar=talep_miktar,
                mevcut_stok=mevcut_stok
            )
            
            # İş kurallarına göre kontrol et
            if sonuc_stok >= 0:
                # Pozitif stok - her zaman izin verilmeli
                assert izin_verildi is True, f"Pozitif stok ({sonuc_stok}) için izin verilmeliydi"
                
            elif Decimal('-5') <= sonuc_stok < 0:
                # -5 ile 0 arası - uyarı ile izin verilmeli
                assert izin_verildi is True, f"Kabul edilebilir negatif stok ({sonuc_stok}) için izin verilmeliydi"
                
            else:
                # -5'ten küçük - işlem engellenmeli
                assert izin_verildi is False, f"Aşırı negatif stok ({sonuc_stok}) için işlem engellenmeliydi"
                
        except NegatifStokError as e:
            # Hata fırlatıldıysa, bu aşırı negatif stok durumunda olmalı
            assert sonuc_stok < Decimal('-5'), f"Sadece aşırı negatif stok ({sonuc_stok}) için hata fırlatılmalı"
    
    @given(
        urun_id=st.integers(min_value=1, max_value=1000),
        ozel_limit=st.decimals(min_value=Decimal('-20'), max_value=Decimal('-1'), places=4)
    )
    @settings(max_examples=50)
    def test_property_urun_bazli_limit_yonetimi(self, urun_id, ozel_limit):
        """
        **Feature: gelismis-stok-yonetimi, Property 10: Negatif stok kontrol kuralları**
        
        For any product with custom negative stock limit, that limit should be respected
        """
        kontrol = NegatifStokKontrol()
        
        # Ürün için özel limit belirle
        kontrol.limit_belirle(urun_id, ozel_limit)
        
        # Özel limitin hemen üstünde bir talep
        mevcut_stok = Decimal('0')
        talep_miktar = abs(ozel_limit) - Decimal('0.0001')
        
        # İzin verilmeli
        izin_verildi = kontrol.kontrol_yap(urun_id, talep_miktar, mevcut_stok)
        assert izin_verildi is True, f"Özel limit ({ozel_limit}) içinde kalıyorsa izin verilmeli"
        
        # Özel limitin altında bir talep
        talep_miktar = abs(ozel_limit) + Decimal('0.0001')
        
        # İzin verilmemeli
        izin_verildi = kontrol.kontrol_yap(urun_id, talep_miktar, mevcut_stok)
        assert izin_verildi is False, f"Özel limit ({ozel_limit}) aşılıyorsa işlem engellenmeli"
    
    @given(
        mevcut_stok=st.decimals(min_value=Decimal('0'), max_value=Decimal('100'), places=4),
        talep_miktar=st.decimals(min_value=Decimal('0.0001'), max_value=Decimal('10'), places=4)
    )
    @settings(max_examples=50)
    def test_property_pozitif_stok_her_zaman_izin(self, mevcut_stok, talep_miktar):
        """
        **Feature: gelismis-stok-yonetimi, Property 10: Negatif stok kontrol kuralları**
        
        For any positive resulting stock level, operation should always be allowed
        """
        # Sadece pozitif sonuç verecek durumları test et
        assume(mevcut_stok >= talep_miktar)
        
        kontrol = NegatifStokKontrol()
        
        izin_verildi = kontrol.kontrol_yap(
            urun_id=1,
            talep_miktar=talep_miktar,
            mevcut_stok=mevcut_stok
        )
        
        sonuc_stok = mevcut_stok - talep_miktar
        assert izin_verildi is True, f"Pozitif sonuç stok ({sonuc_stok}) için her zaman izin verilmeli"
    
    @given(
        talep_miktar=st.decimals(min_value=Decimal('10'), max_value=Decimal('50'), places=4)
    )
    @settings(max_examples=50)
    def test_property_asiri_negatif_stok_engelleme(self, talep_miktar):
        """
        **Feature: gelismis-stok-yonetimi, Property 10: Negatif stok kontrol kuralları**
        
        For any demand that would result in stock below -5, operation should be blocked
        """
        kontrol = NegatifStokKontrol()
        mevcut_stok = Decimal('0')  # Sıfır stoktan başla
        
        # -5'ten daha negatif sonuç verecek talep
        assume(talep_miktar > Decimal('5'))
        
        izin_verildi = kontrol.kontrol_yap(
            urun_id=1,
            talep_miktar=talep_miktar,
            mevcut_stok=mevcut_stok
        )
        
        sonuc_stok = mevcut_stok - talep_miktar
        assert izin_verildi is False, f"Aşırı negatif stok ({sonuc_stok}) için işlem engellenmeliydi"
    
    @given(
        urun_id=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=30)
    def test_property_varsayilan_limit_tutarliligi(self, urun_id):
        """
        **Feature: gelismis-stok-yonetimi, Property 10: Negatif stok kontrol kuralları**
        
        For any product without custom limit, default limit (-5) should be used consistently
        """
        kontrol = NegatifStokKontrol()
        
        # Varsayılan limitin tam sınırında test
        mevcut_stok = Decimal('0')
        talep_miktar = Decimal('5')  # Sonuç: -5 (limit)
        
        izin_verildi = kontrol.kontrol_yap(urun_id, talep_miktar, mevcut_stok)
        assert izin_verildi is True, "Varsayılan limit (-5) sınırında izin verilmeli"
        
        # Varsayılan limitin altında test
        talep_miktar = Decimal('5.0001')  # Sonuç: -5.0001 (limit aşımı)
        
        izin_verildi = kontrol.kontrol_yap(urun_id, talep_miktar, mevcut_stok)
        assert izin_verildi is False, "Varsayılan limit (-5) aşımında işlem engellenmeli"