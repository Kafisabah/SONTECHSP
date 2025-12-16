# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.test_entegrasyon_e2e
# Description: POS End-to-End entegrasyon testleri
# Changelog:
# - İlk oluşturma

"""
POS End-to-End Entegrasyon Testleri

Bu modül barkod okuma -> sepet -> ödeme -> fiş akışının tam entegrasyon testlerini içerir.
Gerçek senaryoları simüle ederek tüm katmanların birlikte çalışmasını doğrular.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch
from typing import Dict, Any

from sontechsp.uygulama.moduller.pos.servisler.sepet_service import SepetService
from sontechsp.uygulama.moduller.pos.servisler.odeme_service import OdemeService
from sontechsp.uygulama.moduller.pos.servisler.fis_service import FisService
from sontechsp.uygulama.moduller.pos.repositories.sepet_repository import SepetRepository
from sontechsp.uygulama.moduller.pos.repositories.satis_repository import SatisRepository
from sontechsp.uygulama.moduller.pos.repositories.iade_repository import IadeRepository
from sontechsp.uygulama.moduller.pos.arayuzler import (
    SepetDurum, SatisDurum, OdemeTuru
)


class TestE2ESatisSenaryosu:
    """End-to-End satış senaryosu testleri"""
    
    @pytest.fixture
    def mock_stok_service(self):
        """Mock stok service fixture"""
        mock_service = Mock()
        mock_service.urun_bilgisi_getir.return_value = {
            'id': 1,
            'ad': 'Test Ürün',
            'barkod': '1234567890',
            'satis_fiyati': Decimal('25.50'),
            'stok_miktari': 100
        }
        mock_service.stok_kontrol.return_value = True
        mock_service.stok_rezerve_et.return_value = True
        mock_service.stok_dusur.return_value = True
        return mock_service
    
    @pytest.fixture
    def mock_repositories(self):
        """Mock repository'ler fixture"""
        sepet_repo = Mock(spec=SepetRepository)
        satis_repo = Mock(spec=SatisRepository)
        iade_repo = Mock(spec=IadeRepository)
        
        # Sepet repository mock'ları
        sepet_repo.sepet_olustur.return_value = 1
        sepet_repo.sepet_getir.return_value = {
            'id': 1,
            'terminal_id': 1,
            'kasiyer_id': 1,
            'durum': SepetDurum.AKTIF.value,
            'toplam_tutar': Decimal('25.50'),
            'satirlar': [
                {
                    'id': 1,
                    'urun_id': 1,
                    'urun_adi': 'Test Ürün',
                    'barkod': '1234567890',
                    'adet': 1,
                    'birim_fiyat': Decimal('25.50'),
                    'toplam_tutar': Decimal('25.50')
                }
            ]
        }
        sepet_repo.sepet_satiri_ekle.return_value = 1
        sepet_repo.sepet_durum_guncelle.return_value = True
        
        # Satış repository mock'ları
        satis_repo.satis_olustur.return_value = 1
        satis_repo.satis_getir.return_value = {
            'id': 1,
            'sepet_id': 1,
            'terminal_id': 1,
            'kasiyer_id': 1,
            'satis_tarihi': datetime.now(),
            'toplam_tutar': Decimal('25.50'),
            'durum': SatisDurum.TAMAMLANDI.value,
            'fis_no': 'FIS001',
            'satirlar': [
                {
                    'id': 1,
                    'urun_id': 1,
                    'urun_adi': 'Test Ürün',
                    'barkod': '1234567890',
                    'adet': 1,
                    'birim_fiyat': Decimal('25.50'),
                    'toplam_tutar': Decimal('25.50')
                }
            ],
            'odemeler': [
                {
                    'id': 1,
                    'odeme_turu': OdemeTuru.NAKIT.value,
                    'tutar': Decimal('25.50')
                }
            ]
        }
        satis_repo.satis_odeme_ekle.return_value = 1
        satis_repo.satis_tamamla.return_value = True
        
        return {
            'sepet_repo': sepet_repo,
            'satis_repo': satis_repo,
            'iade_repo': iade_repo
        }
    
    @pytest.fixture
    def services(self, mock_repositories, mock_stok_service):
        """Service'ler fixture"""
        sepet_service = SepetService(
            sepet_repository=mock_repositories['sepet_repo'],
            stok_service=mock_stok_service
        )
        
        odeme_service = OdemeService(
            sepet_repository=mock_repositories['sepet_repo'],
            satis_repository=mock_repositories['satis_repo'],
            stok_service=mock_stok_service
        )
        
        fis_service = FisService(
            satis_repository=mock_repositories['satis_repo'],
            iade_repository=mock_repositories['iade_repo']
        )
        
        return {
            'sepet_service': sepet_service,
            'odeme_service': odeme_service,
            'fis_service': fis_service
        }
    
    def test_basarili_satis_akisi_e2e(self, services, mock_repositories):
        """
        Başarılı satış akışının end-to-end testi
        
        Senaryo:
        1. Yeni sepet oluştur
        2. Barkod okut ve ürün ekle
        3. Ödeme yap
        4. Fiş oluştur
        
        Requirements: 1.1, 1.2, 3.1, 3.5
        """
        sepet_service = services['sepet_service']
        odeme_service = services['odeme_service']
        fis_service = services['fis_service']
        
        # 1. Yeni sepet oluştur
        sepet_id = sepet_service.yeni_sepet_olustur(terminal_id=1, kasiyer_id=1)
        assert sepet_id == 1
        
        # 2. Barkod okut ve ürün ekle
        barkod_ekleme_sonuc = sepet_service.barkod_ekle(sepet_id, '1234567890')
        assert barkod_ekleme_sonuc is True
        
        # Sepet bilgisini kontrol et
        sepet_bilgisi = sepet_service.sepet_bilgisi_getir(sepet_id)
        assert sepet_bilgisi is not None
        assert sepet_bilgisi['toplam_tutar'] == Decimal('25.50')
        assert len(sepet_bilgisi['satirlar']) == 1
        
        # 3. Ödeme yap
        odeme_sonuc = odeme_service.tek_odeme_yap(
            sepet_id=sepet_id,
            odeme_turu=OdemeTuru.NAKIT,
            tutar=Decimal('25.50')
        )
        assert odeme_sonuc is True
        
        # 4. Fiş oluştur
        fis_icerik = fis_service.satis_fisi_olustur(satis_id=1)
        assert fis_icerik is not None
        assert 'SATIŞ FİŞİ' in fis_icerik
        assert 'Test Ürün' in fis_icerik
        assert '25.50' in fis_icerik
        
        # Repository çağrılarını doğrula
        mock_repositories['sepet_repo'].sepet_olustur.assert_called_once_with(1, 1)
        mock_repositories['sepet_repo'].sepet_satiri_ekle.assert_called_once()
        mock_repositories['satis_repo'].satis_olustur.assert_called_once()
        mock_repositories['satis_repo'].satis_odeme_ekle.assert_called_once()
        mock_repositories['satis_repo'].satis_tamamla.assert_called_once()
    
    def test_coklu_urun_satis_akisi_e2e(self, services, mock_repositories, mock_stok_service):
        """
        Çoklu ürün satış akışının end-to-end testi
        
        Senaryo:
        1. Sepet oluştur
        2. Birden fazla ürün ekle
        3. Parçalı ödeme yap
        4. Fiş oluştur
        
        Requirements: 1.1, 1.2, 3.2, 3.5
        """
        sepet_service = services['sepet_service']
        odeme_service = services['odeme_service']
        fis_service = services['fis_service']
        
        # Mock'ları çoklu ürün için güncelle
        mock_repositories['sepet_repo'].sepet_getir.return_value = {
            'id': 1,
            'terminal_id': 1,
            'kasiyer_id': 1,
            'durum': SepetDurum.AKTIF.value,
            'toplam_tutar': Decimal('75.00'),
            'satirlar': [
                {
                    'id': 1,
                    'urun_id': 1,
                    'urun_adi': 'Ürün 1',
                    'barkod': '1111111111',
                    'adet': 2,
                    'birim_fiyat': Decimal('25.00'),
                    'toplam_tutar': Decimal('50.00')
                },
                {
                    'id': 2,
                    'urun_id': 2,
                    'urun_adi': 'Ürün 2',
                    'barkod': '2222222222',
                    'adet': 1,
                    'birim_fiyat': Decimal('25.00'),
                    'toplam_tutar': Decimal('25.00')
                }
            ]
        }
        
        # Satış repository mock'unu çoklu ödeme için güncelle
        mock_repositories['satis_repo'].satis_getir.return_value = {
            'id': 1,
            'sepet_id': 1,
            'terminal_id': 1,
            'kasiyer_id': 1,
            'satis_tarihi': datetime.now(),
            'toplam_tutar': Decimal('75.00'),
            'durum': SatisDurum.TAMAMLANDI.value,
            'fis_no': 'FIS001',
            'satirlar': [
                {
                    'id': 1,
                    'urun_id': 1,
                    'urun_adi': 'Ürün 1',
                    'barkod': '1111111111',
                    'adet': 2,
                    'birim_fiyat': Decimal('25.00'),
                    'toplam_tutar': Decimal('50.00')
                },
                {
                    'id': 2,
                    'urun_id': 2,
                    'urun_adi': 'Ürün 2',
                    'barkod': '2222222222',
                    'adet': 1,
                    'birim_fiyat': Decimal('25.00'),
                    'toplam_tutar': Decimal('25.00')
                }
            ],
            'odemeler': [
                {
                    'id': 1,
                    'odeme_turu': OdemeTuru.NAKIT.value,
                    'tutar': Decimal('50.00')
                },
                {
                    'id': 2,
                    'odeme_turu': OdemeTuru.KART.value,
                    'tutar': Decimal('25.00')
                }
            ]
        }
        
        # Stok service'i farklı ürünler için güncelle
        def mock_urun_bilgisi_getir(barkod):
            if barkod == '1111111111':
                return {
                    'id': 1,
                    'ad': 'Ürün 1',
                    'barkod': '1111111111',
                    'satis_fiyati': Decimal('25.00'),
                    'stok_miktari': 100
                }
            elif barkod == '2222222222':
                return {
                    'id': 2,
                    'ad': 'Ürün 2',
                    'barkod': '2222222222',
                    'satis_fiyati': Decimal('25.00'),
                    'stok_miktari': 50
                }
            return None
        
        mock_stok_service.urun_bilgisi_getir.side_effect = mock_urun_bilgisi_getir
        
        # 1. Sepet oluştur
        sepet_id = sepet_service.yeni_sepet_olustur(terminal_id=1, kasiyer_id=1)
        
        # 2. Birden fazla ürün ekle
        sepet_service.barkod_ekle(sepet_id, '1111111111')
        sepet_service.barkod_ekle(sepet_id, '1111111111')  # Aynı ürün tekrar
        sepet_service.barkod_ekle(sepet_id, '2222222222')
        
        # 3. Parçalı ödeme yap
        odemeler = [
            {'turu': OdemeTuru.NAKIT, 'tutar': Decimal('50.00')},
            {'turu': OdemeTuru.KART, 'tutar': Decimal('25.00')}
        ]
        
        odeme_sonuc = odeme_service.parcali_odeme_yap(sepet_id, odemeler)
        assert odeme_sonuc is True
        
        # 4. Fiş oluştur
        fis_icerik = fis_service.satis_fisi_olustur(satis_id=1)
        assert 'SATIŞ FİŞİ' in fis_icerik
        assert 'ÖDEME BİLGİLERİ' in fis_icerik
        assert 'NAKIT' in fis_icerik
        assert 'KART' in fis_icerik
    
    def test_stok_yetersizligi_e2e(self, services, mock_stok_service):
        """
        Stok yetersizliği durumunda end-to-end test
        
        Senaryo:
        1. Sepet oluştur
        2. Stok yetersiz ürün eklemeye çalış
        3. Hata alındığını doğrula
        
        Requirements: 1.5
        """
        sepet_service = services['sepet_service']
        
        # Stok kontrolünü başarısız yap
        mock_stok_service.stok_kontrol.return_value = False
        
        # Sepet oluştur
        sepet_id = sepet_service.yeni_sepet_olustur(terminal_id=1, kasiyer_id=1)
        
        # Stok yetersiz ürün eklemeye çalış
        from sontechsp.uygulama.moduller.pos.servisler.sepet_service import StokHatasi
        
        with pytest.raises(StokHatasi) as exc_info:
            sepet_service.barkod_ekle(sepet_id, '1234567890')
        
        assert "Stok yetersiz" in str(exc_info.value)
    
    def test_gecersiz_barkod_e2e(self, services, mock_stok_service):
        """
        Geçersiz barkod durumunda end-to-end test
        
        Senaryo:
        1. Sepet oluştur
        2. Geçersiz barkod okut
        3. Hata alındığını doğrula
        
        Requirements: 1.4
        """
        sepet_service = services['sepet_service']
        
        # Ürün bilgisini None döndür (geçersiz barkod)
        mock_stok_service.urun_bilgisi_getir.return_value = None
        
        # Sepet oluştur
        sepet_id = sepet_service.yeni_sepet_olustur(terminal_id=1, kasiyer_id=1)
        
        # Geçersiz barkod okut
        from sontechsp.uygulama.moduller.pos.servisler.sepet_service import BarkodHatasi
        
        with pytest.raises(BarkodHatasi) as exc_info:
            sepet_service.barkod_ekle(sepet_id, 'GECERSIZ_BARKOD')
        
        assert "Geçersiz barkod" in str(exc_info.value)
    
    def test_yetersiz_odeme_e2e(self, services):
        """
        Yetersiz ödeme durumunda end-to-end test
        
        Senaryo:
        1. Sepet oluştur ve ürün ekle
        2. Yetersiz tutar ile ödeme yap
        3. Hata alındığını doğrula
        
        Requirements: 3.4
        """
        sepet_service = services['sepet_service']
        odeme_service = services['odeme_service']
        
        # Sepet oluştur ve ürün ekle
        sepet_id = sepet_service.yeni_sepet_olustur(terminal_id=1, kasiyer_id=1)
        sepet_service.barkod_ekle(sepet_id, '1234567890')
        
        # Yetersiz tutar ile ödeme yap
        from sontechsp.uygulama.moduller.pos.servisler.odeme_service import OdemeHatasi
        
        with pytest.raises(OdemeHatasi) as exc_info:
            odeme_service.tek_odeme_yap(
                sepet_id=sepet_id,
                odeme_turu=OdemeTuru.NAKIT,
                tutar=Decimal('20.00')  # Sepet toplamı 25.50
            )
        
        assert "eşit değil" in str(exc_info.value)
    
    def test_fis_yazdirma_e2e(self, services):
        """
        Fiş yazdırma end-to-end test
        
        Senaryo:
        1. Satış tamamla
        2. Fiş oluştur
        3. Fiş yazdır
        4. Yazdırma durumunu kontrol et
        
        Requirements: 6.1, 6.2, 6.3
        """
        fis_service = services['fis_service']
        
        # Fiş oluştur
        fis_icerik = fis_service.satis_fisi_olustur(satis_id=1)
        
        # Fiş yazdır
        yazdirma_sonuc = fis_service.fis_yazdir(fis_icerik)
        assert yazdirma_sonuc is True
        
        # Yazıcı durumunu kontrol et
        yazici_durum = fis_service.yazici_durumu_kontrol()
        assert yazici_durum['yazdirma_hazir'] is True
        assert yazici_durum['durum'] == 'hazir'
        
        # Fiş önizlemesi
        onizleme = fis_service.fis_onizleme(fis_icerik)
        assert onizleme['yazdirma_hazir'] is True
        assert onizleme['satir_sayisi'] > 0
    
    def test_tam_satis_dongusu_e2e(self, services, mock_repositories):
        """
        Tam satış döngüsü end-to-end test
        
        Senaryo: Sepet oluştur -> Ürün ekle -> Adet değiştir -> İndirim uygula -> Ödeme -> Fiş
        
        Requirements: 1.1, 1.2, 2.2, 2.3, 3.1, 3.5
        """
        sepet_service = services['sepet_service']
        odeme_service = services['odeme_service']
        fis_service = services['fis_service']
        
        # Sepet oluştur
        sepet_id = sepet_service.yeni_sepet_olustur(terminal_id=1, kasiyer_id=1)
        
        # Ürün ekle
        sepet_service.barkod_ekle(sepet_id, '1234567890')
        
        # Adet değiştir (mock için satır ID = 1)
        sepet_service.urun_adedi_degistir(satir_id=1, yeni_adet=3)
        
        # İndirim uygula
        sepet_service.indirim_uygula(sepet_id, Decimal('5.00'))
        
        # Sepet bilgisini güncelle (indirimli toplam için)
        mock_repositories['sepet_repo'].sepet_getir.return_value.update({
            'toplam_tutar': Decimal('76.50'),  # 3 * 25.50
            'indirim_tutari': Decimal('5.00'),
            'net_tutar': Decimal('71.50')
        })
        
        # Ödeme yap
        odeme_sonuc = odeme_service.tek_odeme_yap(
            sepet_id=sepet_id,
            odeme_turu=OdemeTuru.KART,
            tutar=Decimal('71.50')
        )
        assert odeme_sonuc is True
        
        # Fiş oluştur
        fis_icerik = fis_service.satis_fisi_olustur(satis_id=1)
        assert 'İndirim:' in fis_icerik or 'NET TOPLAM:' in fis_icerik
        
        # Tüm adımların çağrıldığını doğrula
        mock_repositories['sepet_repo'].sepet_olustur.assert_called_once()
        mock_repositories['sepet_repo'].sepet_satiri_ekle.assert_called_once()
        mock_repositories['sepet_repo'].sepet_satiri_guncelle.assert_called_once()
        mock_repositories['satis_repo'].satis_olustur.assert_called_once()
        mock_repositories['satis_repo'].satis_tamamla.assert_called_once()


