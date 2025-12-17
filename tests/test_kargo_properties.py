# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_kargo_properties
# Description: Kargo modülü property-based testleri
# Changelog:
# - Property-based testler eklendi
# - Hypothesis kütüphanesi kullanıldı

"""
Kargo modülü property-based testleri.

Bu modül, kargo işlemlerinin doğruluk özelliklerini test eder.
Hypothesis kütüphanesi ile rastgele veri üretimi yapılır.
"""

import pytest
from hypothesis import given, strategies as st, settings
from decimal import Decimal
from unittest.mock import Mock, patch

from uygulama.moduller.kargo.dto import KargoEtiketOlusturDTO
from uygulama.moduller.kargo.sabitler import (
    KaynakTurleri, EtiketDurumlari, Tasiyicilar
)
from uygulama.moduller.kargo.servisler import (
    KargoServisi, DogrulamaHatasi, BenzersizlikHatasi
)
from uygulama.moduller.kargo.tasiyici_fabrikasi import TasiyiciFabrikasi


# Test veri üreticileri
@st.composite
def valid_kargo_dto(draw):
    """Geçerli kargo DTO üretir."""
    return KargoEtiketOlusturDTO(
        kaynak_turu=draw(st.sampled_from(KaynakTurleri.tum_turler())),
        kaynak_id=draw(st.integers(min_value=1, max_value=999999)),
        alici_ad=draw(st.text(min_size=1, max_size=100, 
                             alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        alici_telefon=draw(st.text(min_size=10, max_size=15, 
                                  alphabet=st.characters(whitelist_categories=('Nd',)))),
        alici_adres=draw(st.text(min_size=5, max_size=200)),
        alici_il=draw(st.text(min_size=2, max_size=50)),
        alici_ilce=draw(st.text(min_size=2, max_size=50)),
        tasiyici=draw(st.sampled_from(Tasiyicilar.tum_tasiyicilar())),
        paket_agirlik_kg=draw(st.decimals(min_value=Decimal('0.1'), 
                                         max_value=Decimal('100.0'), 
                                         places=2))
    )


@st.composite
def invalid_kargo_dto(draw):
    """Geçersiz kargo DTO üretir."""
    # Rastgele geçersiz alan seç
    invalid_field = draw(st.sampled_from([
        'kaynak_turu', 'kaynak_id', 'alici_ad', 'alici_telefon',
        'alici_adres', 'alici_il', 'alici_ilce', 'tasiyici', 'paket_agirlik_kg'
    ]))
    
    base_dto = draw(valid_kargo_dto())
    
    # Seçilen alanı geçersiz yap
    if invalid_field == 'kaynak_turu':
        base_dto.kaynak_turu = draw(st.text().filter(
            lambda x: x not in KaynakTurleri.tum_turler()
        ))
    elif invalid_field == 'kaynak_id':
        base_dto.kaynak_id = draw(st.integers(max_value=0))
    elif invalid_field == 'alici_ad':
        base_dto.alici_ad = draw(st.sampled_from(['', '   ', None]))
    elif invalid_field == 'alici_telefon':
        base_dto.alici_telefon = draw(st.sampled_from(['', '   ', None]))
    elif invalid_field == 'alici_adres':
        base_dto.alici_adres = draw(st.sampled_from(['', '   ', None]))
    elif invalid_field == 'alici_il':
        base_dto.alici_il = draw(st.sampled_from(['', '   ', None]))
    elif invalid_field == 'alici_ilce':
        base_dto.alici_ilce = draw(st.sampled_from(['', '   ', None]))
    elif invalid_field == 'tasiyici':
        base_dto.tasiyici = draw(st.text().filter(
            lambda x: x not in Tasiyicilar.tum_tasiyicilar()
        ))
    elif invalid_field == 'paket_agirlik_kg':
        base_dto.paket_agirlik_kg = draw(st.decimals(max_value=Decimal('0')))
    
    return base_dto


class TestKargoProperties:
    """Kargo modülü property-based testleri."""
    
    @given(dto=valid_kargo_dto())
    @settings(max_examples=100)
    def test_property_1_etiket_olusturma_dogrulama(self, dto):
        """
        **Feature: kargo-entegrasyon-altyapisi, Property 1: Etiket Oluşturma Doğrulama**
        
        Herhangi bir etiket oluşturma talebi için, sistem geçerli taşıyıcı bilgilerini 
        doğrulayacak, kaynak türü ve ID'sini kontrol edecek, benzersizlik kuralını 
        uygulayacak ve başarılı işlemlerde takip numarası ile sonuç döndürecek.
        
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
        """
        # Mock session ve depo
        mock_session = Mock()
        mock_depo = Mock()
        
        with patch('uygulama.moduller.kargo.servisler.KargoDeposu') as mock_depo_class:
            mock_depo_class.return_value = mock_depo
            
            # Benzersizlik kontrolü - etiket yok
            mock_depo.etiket_kaynaktan_bul.return_value = None
            
            # Etiket kaydı oluşturma
            mock_etiket = Mock()
            mock_etiket.id = 1
            mock_depo.etiket_kaydi_olustur.return_value = mock_etiket
            
            # Taşıyıcı mock'u
            with patch.object(TasiyiciFabrikasi, 'tasiyici_olustur') as mock_tasiyici_factory:
                mock_tasiyici = Mock()
                mock_tasiyici.etiket_olustur.return_value = {
                    'durum': EtiketDurumlari.OLUSTURULDU,
                    'takip_no': 'TEST123456',
                    'mesaj': 'Başarılı'
                }
                mock_tasiyici_factory.return_value = mock_tasiyici
                
                # Servis oluştur ve test et
                servis = KargoServisi(mock_session)
                sonuc = servis.etiket_olustur(dto)
                
                # Doğrulamalar
                assert sonuc.etiket_id == 1
                assert sonuc.durum == EtiketDurumlari.OLUSTURULDU
                assert sonuc.takip_no == 'TEST123456'
                
                # Metodların çağrıldığını kontrol et
                mock_depo.etiket_kaynaktan_bul.assert_called_once_with(
                    dto.kaynak_turu, dto.kaynak_id, dto.tasiyici
                )
                mock_depo.etiket_kaydi_olustur.assert_called_once_with(dto)
                mock_tasiyici_factory.assert_called_once_with(dto.tasiyici)
                mock_tasiyici.etiket_olustur.assert_called_once()
    
    @given(dto=invalid_kargo_dto())
    @settings(max_examples=50)
    def test_property_1_etiket_olusturma_dogrulama_hatali_veri(self, dto):
        """
        Geçersiz verilerle etiket oluşturma denemesi DogrulamaHatasi vermeli.
        """
        mock_session = Mock()
        
        with patch('uygulama.moduller.kargo.servisler.KargoDeposu'):
            servis = KargoServisi(mock_session)
            
            # Geçersiz veri ile DogrulamaHatasi beklenir
            with pytest.raises(DogrulamaHatasi):
                servis.etiket_olustur(dto)
    
    @given(dto=valid_kargo_dto())
    @settings(max_examples=50)
    def test_property_1_benzersizlik_kontrolu(self, dto):
        """
        Aynı kaynak+taşıyıcı kombinasyonu için ikinci etiket BenzersizlikHatasi vermeli.
        """
        mock_session = Mock()
        mock_depo = Mock()
        
        with patch('uygulama.moduller.kargo.servisler.KargoDeposu') as mock_depo_class:
            mock_depo_class.return_value = mock_depo
            
            # Mevcut etiket var
            mock_mevcut_etiket = Mock()
            mock_depo.etiket_kaynaktan_bul.return_value = mock_mevcut_etiket
            
            servis = KargoServisi(mock_session)
            
            # BenzersizlikHatasi beklenir
            with pytest.raises(BenzersizlikHatasi):
                servis.etiket_olustur(dto)
    
    @given(kaynak_turu=st.sampled_from(KaynakTurleri.tum_turler()),
           dto=valid_kargo_dto())
    @settings(max_examples=100)
    def test_property_2_kaynak_turu_yonetimi(self, kaynak_turu, dto):
        """
        **Feature: kargo-entegrasyon-altyapisi, Property 2: Kaynak Türü Yönetimi**
        
        Herhangi bir etiket oluşturma işleminde, sistem kaynak türünü 
        (POS_SATIS veya SATIS_BELGESI) doğru şekilde kayıt edecek ve 
        eksik/geçersiz veriler için uygun hata mesajları döndürecek.
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
        """
        # DTO'nun kaynak türünü test edilecek türe ayarla
        dto.kaynak_turu = kaynak_turu
        
        mock_session = Mock()
        mock_depo = Mock()
        
        with patch('uygulama.moduller.kargo.servisler.KargoDeposu') as mock_depo_class:
            mock_depo_class.return_value = mock_depo
            
            # Benzersizlik kontrolü - etiket yok
            mock_depo.etiket_kaynaktan_bul.return_value = None
            
            # Etiket kaydı oluşturma
            mock_etiket = Mock()
            mock_etiket.id = 1
            mock_depo.etiket_kaydi_olustur.return_value = mock_etiket
            
            # Taşıyıcı mock'u
            with patch.object(TasiyiciFabrikasi, 'tasiyici_olustur') as mock_tasiyici_factory:
                mock_tasiyici = Mock()
                mock_tasiyici.etiket_olustur.return_value = {
                    'durum': EtiketDurumlari.OLUSTURULDU,
                    'takip_no': 'TEST123456',
                    'mesaj': 'Başarılı'
                }
                mock_tasiyici_factory.return_value = mock_tasiyici
                
                servis = KargoServisi(mock_session)
                sonuc = servis.etiket_olustur(dto)
                
                # Kaynak türünün doğru kaydedildiğini kontrol et
                mock_depo.etiket_kaydi_olustur.assert_called_once()
                call_args = mock_depo.etiket_kaydi_olustur.call_args[0][0]
                assert call_args.kaynak_turu == kaynak_turu
                
                # Sonucun başarılı olduğunu kontrol et
                assert sonuc.durum == EtiketDurumlari.OLUSTURULDU
    
    @given(gecersiz_kaynak_turu=st.text().filter(
        lambda x: x not in KaynakTurleri.tum_turler() and x.strip() != ''
    ))
    @settings(max_examples=50)
    def test_property_2_gecersiz_kaynak_turu(self, gecersiz_kaynak_turu):
        """
        Geçersiz kaynak türü ile etiket oluşturma DogrulamaHatasi vermeli.
        """
        dto = KargoEtiketOlusturDTO(
            kaynak_turu=gecersiz_kaynak_turu,
            kaynak_id=1,
            alici_ad="Test Alıcı",
            alici_telefon="5551234567",
            alici_adres="Test Adres",
            alici_il="İstanbul",
            alici_ilce="Kadıköy",
            tasiyici=Tasiyicilar.YURTICI
        )
        
        mock_session = Mock()
        
        with patch('uygulama.moduller.kargo.servisler.KargoDeposu'):
            servis = KargoServisi(mock_session)
            
            # DogrulamaHatasi beklenir
            with pytest.raises(DogrulamaHatasi):
                servis.etiket_olustur(dto)
    
    @given(dto_without_weight=st.builds(
        KargoEtiketOlusturDTO,
        kaynak_turu=st.sampled_from(KaynakTurleri.tum_turler()),
        kaynak_id=st.integers(min_value=1, max_value=999999),
        alici_ad=st.text(min_size=1, max_size=100),
        alici_telefon=st.text(min_size=10, max_size=15),
        alici_adres=st.text(min_size=5, max_size=200),
        alici_il=st.text(min_size=2, max_size=50),
        alici_ilce=st.text(min_size=2, max_size=50),
        tasiyici=st.sampled_from(Tasiyicilar.tum_tasiyicilar())
        # paket_agirlik_kg belirtilmiyor - varsayılan değer kullanılacak
    ))
    @settings(max_examples=100)
    def test_property_3_varsayilan_deger_atama(self, dto_without_weight):
        """
        **Feature: kargo-entegrasyon-altyapisi, Property 3: Varsayılan Değer Atama**
        
        Herhangi bir etiket oluşturma işleminde paket ağırlığı belirtilmediğinde, 
        sistem varsayılan 1.0 kg değerini kullanacak.
        
        **Validates: Requirements 2.5**
        """
        from uygulama.moduller.kargo.sabitler import VARSAYILAN_PAKET_AGIRLIK_KG
        
        # DTO oluşturulduğunda varsayılan değer atanmalı
        assert dto_without_weight.paket_agirlik_kg == Decimal(str(VARSAYILAN_PAKET_AGIRLIK_KG))
        
        mock_session = Mock()
        mock_depo = Mock()
        
        with patch('uygulama.moduller.kargo.servisler.KargoDeposu') as mock_depo_class:
            mock_depo_class.return_value = mock_depo
            
            # Benzersizlik kontrolü - etiket yok
            mock_depo.etiket_kaynaktan_bul.return_value = None
            
            # Etiket kaydı oluşturma
            mock_etiket = Mock()
            mock_etiket.id = 1
            mock_depo.etiket_kaydi_olustur.return_value = mock_etiket
            
            # Taşıyıcı mock'u
            with patch.object(TasiyiciFabrikasi, 'tasiyici_olustur') as mock_tasiyici_factory:
                mock_tasiyici = Mock()
                mock_tasiyici.etiket_olustur.return_value = {
                    'durum': EtiketDurumlari.OLUSTURULDU,
                    'takip_no': 'TEST123456',
                    'mesaj': 'Başarılı'
                }
                mock_tasiyici_factory.return_value = mock_tasiyici
                
                servis = KargoServisi(mock_session)
                sonuc = servis.etiket_olustur(dto_without_weight)
                
                # Varsayılan ağırlığın kullanıldığını kontrol et
                mock_depo.etiket_kaydi_olustur.assert_called_once()
                call_args = mock_depo.etiket_kaydi_olustur.call_args[0][0]
                assert call_args.paket_agirlik_kg == Decimal(str(VARSAYILAN_PAKET_AGIRLIK_KG))
                
                # Sonucun başarılı olduğunu kontrol et
                assert sonuc.durum == EtiketDurumlari.OLUSTURULDU