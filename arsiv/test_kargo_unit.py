# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_kargo_unit
# Description: Kargo modülü unit testleri
# Changelog:
# - Unit testler eklendi
# - Edge case'ler test edildi

"""
Kargo modülü unit testleri.

Bu modül, spesifik örnekler ve edge case'leri test eder.
"""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal

from uygulama.moduller.kargo.dto import KargoEtiketOlusturDTO
from uygulama.moduller.kargo.sabitler import (
    KaynakTurleri, EtiketDurumlari, Tasiyicilar, MAKSIMUM_DENEME_SAYISI
)
from uygulama.moduller.kargo.servisler import (
    KargoServisi, DogrulamaHatasi, BenzersizlikHatasi
)
from uygulama.moduller.kargo.tasiyici_fabrikasi import TasiyiciFabrikasi
from uygulama.moduller.kargo.dummy_tasiyici import DummyTasiyici


class TestKargoUnit:
    """Kargo modülü unit testleri."""
    
    def test_gecersiz_veri_ile_etiket_olusturma(self):
        """
        Geçersiz veri ile etiket oluşturma testleri.
        **Validates: Requirements 1.3, 2.3**
        """
        mock_session = Mock()
        
        with patch('uygulama.moduller.kargo.servisler.KargoDeposu'):
            servis = KargoServisi(mock_session)
            
            # Boş alıcı adı
            dto = KargoEtiketOlusturDTO(
                kaynak_turu=KaynakTurleri.POS_SATIS,
                kaynak_id=1,
                alici_ad="",  # Boş
                alici_telefon="5551234567",
                alici_adres="Test Adres",
                alici_il="İstanbul",
                alici_ilce="Kadıköy",
                tasiyici=Tasiyicilar.YURTICI
            )
            
            with pytest.raises(DogrulamaHatasi, match="Zorunlu alan eksik: alici_ad"):
                servis.etiket_olustur(dto)
            
            # Negatif kaynak ID
            dto.alici_ad = "Test Alıcı"
            dto.kaynak_id = -1
            
            with pytest.raises(DogrulamaHatasi, match="Kaynak ID pozitif olmalıdır"):
                servis.etiket_olustur(dto)
            
            # Negatif paket ağırlığı
            dto.kaynak_id = 1
            dto.paket_agirlik_kg = Decimal('-1.0')
            
            with pytest.raises(DogrulamaHatasi, match="Paket ağırlığı pozitif olmalıdır"):
                servis.etiket_olustur(dto)
    
    def test_benzersizlik_kisitlama(self):
        """
        Benzersizlik kısıtlama testleri.
        **Validates: Requirements 1.3, 2.3**
        """
        mock_session = Mock()
        mock_depo = Mock()
        
        with patch('uygulama.moduller.kargo.servisler.KargoDeposu') as mock_depo_class:
            mock_depo_class.return_value = mock_depo
            
            # Mevcut etiket var
            mock_mevcut_etiket = Mock()
            mock_depo.etiket_kaynaktan_bul.return_value = mock_mevcut_etiket
            
            dto = KargoEtiketOlusturDTO(
                kaynak_turu=KaynakTurleri.POS_SATIS,
                kaynak_id=1,
                alici_ad="Test Alıcı",
                alici_telefon="5551234567",
                alici_adres="Test Adres",
                alici_il="İstanbul",
                alici_ilce="Kadıköy",
                tasiyici=Tasiyicilar.YURTICI
            )
            
            servis = KargoServisi(mock_session)
            
            with pytest.raises(BenzersizlikHatasi, match="Bu kaynak için zaten etiket mevcut"):
                servis.etiket_olustur(dto)
    
    def test_maksimum_deneme_sayisi(self):
        """
        Maksimum deneme sayısı testleri.
        **Validates: Requirements 4.4, 2.5**
        """
        mock_session = Mock()
        mock_depo = Mock()
        
        with patch('uygulama.moduller.kargo.servisler.KargoDeposu') as mock_depo_class:
            mock_depo_class.return_value = mock_depo
            
            # Maksimum deneme sayısına ulaşmış etiket
            mock_etiket = Mock()
            mock_etiket.id = 1
            mock_etiket.deneme_sayisi = MAKSIMUM_DENEME_SAYISI
            mock_depo.bekleyen_etiketleri_al.return_value = [mock_etiket]
            
            servis = KargoServisi(mock_session)
            sonuc = servis.bekleyen_etiketleri_isle(limit=1)
            
            # Maksimum deneme aşıldığı için işlem yapılmamalı
            assert sonuc['maksimum_deneme_asilan'] == 1
            assert sonuc['basarili'] == 0
            assert sonuc['basarisiz'] == 0
            
            # Deneme sayısı artırılmamalı
            mock_depo.deneme_sayisi_artir.assert_not_called()
    
    def test_dummy_tasiyici_edge_cases(self):
        """
        DummyTasiyici edge case testleri.
        """
        # Çok düşük başarı oranı
        dummy = DummyTasiyici(basari_orani=0.0)
        
        payload = {
            'alici_ad': 'Test Alıcı',
            'alici_telefon': '5551234567',
            'alici_adres': 'Test Adres',
            'alici_il': 'İstanbul',
            'alici_ilce': 'Kadıköy',
            'paket_agirlik_kg': Decimal('1.0')
        }
        
        # Her zaman hata dönmeli
        for _ in range(10):
            sonuc = dummy.etiket_olustur(payload)
            assert sonuc['durum'] == EtiketDurumlari.HATA
            assert sonuc['takip_no'] is None
        
        # Geçersiz takip numarası ile durum sorgulama
        durum = dummy.durum_sorgula('')
        assert durum['durum'] == 'BILINMIYOR'
        assert 'Geçersiz takip numarası' in durum['aciklama']
        
        # Çok kısa takip numarası
        durum = dummy.durum_sorgula('123')
        assert durum['durum'] == 'BILINMIYOR'
    
    def test_tasiyici_fabrikasi_edge_cases(self):
        """
        TasiyiciFabrikasi edge case testleri.
        """
        # Geçersiz taşıyıcı kodu
        with pytest.raises(ValueError, match="Desteklenmeyen taşıyıcı kodu"):
            TasiyiciFabrikasi.tasiyici_olustur("GECERSIZ_TASIYICI")
        
        # Desteklenen taşıyıcılar listesi
        desteklenenler = TasiyiciFabrikasi.desteklenen_tasiyicilar()
        assert len(desteklenenler) == 5
        assert all(kod in Tasiyicilar.tum_tasiyicilar() for kod in desteklenenler)
        
        # Yeni taşıyıcı ekleme - geçersiz sınıf
        with pytest.raises(ValueError, match="TasiyiciArayuzu'nden türetilmelidir"):
            TasiyiciFabrikasi.tasiyici_ekle("TEST", str)  # str TasiyiciArayuzu'nden türemez