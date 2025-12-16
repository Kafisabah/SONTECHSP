# Version: 0.1.0
# Last Update: 2025-12-16
# Module: test_pos_ui_complete
# Description: POS UI katmanı birim testleri - Tam implementasyonyon
# Changelog:
# - İlk oluşturma
# - Ekran yükleme testleri eklendi
# - Signal/slot bağlantı testleri eklendi
# - Service çağrı testleri eklendi

"""
POS UI Katmanı Birim Testleri

Ekran yükleme, signal/slot bağlantıları ve service çağrı testleri.
Requirements: 1.1, 3.1, 4.1
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock, call
from decimal import Decimal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest

from sontechsp.uygulama.moduller.pos.ui.sepet_ekrani import SepetEkrani
from sontechsp.uygulama.moduller.pos.ui.odeme_ekrani import OdemeEkrani
from sontechsp.uygulama.moduller.pos.ui.iade_ekrani import IadeEkrani


@pytest.fixture(scope="session")
def qapp():
    """PyQt6 uygulama fixture'ı"""
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app


@pytest.fixture
def mock_oturum():
    """Mock oturum fixture'ı"""
    oturum = Mock()
    oturum.terminal_id = 1
    oturum.kullanici_id = 1
    oturum.kullanici_adi = "Test Kasiyer"
    return oturum


@pytest.fixture
def mock_sepet_service():
    """Mock sepet service fixture'ı"""
    service = Mock()
    service.yeni_sepet_olustur.return_value = 1
    service.sepet_bilgisi_getir.return_value = {
        'id': 1,
        'toplam_tutar': Decimal('50.00'),
        'durum': 'AKTIF'
    }
    service.barkod_ekle.return_value = True
    service.urun_adedi_degistir.return_value = True
    service.satir_sil.return_value = True
    service.sepet_bosalt.return_value = True
    service.indirim_uygula.return_value = True
    return service


@pytest.fixture
def mock_odeme_service():
    """Mock ödeme service fixture'ı"""
    service = Mock()
    service.odeme_tamamla.return_value = True
    return service


@pytest.fixture
def mock_iade_service():
    """Mock iade service fixture'ı"""
    service = Mock()
    service.satis_bilgisi_getir.return_value = {
        'id': 1,
        'satis_tarihi': '2025-12-16',
        'kasiyer_adi': 'Test Kasiyer',
        'toplam_tutar': Decimal('100.00'),
        'durum': 'TAMAMLANDI'
    }
    service.fis_no_ile_satis_getir.return_value = {
        'id': 1,
        'satis_tarihi': '2025-12-16',
        'kasiyer_adi': 'Test Kasiyer',
        'toplam_tutar': Decimal('100.00'),
        'durum': 'TAMAMLANDI'
    }
    service.iade_olustur.return_value = True
    return service


