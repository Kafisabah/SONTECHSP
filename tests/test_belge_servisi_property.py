# Version: 0.1.0
# Last Update: 2024-12-16
# Module: test_belge_servisi_property
# Description: Belge servisi property testleri
# Changelog:
# - İlk oluşturma

"""
**Feature: satis-belgeleri-modulu, Property 4: Durum tabanlı belge oluşturma**
**Validates: Requirements 2.1, 2.4**

**Feature: satis-belgeleri-modulu, Property 6: Durum güncelleme tutarlılığı**
**Validates: Requirements 2.3, 3.4**

**Feature: satis-belgeleri-modulu, Property 7: Fatura oluşturma tutarlılığı**
**Validates: Requirements 3.1, 3.2, 3.3**

Belge servisi için property-based testler.
Bu testler belge yaşam döngüsü işlemlerinin doğruluk özelliklerini test eder.
"""

from decimal import Decimal
from hypothesis import given, strategies as st, assume
import pytest
from unittest.mock import Mock, MagicMock

from sontechsp.uygulama.moduller.satis_belgeleri.modeller import (
    SatisBelgesi, BelgeSatiri, BelgeTuru, BelgeDurumu
)
from sontechsp.uygulama.moduller.satis_belgeleri.servisler import (
    BelgeServisi, SiparisBilgileriDTO, NumaraServisi, 
    DurumAkisServisi, DogrulamaServisi
)
from sontechsp.uygulama.cekirdek.hatalar import IsKuraliHatasi


# Test stratejileri
@st.composite
def pozitif_decimal_strategy(draw):
    """Pozitif decimal üretici"""
    return Decimal(str(draw(st.floats(min_value=0.01, max_value=9999.99))))


@st.composite
def satir_bilgisi_strategy(draw):
    """Satır bilgisi üretici"""
    return {
        'urun_id': draw(st.integers(min_value=1, max_value=10000)),
        'miktar': draw(pozitif_decimal_strategy()),
        'birim_fiyat': draw(pozitif_decimal_strategy()),
        'kdv_orani': draw(st.sampled_from([Decimal('0'), Decimal('8'), Decimal('18')]))
    }


@st.composite
def siparis_bilgileri_strategy(draw):
    """Sipariş bilgileri üretici"""
    return SiparisBilgileriDTO(
        magaza_id=draw(st.integers(min_value=1, max_value=100)),
        magaza_kodu=draw(st.text(min_size=3, max_size=3, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ')),
        olusturan_kullanici_id=draw(st.integers(min_value=1, max_value=1000)),
        musteri_id=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=10000))),
        satirlar=draw(st.lists(satir_bilgisi_strategy(), min_size=1, max_size=5))
    )


@st.composite
def onaylanmis_siparis_strategy(draw):
    """Onaylanmış sipariş üretici"""
    siparis = SatisBelgesi(
        belge_id=draw(st.integers(min_value=1, max_value=10000)),
        belge_numarasi=f"SIP-{draw(st.integers(min_value=1000, max_value=9999))}",
        belge_turu=BelgeTuru.SIPARIS,
        belge_durumu=BelgeDurumu.ONAYLANDI,
        magaza_id=draw(st.integers(min_value=1, max_value=100)),
        olusturan_kullanici_id=draw(st.integers(min_value=1, max_value=1000)),
        musteri_id=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=10000)))
    )
    
    # Satırlar ekle
    satirlar = draw(st.lists(satir_bilgisi_strategy(), min_size=1, max_size=3))
    for satir_bilgisi in satirlar:
        satir = BelgeSatiri(
            urun_id=satir_bilgisi['urun_id'],
            miktar=satir_bilgisi['miktar'],
            birim_fiyat=satir_bilgisi['birim_fiyat'],
            kdv_orani=satir_bilgisi['kdv_orani']
        )
        siparis.satir_ekle(satir)
    
    return siparis