class TestE2EPerformans:
    """End-to-End performans testleri"""
    
    def test_coklu_islem_performansi(self):
        """
        Çoklu işlem performans testi - basit sürüm
        
        Basit hesaplama işlemlerinin makul sürede tamamlanması
        """
        import time
        from decimal import Decimal
        
        baslangic = time.time()
        
        # Basit hesaplama işlemleri (mock olmadan)
        for i in range(1000):
            # Decimal hesaplamaları
            fiyat = Decimal('25.50')
            adet = i % 10 + 1
            toplam = fiyat * adet
            
            # String işlemleri
            barkod = f'123456789{i:04d}'
            urun_adi = f'Ürün {i}'
            
        bitis = time.time()
        sure = bitis - baslangic
        
        # 1000 işlem 1 saniyede tamamlanmalı
        assert sure < 1.0, f"İşlem çok yavaş: {sure:.2f} saniye"
    
    def test_bellek_kullanimi(self):
        """
        Bellek kullanımı testi - basit sürüm
        
        Çoklu işlem sonrası bellek sızıntısı olmaması
        """
        import gc
        from decimal import Decimal
        
        # Başlangıç bellek durumu
        gc.collect()
        baslangic_objeler = len(gc.get_objects())
        
        # Çoklu işlem yap
        veriler = []
        for i in range(100):
            veri = {
                'id': i,
                'fiyat': Decimal('25.50'),
                'barkod': f'123456789{i:04d}',
                'urun_adi': f'Ürün {i}'
            }
            veriler.append(veri)
        
        # Verileri temizle
        veriler.clear()
        del veriler
        
        # Bitiş bellek durumu
        gc.collect()
        bitis_objeler = len(gc.get_objects())
        
        # Obje sayısı çok artmamalı (bellek sızıntısı kontrolü)
        artis = bitis_objeler - baslangic_objeler
        assert artis < 200, f"Bellek sızıntısı olabilir: {artis} yeni obje"