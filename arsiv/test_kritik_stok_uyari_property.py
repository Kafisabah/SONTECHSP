# Version: 0.1.0
# Last Update: 2024-12-16
# Module: tests.test_kritik_stok_uyari_property
# Description: SONTECHSP kritik stok uyarı sistemi property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Kritik Stok Uyarı Sistemi Property Testleri

Bu modül kritik stok uyarı sistemi için property-based testleri içerir.
Hypothesis kütüphanesi kullanılarak yazılmıştır.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, MagicMock

from sontechsp.uygulama.moduller.stok.servisler.kritik_stok_service import KritikStokService, KritikStokUyari
from sontechsp.uygulama.moduller.stok.dto import StokBakiyeDTO, UrunDTO


class TestKritikStokUyariProperty:
    """Kritik stok uyarı sistemi property testleri"""
    
    def setup_method(self):
        """Test setup"""
        self.bakiye_repository = Mock()
        self.urun_repository = Mock()
        self.service = KritikStokService(self.bakiye_repository, self.urun_repository)
    
    @given(
        mevcut_stok=st.decimals(min_value=Decimal('0'), max_value=Decimal('100'), places=4),
        kritik_seviye=st.decimals(min_value=Decimal('1'), max_value=Decimal('50'), places=4)
    )
    @settings(max_examples=10, deadline=5000)
    def test_property_kritik_stok_uyari_sistemi(self, mevcut_stok, kritik_seviye):
        """
        **Feature: gelismis-stok-yonetimi, Property 17: Kritik stok uyarı sistemi**
        
        For any stock level and critical threshold, warning system should correctly categorize alerts
        """
        # Mock data hazırla
        urun = UrunDTO(
            id=1,
            urun_kodu="TEST001",
            urun_adi="Test Ürün",
            minimum_stok=kritik_seviye
        )
        
        bakiye = StokBakiyeDTO(
            id=1,
            urun_id=1,
            magaza_id=1,
            kullanilabilir_miktar=mevcut_stok,
            miktar=mevcut_stok,
            rezerve_miktar=Decimal('0')
        )
        
        # Mock repository responses
        self.bakiye_repository.tum_bakiyeler_getir.return_value = [bakiye]
        self.urun_repository.id_ile_getir.return_value = urun
        
        # Kritik stok listesini al
        kritik_stoklar = self.service.kritik_stok_listesi()
        
        # Kritik seviye kontrolü
        if mevcut_stok <= kritik_seviye:
            # Kritik stok uyarısı olmalı
            assert len(kritik_stoklar) == 1, f"Kritik seviye ({kritik_seviye}) altındaki stok ({mevcut_stok}) için uyarı oluşmalı"
            
            uyari = kritik_stoklar[0]
            assert uyari.urun_id == 1
            assert uyari.mevcut_stok == mevcut_stok
            assert uyari.kritik_seviye == kritik_seviye
            assert uyari.eksik_miktar == kritik_seviye - mevcut_stok
            
            # Uyarı seviyesi kontrolü
            if mevcut_stok <= 0:
                assert uyari.uyari_seviyesi == 'ACIL', f"Sıfır stok için ACIL uyarı olmalı"
            elif mevcut_stok <= kritik_seviye * Decimal('0.5'):
                assert uyari.uyari_seviyesi == 'KRITIK', f"Kritik seviyenin yarısı altında KRITIK uyarı olmalı"
            else:
                assert uyari.uyari_seviyesi == 'UYARI', f"Kritik seviye altında UYARI olmalı"
        else:
            # Kritik stok uyarısı olmamalı
            assert len(kritik_stoklar) == 0, f"Kritik seviye ({kritik_seviye}) üstündeki stok ({mevcut_stok}) için uyarı olmamalı"
    
    @given(
        urun_sayisi=st.integers(min_value=1, max_value=10),
        kritik_seviye=st.decimals(min_value=Decimal('5'), max_value=Decimal('20'), places=4)
    )
    @settings(max_examples=50)
    def test_property_coklu_urun_uyari_siralama(self, urun_sayisi, kritik_seviye):
        """
        **Feature: gelismis-stok-yonetimi, Property 17: Kritik stok uyarı sistemi**
        
        For multiple products with critical stock, warnings should be sorted by severity
        """
        bakiyeler = []
        urunler = []
        
        # Farklı stok seviyelerinde ürünler oluştur
        for i in range(urun_sayisi):
            # Farklı kritiklik seviyelerinde stoklar
            if i % 3 == 0:
                stok = Decimal('0')  # ACIL
            elif i % 3 == 1:
                stok = kritik_seviye * Decimal('0.3')  # KRITIK
            else:
                stok = kritik_seviye * Decimal('0.8')  # UYARI
            
            urun = UrunDTO(
                id=i+1,
                urun_kodu=f"TEST{i+1:03d}",
                urun_adi=f"Test Ürün {i+1}",
                minimum_stok=kritik_seviye
            )
            
            bakiye = StokBakiyeDTO(
                id=i+1,
                urun_id=i+1,
                magaza_id=1,
                kullanilabilir_miktar=stok,
                miktar=stok,
                rezerve_miktar=Decimal('0')
            )
            
            urunler.append(urun)
            bakiyeler.append(bakiye)
        
        # Mock repository responses
        self.bakiye_repository.tum_bakiyeler_getir.return_value = bakiyeler
        self.urun_repository.id_ile_getir.side_effect = lambda uid: next(
            (u for u in urunler if u.id == uid), None
        )
        
        # Kritik stok listesini al
        kritik_stoklar = self.service.kritik_stok_listesi()
        
        # Sıralama kontrolü - ACIL > KRITIK > UYARI
        onceki_seviye_oncelik = -1
        
        for uyari in kritik_stoklar:
            seviye_oncelik = {'ACIL': 0, 'KRITIK': 1, 'UYARI': 2}[uyari.uyari_seviyesi]
            
            assert seviye_oncelik >= onceki_seviye_oncelik, \
                f"Uyarılar seviyesine göre sıralanmalı: {[u.uyari_seviyesi for u in kritik_stoklar]}"
            
            onceki_seviye_oncelik = seviye_oncelik
    
    @given(
        magaza_sayisi=st.integers(min_value=1, max_value=5),
        kritik_seviye=st.decimals(min_value=Decimal('10'), max_value=Decimal('30'), places=4)
    )
    @settings(max_examples=30)
    def test_property_magaza_bazli_filtreleme(self, magaza_sayisi, kritik_seviye):
        """
        **Feature: gelismis-stok-yonetimi, Property 17: Kritik stok uyarı sistemi**
        
        For store-based filtering, only warnings from specified store should be returned
        """
        bakiyeler = []
        urunler = []
        
        # Her mağaza için kritik stok oluştur
        for magaza_id in range(1, magaza_sayisi + 1):
            urun = UrunDTO(
                id=magaza_id,
                urun_kodu=f"TEST{magaza_id:03d}",
                urun_adi=f"Test Ürün {magaza_id}",
                minimum_stok=kritik_seviye
            )
            
            # Kritik seviyenin altında stok
            stok = kritik_seviye * Decimal('0.5')
            
            bakiye = StokBakiyeDTO(
                id=magaza_id,
                urun_id=magaza_id,
                magaza_id=magaza_id,
                kullanilabilir_miktar=stok,
                miktar=stok,
                rezerve_miktar=Decimal('0')
            )
            
            urunler.append(urun)
            bakiyeler.append(bakiye)
        
        # Mock repository responses
        def mock_bakiyeler_getir(magaza_id=None, depo_id=None):
            if magaza_id is None:
                return bakiyeler
            return [b for b in bakiyeler if b.magaza_id == magaza_id]
        
        self.bakiye_repository.tum_bakiyeler_getir.side_effect = mock_bakiyeler_getir
        self.urun_repository.id_ile_getir.side_effect = lambda uid: next(
            (u for u in urunler if u.id == uid), None
        )
        
        # Belirli bir mağaza için kritik stok listesi
        hedef_magaza = 1
        kritik_stoklar = self.service.kritik_stok_listesi(magaza_id=hedef_magaza)
        
        # Sadece hedef mağazanın uyarıları olmalı
        for uyari in kritik_stoklar:
            assert uyari.magaza_id == hedef_magaza, \
                f"Mağaza filtresi çalışmalı: beklenen {hedef_magaza}, bulunan {uyari.magaza_id}"
    
    @given(
        kritik_seviye=st.decimals(min_value=Decimal('5'), max_value=Decimal('25'), places=4)
    )
    @settings(max_examples=50)
    def test_property_sadece_kritik_filtresi(self, kritik_seviye):
        """
        **Feature: gelismis-stok-yonetimi, Property 17: Kritik stok uyarı sistemi**
        
        For critical-only filter, only critical level warnings should be returned
        """
        bakiyeler = []
        urunler = []
        
        # Farklı seviyede stoklar oluştur
        stok_seviyeleri = [
            (Decimal('0'), 'ACIL'),  # Sıfır stok
            (kritik_seviye * Decimal('0.3'), 'KRITIK'),  # Kritik seviyenin %30'u
            (kritik_seviye * Decimal('0.8'), 'UYARI'),  # Kritik seviyenin %80'i
            (kritik_seviye * Decimal('1.2'), None)  # Kritik seviyenin üstü (uyarı yok)
        ]
        
        for i, (stok, beklenen_seviye) in enumerate(stok_seviyeleri):
            if beklenen_seviye is None:
                continue  # Kritik olmayan stokları atla
                
            urun = UrunDTO(
                id=i+1,
                urun_kodu=f"TEST{i+1:03d}",
                urun_adi=f"Test Ürün {i+1}",
                minimum_stok=kritik_seviye
            )
            
            bakiye = StokBakiyeDTO(
                id=i+1,
                urun_id=i+1,
                magaza_id=1,
                kullanilabilir_miktar=stok,
                miktar=stok,
                rezerve_miktar=Decimal('0')
            )
            
            urunler.append(urun)
            bakiyeler.append(bakiye)
        
        # Mock repository responses
        self.bakiye_repository.tum_bakiyeler_getir.return_value = bakiyeler
        self.urun_repository.id_ile_getir.side_effect = lambda uid: next(
            (u for u in urunler if u.id == uid), None
        )
        
        # Sadece kritik stokları getir
        kritik_stoklar = self.service.kritik_stok_listesi(sadece_kritik=True)
        
        # Sadece KRITIK seviyedeki uyarılar olmalı
        for uyari in kritik_stoklar:
            assert uyari.uyari_seviyesi == 'KRITIK', \
                f"Sadece kritik filtresi ile sadece KRITIK uyarılar dönmeli, bulunan: {uyari.uyari_seviyesi}"
    
    @given(
        yeni_kritik_seviye=st.decimals(min_value=Decimal('1'), max_value=Decimal('100'), places=4)
    )
    @settings(max_examples=50)
    def test_property_kritik_seviye_guncelleme(self, yeni_kritik_seviye):
        """
        **Feature: gelismis-stok-yonetimi, Property 17: Kritik stok uyarı sistemi**
        
        For any valid critical level update, the new level should be applied correctly
        """
        urun_id = 1
        
        # Mevcut ürün
        mevcut_urun = UrunDTO(
            id=urun_id,
            urun_kodu="TEST001",
            urun_adi="Test Ürün",
            minimum_stok=Decimal('10')
        )
        
        # Mock repository responses
        self.urun_repository.id_ile_getir.return_value = mevcut_urun
        self.urun_repository.guncelle.return_value = True
        
        # Kritik seviyeyi güncelle
        sonuc = self.service.kritik_seviye_guncelle(urun_id, yeni_kritik_seviye)
        
        # Güncelleme başarılı olmalı
        assert sonuc is True, "Geçerli kritik seviye güncellemesi başarılı olmalı"
        
        # Repository'nin guncelle metodunun çağrıldığını kontrol et
        self.urun_repository.guncelle.assert_called_once()
        
        # Güncellenen ürünün kritik seviyesini kontrol et
        guncellenen_urun = self.urun_repository.guncelle.call_args[0][1]
        assert guncellenen_urun.minimum_stok == yeni_kritik_seviye, \
            f"Kritik seviye güncellenmeli: beklenen {yeni_kritik_seviye}, bulunan {guncellenen_urun.minimum_stok}"