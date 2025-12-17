# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_crm_entegrasyon_hata_yonetimi_property
# Description: CRM entegrasyon hata yönetimi property testleri
# Changelog:
# - İlk oluşturma

"""
**Feature: crm-cekirdek-modulu, Property 20: Entegrasyon hata yönetimi**
**Validates: Requirements 8.3, 9.4**

CRM modülü entegrasyon hata yönetimi için property-based testler.
Entegrasyon fonksiyonları hata durumunda POS/belge işlemlerini durdurmamalı.
"""

from unittest.mock import Mock, MagicMock, patch
from hypothesis import given, strategies as st, assume, settings
import pytest

from sontechsp.uygulama.moduller.crm.entegrasyon_kancalari import (
    pos_satis_tamamlandi, 
    satis_belgesi_olustu
)
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, VeritabaniHatasi


# Test stratejileri
musteri_id_strategy = st.integers(min_value=1, max_value=999999)
tutar_strategy = st.floats(min_value=1.0, max_value=10000.0, allow_nan=False, allow_infinity=False)
satis_id_strategy = st.integers(min_value=1, max_value=999999)

# Hata türleri
hata_turleri = [
    DogrulamaHatasi("Test doğrulama hatası"),
    VeritabaniHatasi("Test veritabanı hatası"),
    Exception("Test genel hatası"),
    RuntimeError("Test runtime hatası"),
    ValueError("Test value hatası")
]


@given(
    musteri_id=musteri_id_strategy,
    toplam_tutar=tutar_strategy,
    satis_id=satis_id_strategy,
    hata_turu=st.sampled_from(hata_turleri)
)
@settings(max_examples=50)
def test_pos_dogrulama_hatasi_yonetimi_property(musteri_id, toplam_tutar, satis_id, hata_turu):
    """
    **Feature: crm-cekirdek-modulu, Property 20: Entegrasyon hata yönetimi**
    **Validates: Requirements 8.3, 9.4**
    
    POS entegrasyonunda doğrulama hatası durumunda işlem durdurulmamalı
    """
    # Mock DB session
    mock_db = Mock()
    
    # Mock SadakatServisi - hata fırlatacak şekilde ayarla
    mock_sadakat_servisi = Mock()
    mock_sadakat_servisi.puan_kazan.side_effect = hata_turu
    
    # Patch SadakatServisi ve logger
    with patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.SadakatServisi') as mock_service_class, \
         patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.logger') as mock_logger:
        
        mock_service_class.return_value = mock_sadakat_servisi
        
        # Fonksiyonu çağır
        sonuc = pos_satis_tamamlandi(mock_db, musteri_id, toplam_tutar, satis_id)
        
        # Hata durumunda bile sonuç False olmalı ama exception fırlatmamalı
        assert sonuc is False
        
        # Puan kazanım çağrılmalı (hata fırlatsa bile)
        mock_sadakat_servisi.puan_kazan.assert_called_once()
        
        # Hata loglanmalı
        if isinstance(hata_turu, (DogrulamaHatasi, VeritabaniHatasi)):
            mock_logger.warning.assert_called_once()
        else:
            mock_logger.error.assert_called_once()


@given(
    musteri_id=musteri_id_strategy,
    belge_tutari=tutar_strategy,
    belge_id=satis_id_strategy,
    hata_turu=st.sampled_from(hata_turleri)
)
@settings(max_examples=50)
def test_satis_belgesi_dogrulama_hatasi_yonetimi_property(musteri_id, belge_tutari, belge_id, hata_turu):
    """
    **Feature: crm-cekirdek-modulu, Property 20: Entegrasyon hata yönetimi**
    **Validates: Requirements 8.3, 9.4**
    
    Satış belgesi entegrasyonunda doğrulama hatası durumunda işlem durdurulmamalı
    """
    # Mock DB session
    mock_db = Mock()
    
    # Mock SadakatServisi - hata fırlatacak şekilde ayarla
    mock_sadakat_servisi = Mock()
    mock_sadakat_servisi.puan_kazan.side_effect = hata_turu
    
    # Patch SadakatServisi ve logger
    with patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.SadakatServisi') as mock_service_class, \
         patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.logger') as mock_logger:
        
        mock_service_class.return_value = mock_sadakat_servisi
        
        # Fonksiyonu çağır
        sonuc = satis_belgesi_olustu(mock_db, musteri_id, belge_tutari, belge_id)
        
        # Hata durumunda bile sonuç False olmalı ama exception fırlatmamalı
        assert sonuc is False
        
        # Puan kazanım çağrılmalı (hata fırlatsa bile)
        mock_sadakat_servisi.puan_kazan.assert_called_once()
        
        # Hata loglanmalı
        if isinstance(hata_turu, (DogrulamaHatasi, VeritabaniHatasi)):
            mock_logger.warning.assert_called_once()
        else:
            mock_logger.error.assert_called_once()