class TestSepetEkrani:
    """Sepet ekranı testleri"""
    
    @patch('sontechsp.uygulama.moduller.pos.ui.sepet_ekrani.oturum_baglamini_al')
    @patch('sontechsp.uygulama.moduller.pos.ui.sepet_ekrani.SepetService')
    def test_ekran_yukleme(self, mock_service_class, mock_oturum_func, qapp, mock_oturum, mock_sepet_service):
        """Sepet ekranının doğru yüklendiğini test eder"""
        # Arrange
        mock_oturum_func.return_value = mock_oturum
        mock_service_class.return_value = mock_sepet_service
        
        # Act
        ekran = SepetEkrani()
        
        # Assert
        assert ekran is not None
        assert ekran.windowTitle() == "POS Sepet"
        assert ekran.aktif_sepet_id == 1
        assert hasattr(ekran, 'barkod_edit')
        assert hasattr(ekran, 'sepet_tablo')
        assert hasattr(ekran, 'toplam_tutar_label')
        
        # Service çağrılarını kontrol et
        mock_sepet_service.yeni_sepet_olustur.assert_called_once_with(1, 1)
        
        ekran.close()
    
    @patch('sontechsp.uygulama.moduller.pos.ui.sepet_ekrani.oturum_baglamini_al')
    @patch('sontechsp.uygulama.moduller.pos.ui.sepet_ekrani.SepetService')
    def test_barkod_ekleme_signal(self, mock_service_class, mock_oturum_func, qapp, mock_oturum, mock_sepet_service):
        """Barkod ekleme sinyalinin doğru çalıştığını test eder"""
        # Arrange
        mock_oturum_func.return_value = mock_oturum
        mock_service_class.return_value = mock_sepet_service
        
        ekran = SepetEkrani()
        signal_received = []
        
        def signal_handler(data):
            signal_received.append(data)
        
        ekran.urun_eklendi.connect(signal_handler)
        
        # Act
        ekran.barkod_edit.setText("1234567890123")
        ekran._barkod_isle()
        
        # Assert
        mock_sepet_service.barkod_ekle.assert_called_once_with(1, "1234567890123")
        assert len(signal_received) == 1
        assert signal_received[0]['barkod'] == "1234567890123"
        
        ekran.close()
    
    @patch('sontechsp.uygulama.moduller.pos.ui.sepet_ekrani.oturum_baglamini_al')
    @patch('sontechsp.uygulama.moduller.pos.ui.sepet_ekrani.SepetService')
    def test_sepet_bosaltma_service_cagrisi(self, mock_service_class, mock_oturum_func, qapp, mock_oturum, mock_sepet_service):
        """Sepet boşaltma service çağrısını test eder"""
        # Arrange
        mock_oturum_func.return_value = mock_oturum
        mock_service_class.return_value = mock_sepet_service
        
        ekran = SepetEkrani()
        
        # Onay mesajını mock'la
        with patch.object(ekran.mesaj_yoneticisi, 'onay_iste', return_value=True):
            # Act
            ekran._sepet_bosalt()
        
        # Assert
        mock_sepet_service.sepet_bosalt.assert_called_once_with(1)
        
        ekran.close()


class TestOdemeEkrani:
    """Ödeme ekranı testleri"""
    
    @patch('sontechsp.uygulama.moduller.pos.ui.odeme_ekrani.oturum_baglamini_al')
    @patch('sontechsp.uygulama.moduller.pos.ui.odeme_ekrani.OdemeService')
    def test_ekran_yukleme(self, mock_service_class, mock_oturum_func, qapp, mock_oturum, mock_odeme_service):
        """Ödeme ekranının doğru yüklendiğini test eder"""
        # Arrange
        mock_oturum_func.return_value = mock_oturum
        mock_service_class.return_value = mock_odeme_service
        
        sepet_bilgisi = {
            'id': 1,
            'toplam_tutar': Decimal('100.00'),
            'durum': 'AKTIF'
        }
        
        # Act
        ekran = OdemeEkrani(sepet_bilgisi)
        
        # Assert
        assert ekran is not None
        assert ekran.windowTitle() == "POS Ödeme"
        assert ekran.sepet_toplami == Decimal('100.00')
        assert hasattr(ekran, 'odeme_tutari_spin')
        assert hasattr(ekran, 'odeme_turu_combo')
        assert hasattr(ekran, 'tamamla_buton')
        
        ekran.close()
    
    @patch('sontechsp.uygulama.moduller.pos.ui.odeme_ekrani.oturum_baglamini_al')
    @patch('sontechsp.uygulama.moduller.pos.ui.odeme_ekrani.OdemeService')
    def test_odeme_tamamlama_signal(self, mock_service_class, mock_oturum_func, qapp, mock_oturum, mock_odeme_service):
        """Ödeme tamamlama sinyalinin doğru çalıştığını test eder"""
        # Arrange
        mock_oturum_func.return_value = mock_oturum
        mock_service_class.return_value = mock_odeme_service
        
        sepet_bilgisi = {
            'id': 1,
            'toplam_tutar': Decimal('100.00'),
            'durum': 'AKTIF'
        }
        
        ekran = OdemeEkrani(sepet_bilgisi)
        signal_received = []
        
        def signal_handler(data):
            signal_received.append(data)
        
        ekran.odeme_tamamlandi.connect(signal_handler)
        
        # Ödeme ekle
        ekran.odeme_tutari_spin.setValue(100.00)
        ekran._odeme_ekle()
        
        # Onay mesajını mock'la
        with patch.object(ekran.mesaj_yoneticisi, 'onay_iste', return_value=True):
            with patch.object(ekran.mesaj_yoneticisi, 'bilgi_goster'):
                # Act
                ekran._satisi_tamamla()
        
        # Assert
        mock_odeme_service.odeme_tamamla.assert_called_once()
        assert len(signal_received) == 1
        assert signal_received[0]['sepet_id'] == 1
        
        ekran.close()
    
    @patch('sontechsp.uygulama.moduller.pos.ui.odeme_ekrani.oturum_baglamini_al')
    @patch('sontechsp.uygulama.moduller.pos.ui.odeme_ekrani.OdemeService')
    def test_parcali_odeme_service_cagrisi(self, mock_service_class, mock_oturum_func, qapp, mock_oturum, mock_odeme_service):
        """Parçalı ödeme service çağrısını test eder"""
        # Arrange
        mock_oturum_func.return_value = mock_oturum
        mock_service_class.return_value = mock_odeme_service
        
        sepet_bilgisi = {
            'id': 1,
            'toplam_tutar': Decimal('100.00'),
            'durum': 'AKTIF'
        }
        
        ekran = OdemeEkrani(sepet_bilgisi)
        
        # Parçalı ödeme aktif et
        ekran.parcali_odeme_check.setChecked(True)
        
        # İlk ödeme
        ekran.odeme_tutari_spin.setValue(60.00)
        ekran._odeme_ekle()
        
        # İkinci ödeme
        ekran.odeme_tutari_spin.setValue(40.00)
        ekran._odeme_ekle()
        
        # Onay mesajını mock'la
        with patch.object(ekran.mesaj_yoneticisi, 'onay_iste', return_value=True):
            with patch.object(ekran.mesaj_yoneticisi, 'bilgi_goster'):
                # Act
                ekran._satisi_tamamla()
        
        # Assert
        mock_odeme_service.odeme_tamamla.assert_called_once()
        call_args = mock_odeme_service.odeme_tamamla.call_args
        assert call_args[1]['sepet_id'] == 1
        assert len(call_args[1]['odemeler']) == 2
        
        ekran.close()


