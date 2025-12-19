# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_crm_entegrasyon_puan_hesaplama_property
# Description: CRM entegrasyon puan hesaplama property testleri
# Changelog:
# - İlk oluşturma

"""
**Feature: crm-cekirdek-modulu, Property 19: Puan hesaplama kuralı**
**Validates: Requirements 8.2, 9.2**

CRM modülü entegrasyon puan hesaplama kuralları için property-based testler.
"""

from unittest.mock import Mock, MagicMock
from hypothesis import given, strategies as st, assume, settings, HealthCheck
import pytest
from decimal import Decimal

from sontechsp.uygulama.moduller.crm.entegrasyon_kancalari import (
    pos_satis_tamamlandi, 
    satis_belgesi_olustu
)
from sontechsp.uygulama.moduller.crm.sabitler import PUAN_HESAPLAMA_ORANI


# Test stratejileri
musteri_id_strategy = st.one_of(
    st.none(),  # Müşteri yok
    st.integers(min_value=1, max_value=999999)  # Geçerli müşteri ID
)

tutar_strategy = st.floats(
    min_value=0.0, 
    max_value=10000.0,
    allow_nan=False,
    allow_infinity=False
)

satis_id_strategy = st.integers(min_value=1, max_value=999999)


@given(
    musteri_id=musteri_id_strategy,
    toplam_tutar=tutar_strategy,
    satis_id=satis_id_strategy
)
@settings(max_examples=100)
def test_pos_puan_hesaplama_kurali_property(musteri_id, toplam_tutar, satis_id):
    """
    **Feature: crm-cekirdek-modulu, Property 19: Puan hesaplama kuralı**
    **Validates: Requirements 8.2, 9.2**
    
    POS satış puan hesaplama kuralı: 1 TL = 1 puan
    """
    # Mock DB session
    mock_db = Mock()
    
    # Mock SadakatServisi
    mock_sadakat_servisi = Mock()
    mock_sadakat_servisi.puan_kazan = Mock(return_value=Mock())
    
    # Patch SadakatServisi import
    with pytest.MonkeyPatch().context() as m:
        m.setattr(
            'sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.SadakatServisi',
            lambda db: mock_sadakat_servisi
        )
        
        # Fonksiyonu çağır
        sonuc = pos_satis_tamamlandi(mock_db, musteri_id, toplam_tutar, satis_id)
        
        # Sonuç her zaman True olmalı (hata durumunda bile)
        assert sonuc is True
        
        # Müşteri varsa ve tutar pozitifse puan kazanım çağrılmalı
        if musteri_id is not None and toplam_tutar > 0:
            beklenen_puan = int(toplam_tutar * PUAN_HESAPLAMA_ORANI)
            if beklenen_puan > 0:
                mock_sadakat_servisi.puan_kazan.assert_called_once()
                
                # Çağrılan DTO'yu kontrol et
                call_args = mock_sadakat_servisi.puan_kazan.call_args[0][0]
                assert call_args.musteri_id == musteri_id
                assert call_args.puan == beklenen_puan
                assert "POS Satış" in call_args.aciklama
                assert call_args.referans_id == satis_id
            else:
                # Puan sıfırsa çağrılmamalı
                mock_sadakat_servisi.puan_kazan.assert_not_called()
        else:
            # Müşteri yoksa veya tutar sıfırsa çağrılmamalı
            mock_sadakat_servisi.puan_kazan.assert_not_called()


@given(
    musteri_id=musteri_id_strategy,
    belge_tutari=tutar_strategy,
    belge_id=satis_id_strategy
)
@settings(max_examples=100)
def test_satis_belgesi_puan_hesaplama_kurali_property(musteri_id, belge_tutari, belge_id):
    """
    **Feature: crm-cekirdek-modulu, Property 19: Puan hesaplama kuralı**
    **Validates: Requirements 8.2, 9.2**
    
    Satış belgesi puan hesaplama kuralı: 1 TL = 1 puan
    """
    # Mock DB session
    mock_db = Mock()
    
    # Mock SadakatServisi
    mock_sadakat_servisi = Mock()
    mock_sadakat_servisi.puan_kazan = Mock(return_value=Mock())
    
    # Patch SadakatServisi import
    with pytest.MonkeyPatch().context() as m:
        m.setattr(
            'sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.SadakatServisi',
            lambda db: mock_sadakat_servisi
        )
        
        # Fonksiyonu çağır
        sonuc = satis_belgesi_olustu(mock_db, musteri_id, belge_tutari, belge_id)
        
        # Sonuç her zaman True olmalı (hata durumunda bile)
        assert sonuc is True
        
        # Müşteri varsa ve tutar pozitifse puan kazanım çağrılmalı
        if musteri_id is not None and belge_tutari > 0:
            beklenen_puan = int(belge_tutari * PUAN_HESAPLAMA_ORANI)
            if beklenen_puan > 0:
                mock_sadakat_servisi.puan_kazan.assert_called_once()
                
                # Çağrılan DTO'yu kontrol et
                call_args = mock_sadakat_servisi.puan_kazan.call_args[0][0]
                assert call_args.musteri_id == musteri_id
                assert call_args.puan == beklenen_puan
                assert "Satış Belgesi" in call_args.aciklama
                assert call_args.referans_id == belge_id
            else:
                # Puan sıfırsa çağrılmamalı
                mock_sadakat_servisi.puan_kazan.assert_not_called()
        else:
            # Müşteri yoksa veya tutar sıfırsa çağrılmamalı
            mock_sadakat_servisi.puan_kazan.assert_not_called()


def test_puan_hesaplama_orani_sabiti():
    """
    Puan hesaplama oranının doğru değerde olduğunu test eder
    """
    # 1 TL = 1 puan kuralı
    assert PUAN_HESAPLAMA_ORANI == 1.0


def test_pos_musteri_yok_durumu():
    """
    POS satışında müşteri yoksa sessizce atlanmalı
    """
    mock_db = Mock()
    
    sonuc = pos_satis_tamamlandi(mock_db, None, 100.0, 123)
    
    assert sonuc is True


def test_satis_belgesi_musteri_yok_durumu():
    """
    Satış belgesinde müşteri yoksa sessizce atlanmalı
    """
    mock_db = Mock()
    
    sonuc = satis_belgesi_olustu(mock_db, None, 100.0, 123)
    
    assert sonuc is True


def test_pos_sifir_tutar_durumu():
    """
    POS satışında sıfır tutar varsa puan kazanımı olmamalı
    """
    mock_db = Mock()
    
    with pytest.MonkeyPatch().context() as m:
        mock_sadakat_servisi = Mock()
        m.setattr(
            'sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.SadakatServisi',
            lambda db: mock_sadakat_servisi
        )
        
        sonuc = pos_satis_tamamlandi(mock_db, 1, 0.0, 123)
        
        assert sonuc is True
        mock_sadakat_servisi.puan_kazan.assert_not_called()


def test_satis_belgesi_sifir_tutar_durumu():
    """
    Satış belgesinde sıfır tutar varsa puan kazanımı olmamalı
    """
    mock_db = Mock()
    
    with pytest.MonkeyPatch().context() as m:
        mock_sadakat_servisi = Mock()
        m.setattr(
            'sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.SadakatServisi',
            lambda db: mock_sadakat_servisi
        )
        
        sonuc = satis_belgesi_olustu(mock_db, 1, 0.0, 123)
        
        assert sonuc is True
        mock_sadakat_servisi.puan_kazan.assert_not_called()