def test_pos_dogrulama_hatasi_spesifik():
    """
    POS entegrasyonunda DogrulamaHatasi durumunda warning log atılmalı
    """
    mock_db = Mock()
    
    with patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.SadakatServisi') as mock_service_class, \
         patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.logger') as mock_logger:
        
        mock_sadakat_servisi = Mock()
        mock_sadakat_servisi.puan_kazan.side_effect = DogrulamaHatasi("Test hatası")
        mock_service_class.return_value = mock_sadakat_servisi
        
        sonuc = pos_satis_tamamlandi(mock_db, 1, 100.0, 123)
        
        assert sonuc is False
        mock_logger.warning.assert_called_once()
        assert "POS puan kazanım iş kuralı hatası" in mock_logger.warning.call_args[0][0]


def test_pos_veritabani_hatasi_spesifik():
    """
    POS entegrasyonunda VeritabaniHatasi durumunda warning log atılmalı
    """
    mock_db = Mock()
    
    with patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.SadakatServisi') as mock_service_class, \
         patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.logger') as mock_logger:
        
        mock_sadakat_servisi = Mock()
        mock_sadakat_servisi.puan_kazan.side_effect = VeritabaniHatasi("Test DB hatası")
        mock_service_class.return_value = mock_sadakat_servisi
        
        sonuc = pos_satis_tamamlandi(mock_db, 1, 100.0, 123)
        
        assert sonuc is False
        mock_logger.warning.assert_called_once()
        assert "POS puan kazanım iş kuralı hatası" in mock_logger.warning.call_args[0][0]


def test_pos_genel_hata_spesifik():
    """
    POS entegrasyonunda genel Exception durumunda error log atılmalı
    """
    mock_db = Mock()
    
    with patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.SadakatServisi') as mock_service_class, \
         patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.logger') as mock_logger:
        
        mock_sadakat_servisi = Mock()
        mock_sadakat_servisi.puan_kazan.side_effect = Exception("Test genel hatası")
        mock_service_class.return_value = mock_sadakat_servisi
        
        sonuc = pos_satis_tamamlandi(mock_db, 1, 100.0, 123)
        
        assert sonuc is False
        mock_logger.error.assert_called_once()
        assert "POS puan kazanım beklenmeyen hatası" in mock_logger.error.call_args[0][0]


def test_satis_belgesi_dogrulama_hatasi_spesifik():
    """
    Satış belgesi entegrasyonunda DogrulamaHatasi durumunda warning log atılmalı
    """
    mock_db = Mock()
    
    with patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.SadakatServisi') as mock_service_class, \
         patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.logger') as mock_logger:
        
        mock_sadakat_servisi = Mock()
        mock_sadakat_servisi.puan_kazan.side_effect = DogrulamaHatasi("Test hatası")
        mock_service_class.return_value = mock_sadakat_servisi
        
        sonuc = satis_belgesi_olustu(mock_db, 1, 100.0, 123)
        
        assert sonuc is False
        mock_logger.warning.assert_called_once()
        assert "Satış belgesi puan kazanım iş kuralı hatası" in mock_logger.warning.call_args[0][0]


def test_satis_belgesi_genel_hata_spesifik():
    """
    Satış belgesi entegrasyonunda genel Exception durumunda error log atılmalı
    """
    mock_db = Mock()
    
    with patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.SadakatServisi') as mock_service_class, \
         patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.logger') as mock_logger:
        
        mock_sadakat_servisi = Mock()
        mock_sadakat_servisi.puan_kazan.side_effect = Exception("Test genel hatası")
        mock_service_class.return_value = mock_sadakat_servisi
        
        sonuc = satis_belgesi_olustu(mock_db, 1, 100.0, 123)
        
        assert sonuc is False
        mock_logger.error.assert_called_once()
        assert "Satış belgesi puan kazanım beklenmeyen hatası" in mock_logger.error.call_args[0][0]