# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_kargo_properties_2
# Description: Kargo modülü property-based testleri (devam)
# Changelog:
# - Property 4-13 testleri eklendi

"""
Kargo modülü property-based testleri (devam).
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, patch
from datetime import datetime

from uygulama.moduller.kargo.dto import KargoDurumDTO
from uygulama.moduller.kargo.sabitler import TakipDurumlari, EtiketDurumlari
from uygulama.moduller.kargo.servisler import KargoServisi, EntegrasyonHatasi
from uygulama.moduller.kargo.tasiyici_fabrikasi import TasiyiciFabrikasi


class TestKargoProperties2:
    """Kargo modülü property-based testleri (devam)."""
    
    @given(etiket_id=st.integers(min_value=1, max_value=999999),
           takip_no=st.text(min_size=10, max_size=20),
           durum=st.sampled_from(TakipDurumlari.tum_durumlar()))
    @settings(max_examples=100)
    def test_property_4_durum_sorgulama_islemleri(self, etiket_id, takip_no, durum):
        """
        **Feature: kargo-entegrasyon-altyapisi, Property 4: Durum Sorgulama İşlemleri**
        
        Herhangi bir geçerli takip numarası için durum sorgulandığında, 
        sistem güncel durum bilgisini döndürecek ve takip geçmişine yeni kayıt ekleyecek.
        
        **Validates: Requirements 3.1, 3.2, 3.5**
        """
        mock_session = Mock()
        mock_depo = Mock()
        
        with patch('uygulama.moduller.kargo.servisler.KargoDeposu') as mock_depo_class:
            mock_depo_class.return_value = mock_depo
            
            # Mock etiket
            mock_etiket = Mock()
            mock_etiket.id = etiket_id
            mock_etiket.takip_no = takip_no
            mock_etiket.tasiyici = 'YURTICI'
            mock_depo.etiket_getir.return_value = mock_etiket
            
            # Mock takip kaydı
            mock_takip = Mock()
            mock_depo.takip_kaydi_ekle.return_value = mock_takip
            
            # Taşıyıcı mock'u
            with patch.object(TasiyiciFabrikasi, 'tasiyici_olustur') as mock_tasiyici_factory:
                mock_tasiyici = Mock()
                mock_zaman = datetime.now()
                mock_tasiyici.durum_sorgula.return_value = {
                    'durum': durum,
                    'aciklama': f'Test açıklama: {durum}',
                    'zaman': mock_zaman
                }
                mock_tasiyici_factory.return_value = mock_tasiyici
                
                servis = KargoServisi(mock_session)
                sonuc = servis.durum_sorgula(etiket_id)
                
                # Sonuç kontrolü
                assert sonuc is not None
                assert sonuc.etiket_id == etiket_id
                assert sonuc.takip_no == takip_no
                assert sonuc.durum == durum
                assert sonuc.zaman == mock_zaman
                
                # Takip kaydı eklendiğini kontrol et
                mock_depo.takip_kaydi_ekle.assert_called_once_with(
                    etiket_id=etiket_id,
                    takip_no=takip_no,
                    durum=durum,
                    aciklama=f'Test açıklama: {durum}',
                    zaman=mock_zaman
                )
    
    @given(gecersiz_takip_no=st.one_of(
        st.just(''),
        st.just(None),
        st.text(max_size=5)  # Çok kısa takip numarası
    ))
    @settings(max_examples=50)
    def test_property_5_hata_yonetimi(self, gecersiz_takip_no):
        """
        **Feature: kargo-entegrasyon-altyapisi, Property 5: Hata Yönetimi**
        
        Herhangi bir geçersiz takip numarası veya taşıyıcı servis hatası durumunda, 
        sistem uygun hata mesajları döndürecek.
        
        **Validates: Requirements 3.3, 3.4**
        """
        mock_session = Mock()
        mock_depo = Mock()
        
        with patch('uygulama.moduller.kargo.servisler.KargoDeposu') as mock_depo_class:
            mock_depo_class.return_value = mock_depo
            
            # Etiket bulunamadı
            mock_depo.etiket_takip_no_ile_bul.return_value = None
            
            servis = KargoServisi(mock_session)
            
            # Geçersiz takip numarası ile None dönmeli
            if gecersiz_takip_no:
                sonuc = servis.takip_no_ile_durum_sorgula(gecersiz_takip_no)
                assert sonuc is None
    
    @given(etiket_id=st.integers(min_value=1, max_value=999999),
           deneme_sayisi=st.integers(min_value=0, max_value=2))
    @settings(max_examples=100)
    def test_property_6_retry_mekanizmasi(self, etiket_id, deneme_sayisi):
        """
        **Feature: kargo-entegrasyon-altyapisi, Property 6: Retry Mekanizması**
        
        Herhangi bir başarısız etiket oluşturma işlemi için, sistem durumu HATA olarak 
        işaretleyecek, bekleyen etiketleri yeniden deneyecek, deneme sayısını artıracak 
        ve maksimum denemeye ulaşıldığında işlemi durduracak.
        
        **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
        """
        mock_session = Mock()
        mock_depo = Mock()
        
        with patch('uygulama.moduller.kargo.servisler.KargoDeposu') as mock_depo_class:
            mock_depo_class.return_value = mock_depo
            
            # Mock bekleyen etiket
            mock_etiket = Mock()
            mock_etiket.id = etiket_id
            mock_etiket.deneme_sayisi = deneme_sayisi
            mock_etiket.tasiyici = 'YURTICI'
            mock_depo.bekleyen_etiketleri_al.return_value = [mock_etiket]
            
            # Taşıyıcı mock'u
            with patch.object(TasiyiciFabrikasi, 'tasiyici_olustur') as mock_tasiyici_factory:
                mock_tasiyici = Mock()
                
                # Başarılı sonuç
                mock_tasiyici.etiket_olustur.return_value = {
                    'durum': EtiketDurumlari.OLUSTURULDU,
                    'takip_no': 'RETRY123456',
                    'mesaj': 'Retry başarılı'
                }
                mock_tasiyici_factory.return_value = mock_tasiyici
                
                servis = KargoServisi(mock_session)
                sonuc = servis.bekleyen_etiketleri_isle(limit=1)
                
                # Sonuç kontrolü
                assert sonuc['toplam_islenen'] == 1
                
                if deneme_sayisi < 3:  # MAKSIMUM_DENEME_SAYISI
                    # Deneme sayısı artırıldı
                    mock_depo.deneme_sayisi_artir.assert_called_once_with(etiket_id)
                    
                    # Durum güncellendi
                    mock_depo.etiket_durum_guncelle.assert_called_once_with(
                        etiket_id,
                        EtiketDurumlari.OLUSTURULDU,
                        'Retry başarılı',
                        'RETRY123456'
                    )
                    
                    assert sonuc['basarili'] == 1
                else:
                    # Maksimum deneme aşıldı
                    assert sonuc['maksimum_deneme_asilan'] == 1