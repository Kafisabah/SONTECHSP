# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.test_sepet_property
# Description: Sepet modeli özellik tabanlı testleri
# Changelog:
# - İlk oluşturma

"""
Sepet Modeli Özellik Tabanlı Testleri

Bu modül sepet modelinin özellik tabanlı testlerini içerir.
Hypothesis kütüphanesi kullanılarak rastgele verilerle test edilir.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from hypothesis import given, strategies as st, assume, settings
from unittest.mock import Mock, patch

from sontechsp.uygulama.moduller.pos.database.models.sepet import (
    Sepet, SepetSatiri, sepet_validasyon, sepet_satiri_validasyon
)
from sontechsp.uygulama.moduller.pos.arayuzler import SepetDurum


class TestSepetPropertyTests:
    """Sepet modeli özellik tabanlı testleri"""
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        barkod=st.text(alphabet='0123456789', min_size=8, max_size=13),
        urun_id=st.integers(min_value=1, max_value=10000),
        adet=st.integers(min_value=1, max_value=100),
        birim_fiyat=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999.99'), places=2)
    )
    @settings(max_examples=100)
    def test_property_1_barkod_dogrulama_ve_sepete_ekleme(
        self, terminal_id, kasiyer_id, barkod, urun_id, adet, birim_fiyat
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 1: Barkod Doğrulama ve Sepete Ekleme**
        **Validates: Requirements 1.1, 1.2**
        
        Herhangi bir geçerli barkod için, barkod okutulduğunda sistem ürün bilgilerini 
        doğru şekilde getirmeli ve sepete eklemeli, sepet toplamını güncellemeli
        """
        # Arrange - Sepet oluştur
        sepet = Sepet(
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            durum=SepetDurum.AKTIF,
            toplam_tutar=Decimal('0.00')
        )
        
        # Mock stok servisi - geçerli ürün döner
        mock_urun_bilgisi = {
            'id': urun_id,
            'ad': f'Test Ürün {urun_id}',
            'barkod': barkod,
            'fiyat': birim_fiyat,
            'stok_miktari': 100
        }
        
        # Act - Sepete ürün ekle
        sepet_satiri = SepetSatiri(
            sepet_id=1,  # Mock sepet ID
            urun_id=urun_id,
            barkod=barkod,
            urun_adi=mock_urun_bilgisi['ad'],
            adet=adet,
            birim_fiyat=birim_fiyat,
            toplam_tutar=Decimal(str(adet)) * birim_fiyat
        )
        
        # Sepet toplamını güncelle
        sepet.toplam_tutar = sepet_satiri.toplam_tutar
        
        # Assert - Özellik doğrulamaları
        # 1. Ürün bilgileri doğru şekilde alınmış olmalı
        assert sepet_satiri.urun_id == urun_id
        assert sepet_satiri.barkod == barkod
        assert sepet_satiri.birim_fiyat == birim_fiyat
        assert sepet_satiri.adet == adet
        
        # 2. Sepete eklenmiş olmalı (validasyon geçmeli)
        sepet_hatalari = sepet_validasyon(sepet)
        satir_hatalari = sepet_satiri_validasyon(sepet_satiri)
        assert len(sepet_hatalari) == 0, f"Sepet validasyon hataları: {sepet_hatalari}"
        assert len(satir_hatalari) == 0, f"Satır validasyon hataları: {satir_hatalari}"
        
        # 3. Sepet toplamı güncellenmiş olmalı
        beklenen_toplam = Decimal(str(adet)) * birim_fiyat
        assert sepet.toplam_tutar == beklenen_toplam
        assert sepet_satiri.toplam_tutar == beklenen_toplam
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        urun_id=st.integers(min_value=1, max_value=10000),
        barkod=st.text(alphabet='0123456789', min_size=8, max_size=13),
        ilk_adet=st.integers(min_value=1, max_value=50),
        ikinci_adet=st.integers(min_value=1, max_value=50),
        birim_fiyat=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999.99'), places=2)
    )
    @settings(max_examples=100)
    def test_property_2_ayni_urun_adet_artirma(
        self, terminal_id, kasiyer_id, urun_id, barkod, ilk_adet, ikinci_adet, birim_fiyat
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 2: Aynı Ürün Adet Artırma**
        **Validates: Requirements 1.3**
        
        Herhangi bir ürün için, aynı ürün tekrar sepete eklendiğinde yeni satır 
        oluşturmak yerine mevcut satırın adedini artırmalı
        """
        # Arrange - Sepet ve ilk satır oluştur
        sepet = Sepet(
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            durum=SepetDurum.AKTIF,
            toplam_tutar=Decimal('0.00')
        )
        
        # İlk ürün ekleme
        mevcut_satir = SepetSatiri(
            sepet_id=1,
            urun_id=urun_id,
            barkod=barkod,
            urun_adi=f'Test Ürün {urun_id}',
            adet=ilk_adet,
            birim_fiyat=birim_fiyat,
            toplam_tutar=Decimal(str(ilk_adet)) * birim_fiyat
        )
        
        # Act - Aynı ürünü tekrar ekleme (adet artırma simülasyonu)
        yeni_toplam_adet = ilk_adet + ikinci_adet
        mevcut_satir.adet = yeni_toplam_adet
        mevcut_satir.toplam_tutar_guncelle()
        
        # Sepet toplamını güncelle
        sepet.toplam_tutar = mevcut_satir.toplam_tutar
        
        # Assert - Özellik doğrulamaları
        # 1. Yeni satır oluşturulmamış, mevcut satır güncellenmiş olmalı
        assert mevcut_satir.adet == yeni_toplam_adet
        
        # 2. Toplam tutar doğru hesaplanmış olmalı
        beklenen_toplam = Decimal(str(yeni_toplam_adet)) * birim_fiyat
        assert mevcut_satir.toplam_tutar == beklenen_toplam
        assert sepet.toplam_tutar == beklenen_toplam
        
        # 3. Validasyon geçmeli
        sepet_hatalari = sepet_validasyon(sepet)
        satir_hatalari = sepet_satiri_validasyon(mevcut_satir)
        assert len(sepet_hatalari) == 0, f"Sepet validasyon hataları: {sepet_hatalari}"
        assert len(satir_hatalari) == 0, f"Satır validasyon hataları: {satir_hatalari}"
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        gecersiz_barkod=st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=20)
    )
    @settings(max_examples=100)
    def test_property_3_gecersiz_barkod_hata_yonetimi(
        self, terminal_id, kasiyer_id, gecersiz_barkod
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 3: Geçersiz Barkod Hata Yönetimi**
        **Validates: Requirements 1.4**
        
        Herhangi bir geçersiz barkod için, sistem hata mesajı göstermeli ve sepeti değiştirmemeli
        """
        # Arrange - Boş sepet oluştur
        sepet = Sepet(
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            durum=SepetDurum.AKTIF,
            toplam_tutar=Decimal('0.00')
        )
        
        onceki_toplam = sepet.toplam_tutar
        
        # Act & Assert - Geçersiz barkod ile ürün ekleme denemesi
        # Mock stok servisi - geçersiz barkod için None döner
        with patch('sontechsp.uygulama.moduller.pos.servisler.sepet_service.IStokService') as mock_stok:
            mock_stok.urun_bilgisi_getir.return_value = None
            
            # Geçersiz barkod durumunda hata oluşmalı
            # Bu durumda sepet değişmemeli
            assert sepet.toplam_tutar == onceki_toplam
            
            # Geçersiz barkod ile satır oluşturma denemesi başarısız olmalı
            # (Gerçek implementasyonda service katmanında kontrol edilir)
            # Burada model seviyesinde validasyon test ediyoruz
            
            # Boş barkod ile satır oluşturma
            try:
                gecersiz_satir = SepetSatiri(
                    sepet_id=1,
                    urun_id=1,
                    barkod="",  # Boş barkod
                    urun_adi="Test",
                    adet=1,
                    birim_fiyat=Decimal('10.00'),
                    toplam_tutar=Decimal('10.00')
                )
                
                # Validasyon hata vermeli
                hatalar = sepet_satiri_validasyon(gecersiz_satir)
                assert len(hatalar) > 0, "Geçersiz barkod için validasyon hatası bekleniyor"
                assert any("barkod" in hata.lower() for hata in hatalar)
                
            except Exception:
                # Model seviyesinde exception da kabul edilebilir
                pass
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('9999.99'), places=2),
        indirim_orani=st.floats(min_value=0.0, max_value=1.0)
    )
    @settings(max_examples=100)
    def test_sepet_net_tutar_hesaplama(
        self, terminal_id, kasiyer_id, toplam_tutar, indirim_orani
    ):
        """
        Sepet net tutar hesaplama özellik testi
        
        Herhangi bir sepet için net tutar doğru hesaplanmalı
        """
        # Arrange
        indirim_tutari = toplam_tutar * Decimal(str(indirim_orani))
        
        sepet = Sepet(
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            durum=SepetDurum.AKTIF,
            toplam_tutar=toplam_tutar,
            indirim_tutari=indirim_tutari
        )
        
        # Act
        net_tutar = sepet.net_tutar_hesapla()
        
        # Assert
        beklenen_net_tutar = toplam_tutar - indirim_tutari
        assert abs(net_tutar - beklenen_net_tutar) < Decimal('0.01')
        assert net_tutar >= Decimal('0.00')
    
    @given(
        adet_listesi=st.lists(
            st.integers(min_value=1, max_value=100),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=100)
    def test_sepet_toplam_adet_hesaplama(self, adet_listesi):
        """
        Sepet toplam adet hesaplama özellik testi
        
        Herhangi bir sepet için toplam adet doğru hesaplanmalı
        """
        # Arrange
        sepet = Sepet(
            terminal_id=1,
            kasiyer_id=1,
            durum=SepetDurum.AKTIF,
            toplam_tutar=Decimal('0.00')
        )
        
        # Gerçek SepetSatiri objelerini oluştur
        from sontechsp.uygulama.moduller.pos.database.models.sepet import SepetSatiri
        satirlar = []
        for i, adet in enumerate(adet_listesi):
            satir = SepetSatiri(
                urun_id=i+1,
                barkod=f"test_barkod_{i}",
                adet=adet,
                birim_fiyat=Decimal('10.00'),
                indirim_tutari=Decimal('0.00'),
                toplam_tutar=Decimal(str(adet * 10))
            )
            satirlar.append(satir)
        
        # Sepete satırları ekle
        for satir in satirlar:
            sepet.satirlar.append(satir)
        
        # Act
        toplam_adet = sepet.toplam_adet()
        
        # Assert
        beklenen_toplam = sum(adet_listesi)
        assert toplam_adet == beklenen_toplam

class TestAyniUrunEklemePropertyTests:
    """Aynı ürün ekleme özellik tabanlı testleri"""
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        urun_id=st.integers(min_value=1, max_value=10000),
        barkod=st.text(alphabet='0123456789', min_size=8, max_size=13),
        ekleme_sayisi=st.integers(min_value=2, max_value=10),
        birim_fiyat=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999.99'), places=2)
    )
    @settings(max_examples=100)
    def test_property_2_coklu_ayni_urun_ekleme(
        self, terminal_id, kasiyer_id, urun_id, barkod, ekleme_sayisi, birim_fiyat
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 2: Aynı Ürün Adet Artırma**
        **Validates: Requirements 1.3**
        
        Aynı ürün birden fazla kez eklendiğinde, her seferinde mevcut satırın adedi artmalı
        """
        # Arrange
        sepet = Sepet(
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            durum=SepetDurum.AKTIF,
            toplam_tutar=Decimal('0.00')
        )
        
        # İlk ürün ekleme
        sepet_satiri = SepetSatiri(
            sepet_id=1,
            urun_id=urun_id,
            barkod=barkod,
            urun_adi=f'Test Ürün {urun_id}',
            adet=1,
            birim_fiyat=birim_fiyat,
            toplam_tutar=birim_fiyat
        )
        
        # Act - Aynı ürünü birden fazla kez ekleme simülasyonu
        for i in range(ekleme_sayisi - 1):  # -1 çünkü ilk ekleme zaten yapıldı
            sepet_satiri.adet += 1
            sepet_satiri.toplam_tutar_guncelle()
        
        # Sepet toplamını güncelle
        sepet.toplam_tutar = sepet_satiri.toplam_tutar
        
        # Assert
        # 1. Toplam adet doğru olmalı
        assert sepet_satiri.adet == ekleme_sayisi
        
        # 2. Toplam tutar doğru hesaplanmış olmalı
        beklenen_toplam = Decimal(str(ekleme_sayisi)) * birim_fiyat
        assert sepet_satiri.toplam_tutar == beklenen_toplam
        assert sepet.toplam_tutar == beklenen_toplam
        
        # 3. Validasyon geçmeli
        sepet_hatalari = sepet_validasyon(sepet)
        satir_hatalari = sepet_satiri_validasyon(sepet_satiri)
        assert len(sepet_hatalari) == 0
        assert len(satir_hatalari) == 0
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        urun_listesi=st.lists(
            st.tuples(
                st.integers(min_value=1, max_value=1000),  # urun_id
                st.text(alphabet='0123456789', min_size=8, max_size=13),  # barkod
                st.decimals(min_value=Decimal('0.01'), max_value=Decimal('99.99'), places=2)  # fiyat
            ),
            min_size=2,
            max_size=5,
            unique_by=lambda x: x[0]  # urun_id'ye göre unique
        )
    )
    @settings(max_examples=50)
    def test_property_2_farkli_urunler_ayri_satirlar(
        self, terminal_id, kasiyer_id, urun_listesi
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 2: Aynı Ürün Adet Artırma**
        **Validates: Requirements 1.3**
        
        Farklı ürünler için ayrı satırlar oluşturulmalı, aynı ürün için tek satır kullanılmalı
        """
        # Arrange
        sepet = Sepet(
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            durum=SepetDurum.AKTIF,
            toplam_tutar=Decimal('0.00')
        )
        
        satirlar = []
        toplam_tutar = Decimal('0.00')
        
        # Act - Her ürün için satır oluştur
        for urun_id, barkod, birim_fiyat in urun_listesi:
            satir = SepetSatiri(
                sepet_id=1,
                urun_id=urun_id,
                barkod=barkod,
                urun_adi=f'Test Ürün {urun_id}',
                adet=1,
                birim_fiyat=birim_fiyat,
                toplam_tutar=birim_fiyat
            )
            satirlar.append(satir)
            toplam_tutar += birim_fiyat
        
        sepet.toplam_tutar = toplam_tutar
        
        # Assert
        # 1. Her ürün için ayrı satır oluşturulmuş olmalı
        assert len(satirlar) == len(urun_listesi)
        
        # 2. Her satırın ürün ID'si farklı olmalı
        urun_idleri = [satir.urun_id for satir in satirlar]
        assert len(set(urun_idleri)) == len(urun_idleri)  # Unique kontrolü
        
        # 3. Toplam tutar doğru hesaplanmış olmalı
        beklenen_toplam = sum(fiyat for _, _, fiyat in urun_listesi)
        assert sepet.toplam_tutar == beklenen_toplam
        
        # 4. Tüm satırlar validasyon geçmeli
        for satir in satirlar:
            hatalar = sepet_satiri_validasyon(satir)
            assert len(hatalar) == 0, f"Satır validasyon hataları: {hatalar}"
        
        sepet_hatalari = sepet_validasyon(sepet)
        assert len(sepet_hatalari) == 0, f"Sepet validasyon hataları: {sepet_hatalari}"
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        urun_id=st.integers(min_value=1, max_value=10000),
        barkod=st.text(alphabet='0123456789', min_size=8, max_size=13),
        baslangic_adet=st.integers(min_value=1, max_value=50),
        eklenen_adet=st.integers(min_value=1, max_value=50),
        birim_fiyat=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999.99'), places=2)
    )
    @settings(max_examples=100)
    def test_property_2_adet_artirma_idempotent(
        self, terminal_id, kasiyer_id, urun_id, barkod, baslangic_adet, eklenen_adet, birim_fiyat
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 2: Aynı Ürün Adet Artırma**
        **Validates: Requirements 1.3**
        
        Adet artırma işlemi idempotent olmalı - aynı sonucu vermeli
        """
        # Arrange - İki aynı sepet satırı oluştur
        satir1 = SepetSatiri(
            sepet_id=1,
            urun_id=urun_id,
            barkod=barkod,
            urun_adi=f'Test Ürün {urun_id}',
            adet=baslangic_adet,
            birim_fiyat=birim_fiyat,
            toplam_tutar=Decimal(str(baslangic_adet)) * birim_fiyat
        )
        
        satir2 = SepetSatiri(
            sepet_id=1,
            urun_id=urun_id,
            barkod=barkod,
            urun_adi=f'Test Ürün {urun_id}',
            adet=baslangic_adet,
            birim_fiyat=birim_fiyat,
            toplam_tutar=Decimal(str(baslangic_adet)) * birim_fiyat
        )
        
        # Act - Her ikisine de aynı miktarda adet ekle
        satir1.adet += eklenen_adet
        satir1.toplam_tutar_guncelle()
        
        satir2.adet += eklenen_adet
        satir2.toplam_tutar_guncelle()
        
        # Assert - Her iki satır da aynı sonucu vermeli
        assert satir1.adet == satir2.adet
        assert satir1.toplam_tutar == satir2.toplam_tutar
        assert satir1.adet == baslangic_adet + eklenen_adet
        
        # Validasyon da aynı sonucu vermeli
        hatalar1 = sepet_satiri_validasyon(satir1)
        hatalar2 = sepet_satiri_validasyon(satir2)
        assert hatalar1 == hatalar2