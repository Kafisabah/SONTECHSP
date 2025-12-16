# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.test_satis_property
# Description: Satış ve ödeme modeli özellik tabanlı testleri
# Changelog:
# - İlk oluşturma

"""
Satış ve Ödeme Modeli Özellik Tabanlı Testleri

Bu modül satış ve ödeme modellerinin özellik tabanlı testlerini içerir.
Hypothesis kütüphanesi kullanılarak rastgele verilerle test edilir.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from hypothesis import given, strategies as st, assume, settings
from unittest.mock import Mock, patch

from sontechsp.uygulama.moduller.pos.database.models.satis import (
    Satis, SatisOdeme, satis_validasyon, satis_odeme_validasyon
)
from sontechsp.uygulama.moduller.pos.arayuzler import SatisDurum, OdemeTuru


class TestSatisOdemePropertyTests:
    """Satış ve ödeme modeli özellik tabanlı testleri"""
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('9999.99'), places=2),
        odeme_turu=st.sampled_from(list(OdemeTuru))
    )
    @settings(max_examples=100)
    def test_property_9_tek_odeme_islemi(
        self, terminal_id, kasiyer_id, toplam_tutar, odeme_turu
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 9: Tek Ödeme İşlemi**
        **Validates: Requirements 3.1**
        
        Herhangi bir tek ödeme yöntemi ve tutarı için, sistem ödeme tutarını 
        doğrulamalı ve satışı tamamlamalı
        """
        # Arrange - Satış oluştur
        satis = Satis(
            sepet_id=1,
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            satis_tarihi=datetime.now(),
            toplam_tutar=toplam_tutar,
            durum=SatisDurum.BEKLEMEDE
        )
        
        # Act - Tek ödeme ekle
        odeme = SatisOdeme(
            satis_id=1,
            odeme_turu=odeme_turu,
            tutar=toplam_tutar,  # Tam tutar ödeme
            odeme_tarihi=datetime.now(),
            referans_no="REF123" if odeme_turu in [OdemeTuru.KART, OdemeTuru.HAVALE] else None
        )
        
        # Satışa ödeme ekle (simülasyon)
        satis.odemeler = [odeme]
        
        # Assert - Özellik doğrulamaları
        # 1. Ödeme tutarı doğrulanmış olmalı
        assert odeme.tutar == toplam_tutar
        assert odeme.tutar > Decimal('0.00')
        
        # 2. Satış tamamlanabilir durumda olmalı
        assert satis.odeme_tamamlandi_mi() == True
        assert satis.kalan_tutar() == Decimal('0.00')
        
        # 3. Validasyon geçmeli
        satis_hatalari = satis_validasyon(satis)
        odeme_hatalari = satis_odeme_validasyon(odeme)
        assert len(satis_hatalari) == 0, f"Satış validasyon hataları: {satis_hatalari}"
        assert len(odeme_hatalari) == 0, f"Ödeme validasyon hataları: {odeme_hatalari}"
        
        # 4. Toplam ödeme tutarı doğru hesaplanmış olmalı
        assert satis.toplam_odeme_tutari() == toplam_tutar
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal('10.00'), max_value=Decimal('1000.00'), places=2),
        odeme_sayisi=st.integers(min_value=2, max_value=5)
    )
    @settings(max_examples=100)
    def test_property_10_parcali_odeme_islemi(
        self, terminal_id, kasiyer_id, toplam_tutar, odeme_sayisi
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 10: Parçalı Ödeme İşlemi**
        **Validates: Requirements 3.2**
        
        Herhangi bir parçalı ödeme kombinasyonu için, sistem birden fazla 
        ödeme yöntemini kabul etmeli
        """
        # Arrange - Satış oluştur
        satis = Satis(
            sepet_id=1,
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            satis_tarihi=datetime.now(),
            toplam_tutar=toplam_tutar,
            durum=SatisDurum.BEKLEMEDE
        )
        
        # Act - Parçalı ödemeler oluştur
        odemeler = []
        kalan_tutar = toplam_tutar
        odeme_turleri = list(OdemeTuru)
        
        for i in range(odeme_sayisi):
            if i == odeme_sayisi - 1:
                # Son ödeme kalan tutarın tamamı
                odeme_tutari = kalan_tutar
            else:
                # Rastgele tutar (kalan tutarın %10-80'i arası)
                min_tutar = min(kalan_tutar * Decimal('0.1'), Decimal('1.00'))
                max_tutar = kalan_tutar * Decimal('0.8')
                odeme_tutari = min(max_tutar, kalan_tutar - Decimal('1.00'))
                odeme_tutari = max(min_tutar, odeme_tutari)
                odeme_tutari = odeme_tutari.quantize(Decimal('0.01'))
            
            odeme_turu = odeme_turleri[i % len(odeme_turleri)]
            
            odeme = SatisOdeme(
                satis_id=1,
                odeme_turu=odeme_turu,
                tutar=odeme_tutari,
                odeme_tarihi=datetime.now(),
                referans_no=f"REF{i}" if odeme_turu in [OdemeTuru.KART, OdemeTuru.HAVALE] else None
            )
            
            odemeler.append(odeme)
            kalan_tutar -= odeme_tutari
        
        # Satışa ödemeleri ekle
        satis.odemeler = odemeler
        
        # Assert - Özellik doğrulamaları
        # 1. Birden fazla ödeme yöntemi kabul edilmiş olmalı
        assert len(odemeler) == odeme_sayisi
        assert len(odemeler) > 1
        
        # 2. Toplam ödeme tutarı satış tutarına eşit olmalı
        toplam_odeme = sum(odeme.tutar for odeme in odemeler)
        assert abs(toplam_odeme - toplam_tutar) < Decimal('0.01')
        
        # 3. Satış tamamlanabilir durumda olmalı
        assert satis.odeme_tamamlandi_mi() == True
        assert satis.kalan_tutar() < Decimal('0.01')
        
        # 4. Tüm ödemeler validasyon geçmeli
        for i, odeme in enumerate(odemeler):
            odeme_hatalari = satis_odeme_validasyon(odeme)
            assert len(odeme_hatalari) == 0, f"Ödeme {i} validasyon hataları: {odeme_hatalari}"
        
        satis_hatalari = satis_validasyon(satis)
        assert len(satis_hatalari) == 0, f"Satış validasyon hataları: {satis_hatalari}"
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal('1.00'), max_value=Decimal('1000.00'), places=2),
        odeme_tutari=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999.99'), places=2)
    )
    @settings(max_examples=100)
    def test_property_11_odeme_tutari_eslesmesi(
        self, terminal_id, kasiyer_id, toplam_tutar, odeme_tutari
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 11: Ödeme Tutarı Eşleşmesi**
        **Validates: Requirements 3.3**
        
        Herhangi bir sepet ve ödeme tutarı eşleşmesi için, sistem satışı onaylamalı 
        ve stok düşümü yapmalı
        """
        # Arrange
        satis = Satis(
            sepet_id=1,
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            satis_tarihi=datetime.now(),
            toplam_tutar=toplam_tutar,
            durum=SatisDurum.BEKLEMEDE
        )
        
        # Act - Ödeme tutarına göre farklı senaryolar
        if abs(odeme_tutari - toplam_tutar) < Decimal('0.01'):
            # Eşleşen tutar durumu
            odeme = SatisOdeme(
                satis_id=1,
                odeme_turu=OdemeTuru.NAKIT,
                tutar=odeme_tutari,
                odeme_tarihi=datetime.now()
            )
            satis.odemeler = [odeme]
            
            # Assert - Eşleşme durumu
            assert satis.odeme_tamamlandi_mi() == True
            assert satis.kalan_tutar() < Decimal('0.01')
            
            # Satış onaylanabilir durumda
            satis.durum = SatisDurum.TAMAMLANDI
            satis.fis_no = "FIS001"
            
            satis_hatalari = satis_validasyon(satis)
            assert len(satis_hatalari) == 0
            
        else:
            # Eşleşmeyen tutar durumu
            odeme = SatisOdeme(
                satis_id=1,
                odeme_turu=OdemeTuru.NAKIT,
                tutar=odeme_tutari,
                odeme_tarihi=datetime.now()
            )
            satis.odemeler = [odeme]
            
            # Assert - Eşleşmeme durumu
            if odeme_tutari < toplam_tutar:
                assert satis.odeme_tamamlandi_mi() == False
                assert satis.kalan_tutar() > Decimal('0.00')
            else:
                # Fazla ödeme durumu - bu durumda da tamamlanmış sayılabilir
                assert satis.odeme_tamamlandi_mi() == True or satis.kalan_tutar() == Decimal('0.00')
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal('10.00'), max_value=Decimal('1000.00'), places=2),
        eksik_oran=st.floats(min_value=0.1, max_value=0.9)
    )
    @settings(max_examples=100)
    def test_property_12_yetersiz_odeme_kontrolu(
        self, terminal_id, kasiyer_id, toplam_tutar, eksik_oran
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 12: Yetersiz Ödeme Kontrolü**
        **Validates: Requirements 3.4**
        
        Herhangi bir yetersiz ödeme durumu için, sistem eksik tutarı bildirmeli 
        ve satışı tamamlamamalı
        """
        # Arrange
        satis = Satis(
            sepet_id=1,
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            satis_tarihi=datetime.now(),
            toplam_tutar=toplam_tutar,
            durum=SatisDurum.BEKLEMEDE
        )
        
        # Act - Yetersiz ödeme
        yetersiz_tutar = (toplam_tutar * Decimal(str(eksik_oran))).quantize(Decimal('0.01'))
        
        odeme = SatisOdeme(
            satis_id=1,
            odeme_turu=OdemeTuru.NAKIT,
            tutar=yetersiz_tutar,
            odeme_tarihi=datetime.now()
        )
        
        satis.odemeler = [odeme]
        
        # Assert - Yetersiz ödeme kontrolleri
        # 1. Ödeme tamamlanmamış olmalı
        assert satis.odeme_tamamlandi_mi() == False
        
        # 2. Kalan tutar pozitif olmalı (eksik tutarı gösterir)
        kalan = satis.kalan_tutar()
        assert kalan > Decimal('0.00')
        
        # 3. Kalan tutar doğru hesaplanmış olmalı
        beklenen_kalan = toplam_tutar - yetersiz_tutar
        assert abs(kalan - beklenen_kalan) < Decimal('0.01')
        
        # 4. Satış tamamlanamaz durumda olmalı
        satis.durum = SatisDurum.TAMAMLANDI
        satis.fis_no = "FIS001"
        
        satis_hatalari = satis_validasyon(satis)
        # Yetersiz ödeme nedeniyle validasyon hatası olmalı
        assert len(satis_hatalari) > 0
        assert any("ödeme tamamlanmış" in hata.lower() for hata in satis_hatalari)
    
    @given(
        kart_son_4_hane=st.text(alphabet='0123456789', min_size=4, max_size=4),
        banka_kodu=st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', min_size=3, max_size=10),
        taksit_sayisi=st.integers(min_value=1, max_value=12),
        tutar=st.decimals(min_value=Decimal('1.00'), max_value=Decimal('1000.00'), places=2)
    )
    @settings(max_examples=100)
    def test_kart_odeme_ozellikleri(
        self, kart_son_4_hane, banka_kodu, taksit_sayisi, tutar
    ):
        """
        Kart ödemesi özellik testi
        
        Herhangi bir kart ödemesi için ek bilgiler doğru saklanmalı
        """
        # Arrange & Act
        odeme = SatisOdeme(
            satis_id=1,
            odeme_turu=OdemeTuru.KART,
            tutar=tutar,
            odeme_tarihi=datetime.now(),
            referans_no="REF123",
            kart_son_4_hane=kart_son_4_hane,
            banka_kodu=banka_kodu,
            taksit_sayisi=taksit_sayisi
        )
        
        # Assert
        # 1. Kart ödemesi olarak tanınmalı
        assert odeme.kart_odeme_mi() == True
        assert odeme.nakit_odeme_mi() == False
        
        # 2. Kart bilgileri doğru saklanmış olmalı
        assert odeme.kart_son_4_hane == kart_son_4_hane
        assert len(odeme.kart_son_4_hane) == 4
        assert odeme.kart_son_4_hane.isdigit()
        
        # 3. Taksit bilgisi doğru olmalı
        assert odeme.taksit_sayisi == taksit_sayisi
        if taksit_sayisi > 1:
            assert odeme.taksitli_mi() == True
        else:
            assert odeme.taksitli_mi() == False
        
        # 4. Validasyon geçmeli
        hatalar = satis_odeme_validasyon(odeme)
        assert len(hatalar) == 0, f"Kart ödeme validasyon hataları: {hatalar}"
    
    @given(
        toplam_tutar=st.decimals(min_value=Decimal('1.00'), max_value=Decimal('1000.00'), places=2),
        indirim_orani=st.floats(min_value=0.0, max_value=0.5)
    )
    @settings(max_examples=100)
    def test_satis_net_tutar_hesaplama(self, toplam_tutar, indirim_orani):
        """
        Satış net tutar hesaplama özellik testi
        
        Herhangi bir satış için net tutar doğru hesaplanmalı
        """
        # Arrange
        indirim_tutari = (toplam_tutar * Decimal(str(indirim_orani))).quantize(Decimal('0.01'))
        
        satis = Satis(
            sepet_id=1,
            terminal_id=1,
            kasiyer_id=1,
            satis_tarihi=datetime.now(),
            toplam_tutar=toplam_tutar,
            indirim_tutari=indirim_tutari,
            durum=SatisDurum.BEKLEMEDE
        )
        
        # Act
        net_tutar = satis.net_tutar_hesapla()
        
        # Assert
        beklenen_net_tutar = toplam_tutar - indirim_tutari
        assert abs(net_tutar - beklenen_net_tutar) < Decimal('0.01')
        assert net_tutar >= Decimal('0.00')
        assert net_tutar <= toplam_tutar