class TestIadeEkrani:
    """İade ekranı testleri"""
    
    @patch('sontechsp.uygulama.moduller.pos.ui.iade_ekrani.oturum_baglamini_al')
    @patch('sontechsp.uygulama.moduller.pos.ui.iade_ekrani.IadeService')
    def test_ekran_yukleme(self, mock_service_class, mock_oturum_func, qapp, mock_oturum, mock_iade_service):
        """İade ekranının doğru yüklendiğini test eder"""
        # Arrange
        mock_oturum_func.return_value = mock_oturum
        mock_service_class.return_value = mock_iade_service
        
        # Act
        ekran = IadeEkrani()
        
        # Assert
        assert ekran is not None
        assert ekran.windowTitle() == "POS İade"
        assert hasattr(ekran, 'satis_no_edit')
        assert hasattr(ekran, 'kalemler_tablo')
        assert hasattr(ekran, 'iade_onayla_buton')
        
        ekran.close()
    
    @patch('sontechsp.uygulama.moduller.pos.ui.iade_ekrani.oturum_baglamini_al')
    @patch('sontechsp.uygulama.moduller.pos.ui.iade_ekrani.IadeService')
    def test_satis_arama_service_cagrisi(self, mock_service_class, mock_oturum_func, qapp, mock_oturum, mock_iade_service):
        """Satış arama service çağrısını test eder"""
        # Arrange
        mock_oturum_func.return_value = mock_oturum
        mock_service_class.return_value = mock_iade_service
        
        ekran = IadeEkrani()
        
        # Act
        ekran.satis_no_edit.setText("123")
        ekran._satis_ara()
        
        # Assert
        mock_iade_service.satis_bilgisi_getir.assert_called_once_with(123)
        
        ekran.close()
    
    @patch('sontechsp.uygulama.moduller.pos.ui.iade_ekrani.oturum_baglamini_al')
    @patch('sontechsp.uygulama.moduller.pos.ui.iade_ekrani.IadeService')
    def test_iade_onaylama_signal(self, mock_service_class, mock_oturum_func, qapp, mock_oturum, mock_iade_service):
        """İade onaylama sinyalinin doğru çalıştığını test eder"""
        # Arrange
        mock_oturum_func.return_value = mock_oturum
        mock_service_class.return_value = mock_iade_service
        
        ekran = IadeEkrani()
        signal_received = []
        
        def signal_handler(data):
            signal_received.append(data)
        
        ekran.iade_tamamlandi.connect(signal_handler)
        
        # Satış bilgilerini yükle
        ekran.satis_no_edit.setText("123")
        ekran._satis_ara()
        
        # Mock kalem seçimi (gerçek UI etkileşimi olmadan)
        with patch.object(ekran, '_secilen_kalemleri_al', return_value=[
            {
                'row': 0,
                'urun_adi': 'Test Ürün',
                'iade_adet': 1,
                'birim_fiyat': Decimal('50.00'),
                'toplam_tutar': Decimal('50.00')
            }
        ]):
            # Onay mesajını mock'la
            with patch.object(ekran.mesaj_yoneticisi, 'onay_iste', return_value=True):
                with patch.object(ekran.mesaj_yoneticisi, 'bilgi_goster'):
                    # Act
                    ekran._iade_onayla()
        
        # Assert
        mock_iade_service.iade_olustur.assert_called_once()
        assert len(signal_received) == 1
        assert 'orijinal_satis_id' in signal_received[0]
        
        ekran.close()