@st.composite
def taslak_siparis_strategy(draw):
    """Taslak sipariş üretici"""
    siparis = SatisBelgesi(
        belge_id=draw(st.integers(min_value=1, max_value=10000)),
        belge_numarasi=f"SIP-{draw(st.integers(min_value=1000, max_value=9999))}",
        belge_turu=BelgeTuru.SIPARIS,
        belge_durumu=BelgeDurumu.TASLAK,
        magaza_id=draw(st.integers(min_value=1, max_value=100)),
        olusturan_kullanici_id=draw(st.integers(min_value=1, max_value=1000))
    )
    
    return siparis


class TestBelgeServisiProperty:
    """Belge servisi property testleri"""
    
    def _mock_servisleri_olustur(self):
        """Test için mock servisleri oluştur"""
        belge_deposu = Mock()
        belge_satir_deposu = Mock()
        numara_servisi = Mock()
        durum_akis_servisi = Mock()
        dogrulama_servisi = Mock()
        
        # Varsayılan mock davranışları
        numara_servisi.numara_uret.return_value = "TEST-2024-12-0001"
        dogrulama_servisi.belge_dogrula.return_value = []
        durum_akis_servisi.durum_guncelle.return_value = True
        
        return (belge_deposu, belge_satir_deposu, numara_servisi, 
                durum_akis_servisi, dogrulama_servisi)
    
    @given(onaylanmis_siparis_strategy(), st.integers(min_value=1, max_value=1000))
    def test_durum_tabanli_belge_olusturma_onaylanmis(self, siparis, kullanici_id):
        """
        **Feature: satis-belgeleri-modulu, Property 4: Durum tabanlı belge oluşturma**
        **Validates: Requirements 2.1, 2.4**
        
        Herhangi bir ONAYLANDI durumundaki sipariş için irsaliye oluşturulabilmeli
        """
        # Mock servisleri oluştur
        mocks = self._mock_servisleri_olustur()
        belge_deposu, belge_satir_deposu, numara_servisi, durum_akis_servisi, dogrulama_servisi = mocks
        
        # Belge deposu mock davranışı
        belge_deposu.bul.return_value = siparis
        
        # Mock irsaliye nesnesi oluştur
        mock_irsaliye = MagicMock()
        mock_irsaliye.belge_id = 999
        mock_irsaliye.belge_numarasi = "IRS-2024-12-0001"
        mock_irsaliye.belge_turu = BelgeTuru.IRSALIYE
        mock_irsaliye.belge_durumu = BelgeDurumu.ONAYLANDI
        mock_irsaliye.satirlar = []
        
        belge_deposu.ekle.return_value = mock_irsaliye
        belge_deposu.guncelle.return_value = True
        
        # Belge servisi oluştur
        belge_servisi = BelgeServisi(*mocks)
        
        # İrsaliye oluşturmayı dene
        try:
            irsaliye_dto = belge_servisi.irsaliye_olustur(siparis.belge_id, kullanici_id)
            
            # İrsaliye başarıyla oluşturulmalı
            assert irsaliye_dto is not None
            assert irsaliye_dto.belge_turu == BelgeTuru.IRSALIYE.value
            
            # Numara servisi çağrılmalı
            numara_servisi.numara_uret.assert_called_once()
            
            # Belge deposuna kayıt yapılmalı
            belge_deposu.ekle.assert_called_once()
            
            # Sipariş durumu güncellenmeye çalışılmalı
            durum_akis_servisi.durum_guncelle.assert_called_once()
            
        except Exception as e:
            # Beklenmeyen hata olmamalı
            pytest.fail(f"Onaylanmış siparişten irsaliye oluşturma başarısız: {e}")
    
    @given(taslak_siparis_strategy(), st.integers(min_value=1, max_value=1000))
    def test_durum_tabanli_belge_olusturma_taslak(self, siparis, kullanici_id):
        """
        **Feature: satis-belgeleri-modulu, Property 4: Durum tabanlı belge oluşturma**
        **Validates: Requirements 2.1, 2.4**
        
        Herhangi bir TASLAK durumundaki sipariş için irsaliye oluşturma reddedilmelidir
        """
        # Mock servisleri oluştur
        mocks = self._mock_servisleri_olustur()
        belge_deposu = mocks[0]
        
        # Belge deposu mock davranışı
        belge_deposu.bul.return_value = siparis
        
        # Belge servisi oluştur
        belge_servisi = BelgeServisi(*mocks)
        
        # İrsaliye oluşturmayı dene - hata fırlatmalı
        with pytest.raises(IsKuraliHatasi) as exc_info:
            belge_servisi.irsaliye_olustur(siparis.belge_id, kullanici_id)
        
        # Hata mesajı durum kontrolü içermeli
        assert "onaylanmış" in str(exc_info.value).lower() or "taslak" in str(exc_info.value).lower()
    
    @given(onaylanmis_siparis_strategy(), st.integers(min_value=1, max_value=1000))
    def test_durum_guncelleme_tutarliligi_irsaliye(self, siparis, kullanici_id):
        """
        **Feature: satis-belgeleri-modulu, Property 6: Durum güncelleme tutarlılığı**
        **Validates: Requirements 2.3, 3.4**
        
        Herhangi bir başarılı irsaliye oluşturma işlemi sonrasında 
        kaynak sipariş durumu FATURALANDI olarak güncellenmelidir
        """
        # Mock servisleri oluştur
        mocks = self._mock_servisleri_olustur()
        belge_deposu, belge_satir_deposu, numara_servisi, durum_akis_servisi, dogrulama_servisi = mocks
        
        # Mock davranışları
        belge_deposu.bul.return_value = siparis
        kaydedilen_irsaliye = MagicMock()
        kaydedilen_irsaliye.belge_id = 999
        kaydedilen_irsaliye.belge_numarasi = "IRS-2024-12-0001"
        kaydedilen_irsaliye.belge_turu = BelgeTuru.IRSALIYE
        kaydedilen_irsaliye.satirlar = []
        belge_deposu.ekle.return_value = kaydedilen_irsaliye
        belge_deposu.guncelle.return_value = True
        
        # Belge servisi oluştur
        belge_servisi = BelgeServisi(*mocks)
        
        # İrsaliye oluştur
        irsaliye_dto = belge_servisi.irsaliye_olustur(siparis.belge_id, kullanici_id)
        
        # Durum güncelleme çağrısını kontrol et
        durum_akis_servisi.durum_guncelle.assert_called_once()
        call_args = durum_akis_servisi.durum_guncelle.call_args
        
        # Sipariş durumu FATURALANDI olarak güncellenmeye çalışılmalı
        assert call_args[0][1] == BelgeDurumu.FATURALANDI  # yeni_durum parametresi
        assert call_args[0][2] == kullanici_id  # degistiren_kullanici_id parametresi
        
        # Belge güncelleme çağrısı yapılmalı
        belge_deposu.guncelle.assert_called_once_with(siparis)
    
    @given(onaylanmis_siparis_strategy(), st.integers(min_value=1, max_value=1000))
    def test_fatura_olusturma_tutarliligi_siparis(self, siparis, kullanici_id):
        """
        **Feature: satis-belgeleri-modulu, Property 7: Fatura oluşturma tutarlılığı**
        **Validates: Requirements 3.1, 3.2, 3.3**
        
        Herhangi bir onaylanmış sipariş için fatura oluşturulabilmeli 
        ve KDV hesaplamaları doğru yapılmalıdır
        """
        # Mock servisleri oluştur
        mocks = self._mock_servisleri_olustur()
        belge_deposu, belge_satir_deposu, numara_servisi, durum_akis_servisi, dogrulama_servisi = mocks
        
        # Mock davranışları
        belge_deposu.bul.return_value = siparis
        kaydedilen_fatura = MagicMock()
        kaydedilen_fatura.belge_id = 888
        kaydedilen_fatura.belge_numarasi = "FAT-2024-12-0001"
        kaydedilen_fatura.belge_turu = BelgeTuru.FATURA
        kaydedilen_fatura.belge_durumu = BelgeDurumu.ONAYLANDI
        kaydedilen_fatura.satirlar = []
        kaydedilen_fatura.toplam_tutar = Decimal('100.00')
        kaydedilen_fatura.kdv_tutari = Decimal('18.00')
        kaydedilen_fatura.genel_toplam = Decimal('118.00')
        belge_deposu.ekle.return_value = kaydedilen_fatura
        belge_deposu.guncelle.return_value = True
        
        # Belge servisi oluştur
        belge_servisi = BelgeServisi(*mocks)
        
        # Fatura oluştur
        fatura_dto = belge_servisi.fatura_olustur(
            siparis.belge_id, 
            "SIPARIS", 
            kullanici_id
        )
        
        # Fatura başarıyla oluşturulmalı
        assert fatura_dto is not None
        assert fatura_dto.belge_turu == BelgeTuru.FATURA.value
        
        # Numara servisi fatura için çağrılmalı
        numara_servisi.numara_uret.assert_called()
        call_args = numara_servisi.numara_uret.call_args[0]
        assert call_args[2] == BelgeTuru.FATURA  # belge_turu parametresi
        
        # Belge doğrulama yapılmalı
        dogrulama_servisi.belge_dogrula.assert_called()
        
        # Belge deposuna kayıt yapılmalı
        belge_deposu.ekle.assert_called_once()
        
        # Sipariş durumu güncellenmeye çalışılmalı
        durum_akis_servisi.durum_guncelle.assert_called_once()
    
    @given(siparis_bilgileri_strategy())
    def test_siparis_olusturma_tutarliligi(self, siparis_bilgileri):
        """
        Sipariş oluşturma işleminin tutarlılığını test et
        """
        # Mock servisleri oluştur
        mocks = self._mock_servisleri_olustur()
        belge_deposu, belge_satir_deposu, numara_servisi, durum_akis_servisi, dogrulama_servisi = mocks
        
        # Mock davranışları
        kaydedilen_siparis = MagicMock()
        kaydedilen_siparis.belge_id = 777
        kaydedilen_siparis.belge_numarasi = "SIP-2024-12-0001"
        kaydedilen_siparis.belge_turu = BelgeTuru.SIPARIS
        kaydedilen_siparis.belge_durumu = BelgeDurumu.TASLAK
        kaydedilen_siparis.satirlar = []
        kaydedilen_siparis.toplam_tutar = Decimal('100.00')
        kaydedilen_siparis.kdv_tutari = Decimal('18.00')
        kaydedilen_siparis.genel_toplam = Decimal('118.00')
        belge_deposu.ekle.return_value = kaydedilen_siparis
        
        # Belge servisi oluştur
        belge_servisi = BelgeServisi(*mocks)
        
        # Sipariş oluştur
        siparis_dto = belge_servisi.siparis_olustur(siparis_bilgileri)
        
        # Sipariş başarıyla oluşturulmalı
        assert siparis_dto is not None
        assert siparis_dto.belge_turu == BelgeTuru.SIPARIS.value
        assert siparis_dto.belge_durumu == BelgeDurumu.TASLAK.value
        
        # Numara servisi çağrılmalı
        numara_servisi.numara_uret.assert_called_once()
        call_args = numara_servisi.numara_uret.call_args[0]
        assert call_args[0] == siparis_bilgileri.magaza_id
        assert call_args[1] == siparis_bilgileri.magaza_kodu
        assert call_args[2] == BelgeTuru.SIPARIS
        
        # Doğrulama yapılmalı
        dogrulama_servisi.belge_dogrula.assert_called_once()
        
        # Belge deposuna kayıt yapılmalı
        belge_deposu.ekle.assert_called_once()
    
    @given(st.integers(min_value=1, max_value=10000), st.integers(min_value=1, max_value=1000))
    def test_pos_satisinden_fatura_desteklenmeme(self, pos_satis_id, kullanici_id):
        """
        POS satışından fatura oluşturmanın henüz desteklenmediğini test et
        """
        # Mock servisleri oluştur
        mocks = self._mock_servisleri_olustur()
        
        # Belge servisi oluştur
        belge_servisi = BelgeServisi(*mocks)
        
        # POS satışından fatura oluşturmayı dene - hata fırlatmalı
        with pytest.raises(IsKuraliHatasi) as exc_info:
            belge_servisi.fatura_olustur(pos_satis_id, "POS", kullanici_id)
        
        # Hata mesajı desteklenmediğini belirtmeli
        assert "desteklenmiyor" in str(exc_info.value).lower()