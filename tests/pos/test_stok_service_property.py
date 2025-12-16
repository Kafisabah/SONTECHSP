# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.test_stok_service_property
# Description: POS stok servisi özellik testleri
# Changelog:
# - İlk oluşturma

"""
POS Stok Servisi Özellik Testleri

Bu modül POS stok servisinin doğruluk özelliklerini test eder.
Property-based testing ile stok yönetimi işlemlerinin tutarlılığını doğrular.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, Optional

from sontechsp.uygulama.moduller.pos.servisler.stok_service import StokService
from sontechsp.uygulama.moduller.pos.arayuzler import StokKilitTuru
from sontechsp.uygulama.cekirdek.hatalar import POSHatasi
from sontechsp.uygulama.moduller.stok.hatalar.stok_hatalari import (
    StokValidationError, StokYetersizError
)


class TestStokServiceProperty:
    """POS stok servisi özellik testleri"""
    
    def _create_mock_dependencies(self):
        """Mock bağımlılıkları oluşturur"""
        mock_entegrasyon = Mock()
        mock_rezervasyon = Mock()
        mock_barkod = Mock()
        mock_bakiye_repo = Mock()
        
        return {
            'entegrasyon': mock_entegrasyon,
            'rezervasyon': mock_rezervasyon,
            'barkod': mock_barkod,
            'bakiye_repo': mock_bakiye_repo
        }
    
    def _create_stok_service(self, mock_dependencies):
        """Stok servisi oluşturur"""
        return StokService(
            stok_entegrasyon_service=mock_dependencies['entegrasyon'],
            rezervasyon_service=mock_dependencies['rezervasyon'],
            barkod_service=mock_dependencies['barkod'],
            bakiye_repository=mock_dependencies['bakiye_repo']
        )
    
    # Özellik 4: Stok Yetersizliği Kontrolü
    @given(
        urun_id=st.integers(min_value=1, max_value=10000),
        magaza_id=st.integers(min_value=1, max_value=100),
        talep_adet=st.integers(min_value=1, max_value=1000),
        mevcut_stok=st.integers(min_value=0, max_value=500)
    )
    @settings(max_examples=100)
    def test_property_4_stok_yetersizligi_kontrolu(self, urun_id, magaza_id, talep_adet, mevcut_stok):
        """
        **Feature: pos-cekirdek-modulu, Property 4: Stok Yetersizliği Kontrolü**
        
        Herhangi bir stok yetersizliği durumunda, sistem uyarı vermeli ve satışa izin vermemeli
        **Validates: Requirements 1.5**
        """
        # Mock bağımlılıkları oluştur
        mock_dependencies = self._create_mock_dependencies()
        stok_service = self._create_stok_service(mock_dependencies)
        
        # Mock stok durumu ayarla
        mock_dependencies['entegrasyon'].gercek_zamanli_stok_durumu_getir.return_value = {
            'urun_id': urun_id,
            'magaza_id': magaza_id,
            'kullanilabilir_stok': Decimal(str(mevcut_stok))
        }
        
        # Stok kontrolü yap
        sonuc = stok_service.stok_kontrol(urun_id, magaza_id, talep_adet)
        
        # Özellik doğrulaması: Yetersiz stok durumunda False dönmeli
        if mevcut_stok < talep_adet:
            assert sonuc is False, f"Yetersiz stok durumunda False dönmeliydi. Mevcut: {mevcut_stok}, Talep: {talep_adet}"
        else:
            assert sonuc is True, f"Yeterli stok durumunda True dönmeliydi. Mevcut: {mevcut_stok}, Talep: {talep_adet}"
    
    # Özellik 25: Eş Zamanlı Stok Kilitleme
    @given(
        urun_id=st.integers(min_value=1, max_value=10000),
        magaza_id=st.integers(min_value=1, max_value=100),
        depo_id=st.one_of(st.none(), st.integers(min_value=1, max_value=50))
    )
    @settings(max_examples=100)
    def test_property_25_es_zamanli_stok_kilitleme(self, urun_id, magaza_id, depo_id):
        """
        **Feature: pos-cekirdek-modulu, Property 25: Eş Zamanlı Stok Kilitleme**
        
        Herhangi bir eş zamanlı satış durumu için, birden fazla terminal aynı ürünü satmaya 
        çalıştığında sistem stok kilitleme uygulamalı
        **Validates: Requirements 7.1**
        """
        # Mock bağımlılıkları oluştur
        mock_dependencies = self._create_mock_dependencies()
        stok_service = self._create_stok_service(mock_dependencies)
        
        # İlk kilitleme başarılı olmalı
        ilk_kilit = stok_service.es_zamanli_stok_kilitle(urun_id, magaza_id, depo_id)
        assert ilk_kilit is True, "İlk stok kilitleme başarılı olmalıydı"
        
        # İkinci kilitleme başarısız olmalı (aynı kaynak için)
        ikinci_kilit = stok_service.es_zamanli_stok_kilitle(urun_id, magaza_id, depo_id)
        assert ikinci_kilit is False, "İkinci stok kilitleme başarısız olmalıydı (zaten kilitli)"
        
        # Kilidi serbest bırak
        serbest_birakma = stok_service.stok_kilidini_serbest_birak(urun_id, magaza_id, depo_id)
        assert serbest_birakma is True, "Stok kilidi serbest bırakılmalıydı"
        
        # Serbest bırakıldıktan sonra tekrar kilitleme başarılı olmalı
        ucuncu_kilit = stok_service.es_zamanli_stok_kilitle(urun_id, magaza_id, depo_id)
        assert ucuncu_kilit is True, "Serbest bırakıldıktan sonra kilitleme başarılı olmalıydı"
        
        # Temizlik
        stok_service.stok_kilidini_serbest_birak(urun_id, magaza_id, depo_id)
    
    # Özellik 26: Güncel Stok Kontrolü
    @given(
        urun_id=st.integers(min_value=1, max_value=10000),
        magaza_id=st.integers(min_value=1, max_value=100),
        depo_id=st.one_of(st.none(), st.integers(min_value=1, max_value=50)),
        stok_miktari=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=100)
    def test_property_26_guncel_stok_kontrolu(self, urun_id, magaza_id, depo_id, stok_miktari):
        """
        **Feature: pos-cekirdek-modulu, Property 26: Güncel Stok Kontrolü**
        
        Herhangi bir stok kontrolü için, sistem güncel stok durumunu Stok_Servisi'nden almalı
        **Validates: Requirements 7.2**
        """
        # Mock bağımlılıkları oluştur
        mock_dependencies = self._create_mock_dependencies()
        stok_service = self._create_stok_service(mock_dependencies)
        
        # Mock stok durumu ayarla
        beklenen_stok_durumu = {
            'urun_id': urun_id,
            'magaza_id': magaza_id,
            'depo_id': depo_id,
            'kullanilabilir_stok': Decimal(str(stok_miktari)),
            'toplam_stok': Decimal(str(stok_miktari)),
            'rezerve_stok': Decimal('0'),
            'durum': 'NORMAL' if stok_miktari > 0 else 'STOK_YOK'
        }
        
        mock_dependencies['entegrasyon'].gercek_zamanli_stok_durumu_getir.return_value = beklenen_stok_durumu
        
        # Güncel stok durumunu al
        stok_durumu = stok_service.guncel_stok_durumu_getir(urun_id, magaza_id, depo_id)
        
        # Özellik doğrulaması: Entegrasyon servisi çağrılmalı ve doğru veri dönmeli
        mock_dependencies['entegrasyon'].gercek_zamanli_stok_durumu_getir.assert_called_with(
            urun_id, magaza_id, depo_id
        )
        
        assert stok_durumu == beklenen_stok_durumu, "Güncel stok durumu doğru dönmeliydi"
        assert stok_durumu['kullanilabilir_stok'] == Decimal(str(stok_miktari)), "Kullanılabilir stok doğru olmalıydı"
    
    # Özellik 27: Stok Yetersizliği İptal
    @given(
        urun_id=st.integers(min_value=1, max_value=10000),
        magaza_id=st.integers(min_value=1, max_value=100),
        talep_adet=st.integers(min_value=1, max_value=1000),
        mevcut_stok=st.integers(min_value=0, max_value=500)
    )
    @settings(max_examples=100)
    def test_property_27_stok_yetersizligi_iptal(self, urun_id, magaza_id, talep_adet, mevcut_stok):
        """
        **Feature: pos-cekirdek-modulu, Property 27: Stok Yetersizliği İptal**
        
        Herhangi bir stok yetersizliği durumu için, sistem satış işlemini iptal etmeli 
        ve stok kilidini serbest bırakmalı
        **Validates: Requirements 7.3**
        """
        assume(mevcut_stok < talep_adet)  # Sadece yetersiz stok durumlarını test et
        
        # Mock bağımlılıkları oluştur
        mock_dependencies = self._create_mock_dependencies()
        stok_service = self._create_stok_service(mock_dependencies)
        
        # Mock stok durumu ayarla (yetersiz stok)
        mock_dependencies['entegrasyon'].gercek_zamanli_stok_durumu_getir.return_value = {
            'urun_id': urun_id,
            'magaza_id': magaza_id,
            'kullanilabilir_stok': Decimal(str(mevcut_stok))
        }
        
        # Rezervasyon denemesi yapılmalı ama başarısız olmalı
        with pytest.raises(POSHatasi) as exc_info:
            stok_service.stok_rezerve_et(urun_id, magaza_id, talep_adet)
        
        # Özellik doğrulaması: Yetersiz stok hatası alınmalı
        assert "Yetersiz stok" in str(exc_info.value), "Yetersiz stok hatası alınmalıydı"
        
        # Stok kilidi serbest bırakılmalı (context manager ile test)
        with stok_service.stok_kilidi_ile(urun_id, magaza_id) as kilit_durumu:
            # Kilit alınabilmeli (çünkü rezervasyon başarısız oldu ve kilit serbest bırakıldı)
            assert kilit_durumu is True, "Stok kilidi alınabilmeliydi"
    
    # Özellik 28: Transaction Stok Düşümü
    @given(
        urun_id=st.integers(min_value=1, max_value=10000),
        magaza_id=st.integers(min_value=1, max_value=100),
        satis_adet=st.integers(min_value=1, max_value=100),
        referans_no=st.text(min_size=5, max_size=20, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
    )
    @settings(max_examples=100)
    def test_property_28_transaction_stok_dusumu(self, urun_id, magaza_id, satis_adet, referans_no):
        """
        **Feature: pos-cekirdek-modulu, Property 28: Transaction Stok Düşümü**
        
        Herhangi bir satış tamamlama işlemi için, sistem transaction içinde stok düşümü yapmalı
        **Validates: Requirements 7.4**
        """
        # Mock bağımlılıkları oluştur
        mock_dependencies = self._create_mock_dependencies()
        stok_service = self._create_stok_service(mock_dependencies)
        
        # Mock entegrasyon servisini başarılı olarak ayarla
        mock_dependencies['entegrasyon'].pos_satisi_isle.return_value = True
        
        # Stok düşümü yap
        sonuc = stok_service.stok_dusur(urun_id, magaza_id, satis_adet, referans_no)
        
        # Özellik doğrulaması: İşlem başarılı olmalı
        assert sonuc is True, "Stok düşümü başarılı olmalıydı"
        
        # Entegrasyon servisi çağrılmalı
        mock_dependencies['entegrasyon'].pos_satisi_isle.assert_called_once()
        
        # Çağrılan parametreleri kontrol et
        call_args = mock_dependencies['entegrasyon'].pos_satisi_isle.call_args[0][0]
        assert call_args.urun_id == urun_id, "Ürün ID doğru geçilmeliydi"
        assert call_args.magaza_id == magaza_id, "Mağaza ID doğru geçilmeliydi"
        assert call_args.satis_miktari == Decimal(str(satis_adet)), "Satış miktarı doğru geçilmeliydi"
        assert call_args.fiş_no == referans_no, "Referans numarası doğru geçilmeliydi"
    
    # Barkod doğrulama ve ürün bilgisi getirme testi
    @given(
        barkod=st.text(min_size=8, max_size=13, alphabet='0123456789'),
        urun_id=st.integers(min_value=1, max_value=10000),
        urun_adi=st.text(min_size=3, max_size=50),
        satis_fiyati=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('9999.99'), places=2)
    )
    @settings(max_examples=100)
    def test_barkod_dogrulama_ve_urun_bilgisi(self, barkod, urun_id, urun_adi, satis_fiyati):
        """
        Barkod doğrulama ve ürün bilgisi getirme özellik testi
        
        Herhangi bir geçerli barkod için, sistem ürün bilgilerini doğru şekilde getirmeli
        """
        # Mock bağımlılıkları oluştur
        mock_dependencies = self._create_mock_dependencies()
        stok_service = self._create_stok_service(mock_dependencies)
        
        # Mock barkod servisi ayarla
        mock_barkod_dto = Mock()
        mock_barkod_dto.urun_id = urun_id
        mock_barkod_dto.barkod = barkod
        mock_barkod_dto.urun_adi = urun_adi
        mock_barkod_dto.birim = "adet"
        mock_barkod_dto.satis_fiyati = satis_fiyati
        mock_barkod_dto.kdv_orani = Decimal('18.00')
        mock_barkod_dto.aktif = True
        
        mock_dependencies['barkod'].barkod_ara.return_value = mock_barkod_dto
        
        # Ürün bilgisi getir
        urun_bilgisi = stok_service.urun_bilgisi_getir(barkod)
        
        # Özellik doğrulaması: Ürün bilgisi doğru dönmeli
        assert urun_bilgisi is not None, "Ürün bilgisi None olmamalıydı"
        assert urun_bilgisi['urun_id'] == urun_id, "Ürün ID doğru olmalıydı"
        assert urun_bilgisi['barkod'] == barkod, "Barkod doğru olmalıydı"
        assert urun_bilgisi['urun_adi'] == urun_adi, "Ürün adı doğru olmalıydı"
        assert urun_bilgisi['satis_fiyati'] == satis_fiyati, "Satış fiyatı doğru olmalıydı"
        
        # Barkod servisi çağrılmalı
        mock_dependencies['barkod'].barkod_ara.assert_called_once_with(barkod)
    
    # Geçersiz barkod testi
    @given(
        gecersiz_barkod=st.one_of(
            st.just(""),  # Boş string
            st.just("   "),  # Sadece boşluk
            st.text(max_size=0)  # Boş
        )
    )
    @settings(max_examples=50)
    def test_gecersiz_barkod_hata_yonetimi(self, gecersiz_barkod):
        """
        Geçersiz barkod hata yönetimi testi
        
        Herhangi bir geçersiz barkod için, sistem hata mesajı göstermeli
        """
        # Mock bağımlılıkları oluştur
        mock_dependencies = self._create_mock_dependencies()
        stok_service = self._create_stok_service(mock_dependencies)
        
        with pytest.raises(POSHatasi) as exc_info:
            stok_service.urun_bilgisi_getir(gecersiz_barkod)
        
        assert "Barkod boş olamaz" in str(exc_info.value), "Barkod boş hatası alınmalıydı"
    
    # Rezervasyon round-trip testi
    @given(
        urun_id=st.integers(min_value=1, max_value=10000),
        magaza_id=st.integers(min_value=1, max_value=100),
        rezerve_adet=st.integers(min_value=1, max_value=100),
        mevcut_stok=st.integers(min_value=100, max_value=1000)  # Yeterli stok
    )
    @settings(max_examples=100)
    def test_rezervasyon_round_trip(self, urun_id, magaza_id, rezerve_adet, mevcut_stok):
        """
        Rezervasyon round-trip testi
        
        Herhangi bir rezervasyon için, rezerve et -> serbest bırak döngüsü çalışmalı
        """
        # Mock bağımlılıkları oluştur
        mock_dependencies = self._create_mock_dependencies()
        stok_service = self._create_stok_service(mock_dependencies)
        
        # Mock stok durumu ayarla (yeterli stok)
        mock_dependencies['entegrasyon'].gercek_zamanli_stok_durumu_getir.return_value = {
            'urun_id': urun_id,
            'magaza_id': magaza_id,
            'kullanilabilir_stok': Decimal(str(mevcut_stok))
        }
        
        # Mock rezervasyon servisi ayarla
        mock_dependencies['rezervasyon'].rezervasyon_olustur.return_value = 123
        mock_dependencies['rezervasyon'].rezervasyon_iptal_et.return_value = True
        
        # Rezervasyon oluştur
        rezervasyon_id = stok_service.stok_rezerve_et(urun_id, magaza_id, rezerve_adet)
        
        # Özellik doğrulaması: Rezervasyon ID dönmeli
        assert rezervasyon_id is not None, "Rezervasyon ID dönmeliydi"
        assert rezervasyon_id == "123", "Rezervasyon ID doğru olmalıydı"
        
        # Rezervasyonu serbest bırak
        serbest_birakma = stok_service.stok_rezervasyon_serbest_birak(rezervasyon_id)
        
        # Özellik doğrulaması: Serbest bırakma başarılı olmalı
        assert serbest_birakma is True, "Rezervasyon serbest bırakma başarılı olmalıydı"
        
        # Servis çağrıları doğrulanmalı
        mock_dependencies['rezervasyon'].rezervasyon_olustur.assert_called_once()
        mock_dependencies['rezervasyon'].rezervasyon_iptal_et.assert_called_once_with(123)