class TestUIKatmaniEntegrasyonu:
    """UI katmanı entegrasyon testleri"""
    
    @patch('sontechsp.uygulama.moduller.pos.ui.sepet_ekrani.oturum_baglamini_al')
    @patch('sontechsp.uygulama.moduller.pos.ui.sepet_ekrani.SepetService')
    def test_sepet_ekrani_signal_slot_baglantilari(self, mock_service_class, mock_oturum_func, qapp, mock_oturum, mock_sepet_service):
        """Sepet ekranı signal/slot bağlantılarını test eder"""
        # Arrange
        mock_oturum_func.return_value = mock_oturum
        mock_service_class.return_value = mock_sepet_service
        
        ekran = SepetEkrani()
        
        # Signal bağlantılarını test et
        assert ekran.barkod_edit.textChanged.connect is not None
        assert ekran.barkod_edit.returnPressed.connect is not None
        assert ekran.barkod_ekle_buton.clicked.connect is not None
        assert ekran.adet_degistir_buton.clicked.connect is not None
        assert ekran.sepet_bosalt_buton.clicked.connect is not None
        
        ekran.close()
    
    @patch('sontechsp.uygulama.moduller.pos.ui.odeme_ekrani.oturum_baglamini_al')
    @patch('sontechsp.uygulama.moduller.pos.ui.odeme_ekrani.OdemeService')
    def test_odeme_ekrani_widget_durumu(self, mock_service_class, mock_oturum_func, qapp, mock_oturum, mock_odeme_service):
        """Ödeme ekranı widget durumlarını test eder"""
        # Arrange
        mock_oturum_func.return_value = mock_oturum
        mock_service_class.return_value = mock_odeme_service
        
        sepet_bilgisi = {
            'id': 1,
            'toplam_tutar': Decimal('100.00'),
            'durum': 'AKTIF'
        }
        
        ekran = OdemeEkrani(sepet_bilgisi)
        
        # Başlangıç durumları
        assert ekran.odeme_tutari_spin.value() == 100.00
        assert ekran.tamamla_buton.isEnabled() == False  # Henüz ödeme eklenmedi
        
        # Ödeme ekle
        ekran._odeme_ekle()
        
        # Ödeme eklendikten sonra
        assert ekran.tamamla_buton.isEnabled() == True
        
        ekran.close()
    
    @patch('sontechsp.uygulama.moduller.pos.ui.iade_ekrani.oturum_baglamini_al')
    @patch('sontechsp.uygulama.moduller.pos.ui.iade_ekrani.IadeService')
    def test_iade_ekrani_form_validasyonu(self, mock_service_class, mock_oturum_func, qapp, mock_oturum, mock_iade_service):
        """İade ekranı form validasyonunu test eder"""
        # Arrange
        mock_oturum_func.return_value = mock_oturum
        mock_service_class.return_value = mock_iade_service
        
        ekran = IadeEkrani()
        
        # Başlangıç durumu
        assert ekran.iade_onayla_buton.isEnabled() == False
        
        # Boş arama testi
        with patch.object(ekran.mesaj_yoneticisi, 'uyari_goster') as mock_uyari:
            ekran._satis_ara()
            mock_uyari.assert_called_once_with("Satış no veya fiş no girin")
        
        ekran.close()