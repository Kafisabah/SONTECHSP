# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_cekirdek_entegrasyon_property
# Description: SONTECHSP çekirdek entegrasyon property-based testleri
# Changelog:
# - 0.1.0: İlk versiyon - Çekirdek entegrasyon property testleri

"""
SONTECHSP Çekirdek Entegrasyon Property-Based Testleri

Bu modül çekirdek sistem entegrasyonu için property-based testleri içerir.
Bağımsızlık ve test edilebilirlik özelliklerini doğrular.
"""

import pytest
import sys
import importlib
import inspect
from hypothesis import given, strategies as st, settings
from typing import List, Set
from unittest.mock import patch, MagicMock

from sontechsp.uygulama.cekirdek import (
    CekirdekSistem, cekirdek_sistem_al, cekirdek_baslat, cekirdek_durdur
)


class TestCekirdekEntegrasyonPropertyTestleri:
    """Çekirdek entegrasyon property-based testleri"""
    
    def setup_method(self):
        """Her test öncesi temizlik"""
        # Global instance'ları temizle
        import sontechsp.uygulama.cekirdek as cekirdek_modulu
        cekirdek_modulu._cekirdek_sistem = None
        
        # Alt modül global instance'larını temizle
        import sontechsp.uygulama.cekirdek.ayarlar as ayarlar_modulu
        import sontechsp.uygulama.cekirdek.kayit as kayit_modulu
        import sontechsp.uygulama.cekirdek.yetki as yetki_modulu
        import sontechsp.uygulama.cekirdek.oturum as oturum_modulu
        
        ayarlar_modulu._ayarlar_yoneticisi = None
        kayit_modulu._kayit_sistemi = None
        yetki_modulu._yetki_kontrolcu = None
        oturum_modulu._oturum_yoneticisi = None
    
    @given(
        test_sayisi=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=50)
    def test_calisma_zamani_bagimsizligi_property(self, test_sayisi: int):
        """
        **Çekirdek Altyapı, Özellik 16: Çalışma zamanı bağımsızlığı**
        **Doğrular: Gereksinim 6.4**
        
        Herhangi bir çekirdek işlev için, dış bağımlılık gerektirmemelidir
        """
        # Çekirdek modüllerin listesi
        cekirdek_moduller = [
            'sontechsp.uygulama.cekirdek.ayarlar',
            'sontechsp.uygulama.cekirdek.kayit',
            'sontechsp.uygulama.cekirdek.hatalar',
            'sontechsp.uygulama.cekirdek.yetki',
            'sontechsp.uygulama.cekirdek.oturum'
        ]
        
        for _ in range(test_sayisi):
            for modul_adi in cekirdek_moduller:
                try:
                    # Modülü import et
                    modul = importlib.import_module(modul_adi)
                    
                    # Özellik: Modül başarıyla import edilebilmeli
                    assert modul is not None
                    
                    # Modülün temel sınıflarını kontrol et
                    siniflar = [obj for name, obj in inspect.getmembers(modul, inspect.isclass)
                              if obj.__module__ == modul_adi]
                    
                    # Özellik: Her modülde en az bir sınıf olmalı
                    assert len(siniflar) > 0
                    
                    # Her sınıfın instance'ı oluşturulabilmeli
                    for sinif in siniflar:
                        if not sinif.__name__.endswith('Hatasi'):  # Hata sınıfları hariç
                            try:
                                # Parametresiz constructor dene
                                instance = sinif()
                                assert instance is not None
                            except TypeError:
                                # Parametreli constructor gerekiyorsa geç
                                pass
                    
                except ImportError as e:
                    pytest.fail(f"Çekirdek modül {modul_adi} import edilemedi: {e}")
                except Exception as e:
                    pytest.fail(f"Çekirdek modül {modul_adi} çalışma zamanı hatası: {e}")
    
    @given(
        test_senaryosu=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=50)
    def test_izole_test_edilebilirlik_property(self, test_senaryosu: int):
        """
        **Çekirdek Altyapı, Özellik 17: İzole test edilebilirlik**
        **Doğrular: Gereksinim 6.5**
        
        Herhangi bir çekirdek modül için, izole test edilebilmelidir
        """
        # Test senaryolarına göre farklı izolasyon testleri
        
        if test_senaryosu == 1:
            # Senaryo 1: Ayarlar modülü izole testi
            from sontechsp.uygulama.cekirdek.ayarlar import AyarlarYoneticisi
            
            # Mock ortam değişkenleri ile test
            with patch.dict('os.environ', {
                'VERITABANI_URL': 'test://localhost',
                'LOG_KLASORU': '/tmp/test',
                'ORTAM': 'test'
            }):
                yonetici = AyarlarYoneticisi()
                
                # Özellik: İzole ortamda çalışabilmeli
                assert yonetici.ayar_oku('ORTAM') == 'test'
                assert yonetici.ayar_dogrula() is True
        
        elif test_senaryosu == 2:
            # Senaryo 2: Kayıt sistemi izole testi
            from sontechsp.uygulama.cekirdek.kayit import KayitSistemi
            
            # Geçici dosya sistemi ile test
            with patch('tempfile.mkdtemp') as mock_temp:
                mock_temp.return_value = '/tmp/test_logs'
                
                kayit = KayitSistemi()
                
                # Özellik: İzole dosya sistemi ile çalışabilmeli
                kayit.info("Test mesajı")
                assert kayit.seviye == "INFO"
        
        elif test_senaryosu == 3:
            # Senaryo 3: Hata sistemi izole testi
            from sontechsp.uygulama.cekirdek.hatalar import (
                SontechHatasi, AlanHatasi, DogrulamaHatasi
            )
            
            # Özellik: Hata sınıfları bağımsız çalışabilmeli
            try:
                raise AlanHatasi("Test alan hatası")
            except SontechHatasi as e:
                assert "Test alan hatası" in str(e)
                assert isinstance(e, AlanHatasi)
        
        elif test_senaryosu == 4:
            # Senaryo 4: Yetki sistemi izole testi
            from sontechsp.uygulama.cekirdek.yetki import YetkiKontrolcu
            
            kontrolcu = YetkiKontrolcu()
            
            # Mock yetki matrisi ile test
            test_matris = {
                'admin': ['okuma', 'yazma', 'silme'],
                'kullanici': ['okuma']
            }
            
            kontrolcu.yetki_matrisi_yukle(test_matris)
            
            # Özellik: İzole yetki matrisi ile çalışabilmeli
            assert kontrolcu.izin_var_mi('admin', 'yazma') is True
            assert kontrolcu.izin_var_mi('kullanici', 'silme') is False
        
        elif test_senaryosu == 5:
            # Senaryo 5: Oturum sistemi izole testi
            from sontechsp.uygulama.cekirdek.oturum import OturumYoneticisi
            
            yonetici = OturumYoneticisi()
            
            # Özellik: İzole oturum yönetimi çalışabilmeli
            oturum = yonetici.oturum_baslat(
                kullanici_id=1,
                kullanici_adi="test_user",
                firma_id=1,
                magaza_id=1
            )
            
            assert oturum is not None
            assert yonetici.oturum_aktif_mi() is True
            
            # Temizlik
            assert yonetici.oturum_sonlandir() is True
            assert yonetici.oturum_aktif_mi() is False
    
    @given(
        baslat_durdur_sayisi=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=30)
    def test_cekirdek_sistem_entegrasyon_property(self, baslat_durdur_sayisi: int):
        """
        Çekirdek sistem entegrasyonu property testi
        
        Herhangi bir başlat/durdur döngüsü için sistem tutarlı çalışmalıdır
        """
        # Mock ayarlar ile test ortamı hazırla
        with patch.dict('os.environ', {
            'VERITABANI_URL': 'test://localhost',
            'LOG_KLASORU': '/tmp/test',
            'ORTAM': 'test'
        }):
            
            for i in range(baslat_durdur_sayisi):
                sistem = cekirdek_sistem_al()
                
                # Özellik: Sistem başlatılabilmeli
                baslat_basarili = sistem.baslat()
                assert baslat_basarili is True
                assert sistem.baslatildi_mi() is True
                
                # Özellik: Durum bilgisi alınabilmeli
                durum = sistem.durum_bilgisi_al()
                assert durum['baslatildi'] is True
                assert durum['ayarlar_yuklendi'] is True
                assert durum['kayit_aktif'] is True
                
                # Özellik: Sağlık kontrolü yapılabilmeli
                saglik = sistem.saglik_kontrolu()
                assert saglik is True
                
                # Özellik: Sistem durdurulabilmeli
                durdur_basarili = sistem.durdur()
                assert durdur_basarili is True
                assert sistem.baslatildi_mi() is False
                
                # Yeni instance için temizlik
                import sontechsp.uygulama.cekirdek as cekirdek_modulu
                cekirdek_modulu._cekirdek_sistem = None
    
    def test_dis_bagimliliklarin_olmamasi_property(self):
        """
        Çekirdek modüllerin dış bağımlılıklarının olmaması property testi
        
        Çekirdek modüller sadece Python standart kütüphanelerini kullanmalıdır
        """
        # İzin verilen standart kütüphaneler
        izinli_moduller = {
            'os', 'sys', 'datetime', 'typing', 'dataclasses', 'threading',
            'logging', 'tempfile', 'pathlib', 'json', 'configparser',
            'inspect', 'importlib', 'unittest', 'collections', 'functools',
            'itertools', 'copy', 'weakref', 'abc', 'enum'
        }
        
        # Çekirdek modüllerin import listelerini kontrol et
        cekirdek_moduller = [
            'sontechsp.uygulama.cekirdek.ayarlar',
            'sontechsp.uygulama.cekirdek.kayit',
            'sontechsp.uygulama.cekirdek.hatalar',
            'sontechsp.uygulama.cekirdek.yetki',
            'sontechsp.uygulama.cekirdek.oturum'
        ]
        
        for modul_adi in cekirdek_moduller:
            try:
                modul = importlib.import_module(modul_adi)
                
                # Modül kaynak kodunu al
                kaynak_dosya = inspect.getfile(modul)
                
                with open(kaynak_dosya, 'r', encoding='utf-8') as f:
                    kaynak_kod = f.read()
                
                # Import satırlarını bul
                import_satirlari = []
                for satir in kaynak_kod.split('\n'):
                    satir = satir.strip()
                    if satir.startswith('import ') or satir.startswith('from '):
                        import_satirlari.append(satir)
                
                # Her import'u kontrol et
                for import_satir in import_satirlari:
                    # Kendi modüllerini hariç tut
                    if 'sontechsp' in import_satir:
                        continue
                    
                    # Import edilen modül adını çıkar
                    if import_satir.startswith('import '):
                        modul_adi_import = import_satir.replace('import ', '').split('.')[0]
                    elif import_satir.startswith('from '):
                        modul_adi_import = import_satir.split(' ')[1].split('.')[0]
                    else:
                        continue
                    
                    # Özellik: Sadece izinli modüller kullanılmalı
                    assert modul_adi_import in izinli_moduller, \
                        f"Çekirdek modül {modul_adi} izinsiz bağımlılık kullanıyor: {modul_adi_import}"
                        
            except Exception as e:
                pytest.fail(f"Bağımlılık kontrolü hatası {modul_adi}: {e}")