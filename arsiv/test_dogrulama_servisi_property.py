# Version: 0.1.0
# Last Update: 2024-12-16
# Module: test_dogrulama_servisi_property
# Description: Doğrulama servisi property testleri
# Changelog:
# - İlk oluşturma

"""
**Feature: satis-belgeleri-modulu, Property 2: Belge satır tutarlılığı**
**Validates: Requirements 1.3**

**Feature: satis-belgeleri-modulu, Property 14: Veri doğrulama tutarlılığı**
**Validates: Requirements 6.2, 6.3**

Doğrulama servisi için property-based testler.
"""

from decimal import Decimal
from hypothesis import given, strategies as st, assume
import pytest

from sontechsp.uygulama.moduller.satis_belgeleri.modeller import (
    SatisBelgesi, BelgeSatiri, BelgeTuru, BelgeDurumu
)
from sontechsp.uygulama.moduller.satis_belgeleri.servisler import DogrulamaServisi
from sontechsp.uygulama.cekirdek.hatalar import IsKuraliHatasi


# Test stratejileri
@st.composite
def pozitif_decimal_strategy(draw):
    """Pozitif decimal üretici"""
    return Decimal(str(draw(st.floats(min_value=0.01, max_value=999999.99))))


@st.composite
def kdv_orani_strategy(draw):
    """Geçerli KDV oranı üretici"""
    return Decimal(str(draw(st.sampled_from([0.00, 8.00, 18.00, 20.00]))))


@st.composite
def belge_satiri_strategy(draw):
    """Geçerli belge satırı üretici"""
    miktar = draw(pozitif_decimal_strategy())
    birim_fiyat = draw(pozitif_decimal_strategy())
    kdv_orani = draw(kdv_orani_strategy())
    
    return BelgeSatiri(
        urun_id=draw(st.integers(min_value=1, max_value=10000)),
        sira_no=draw(st.integers(min_value=1, max_value=100)),
        miktar=miktar,
        birim_fiyat=birim_fiyat,
        kdv_orani=kdv_orani
    )


@st.composite
def satis_belgesi_strategy(draw):
    """Geçerli satış belgesi üretici"""
    belge = SatisBelgesi(
        belge_numarasi=draw(st.text(min_size=10, max_size=20)),
        belge_turu=draw(st.sampled_from(list(BelgeTuru))),
        belge_durumu=draw(st.sampled_from(list(BelgeDurumu))),
        magaza_id=draw(st.integers(min_value=1, max_value=100)),
        olusturan_kullanici_id=draw(st.integers(min_value=1, max_value=1000))
    )
    
    # Satırlar ekle
    satirlar = draw(st.lists(belge_satiri_strategy(), min_size=1, max_size=5))
    for satir in satirlar:
        belge.satir_ekle(satir)
    
    return belge


class TestDogrulamaServisiProperty:
    """Doğrulama servisi property testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.dogrulama_servisi = DogrulamaServisi()
    
    @given(belge_satiri_strategy())
    def test_belge_satir_tutarliligi(self, satir):
        """
        **Feature: satis-belgeleri-modulu, Property 2: Belge satır tutarlılığı**
        **Validates: Requirements 1.3**
        
        Herhangi bir belge satırı eklendiğinde, ürün bilgileri doğrulanmalı 
        ve toplam tutarlar doğru hesaplanmalıdır
        """
        # Satır tutarlarını hesapla
        hesaplanan_tutarlar = self.dogrulama_servisi.satir_tutarlari_hesapla(satir)
        
        # Beklenen hesaplamalar
        beklenen_satir_tutari = satir.miktar * satir.birim_fiyat
        beklenen_kdv_tutari = beklenen_satir_tutari * (satir.kdv_orani / Decimal('100'))
        beklenen_satir_toplami = beklenen_satir_tutari + beklenen_kdv_tutari
        
        # Hesaplanan tutarlar doğru olmalı
        assert hesaplanan_tutarlar['satir_tutari'] == beklenen_satir_tutari
        assert hesaplanan_tutarlar['kdv_tutari'] == beklenen_kdv_tutari
        assert hesaplanan_tutarlar['satir_toplami'] == beklenen_satir_toplami
        
        # Satır doğrulaması başarılı olmalı
        hatalar = self.dogrulama_servisi.satir_dogrula(satir)
        
        # Geçerli satır için hata olmamalı
        if (satir.urun_id and satir.urun_id > 0 and 
            satir.miktar > 0 and satir.birim_fiyat >= 0 and
            satir.sira_no and satir.sira_no > 0):
            assert len(hatalar) == 0
    
    @given(satis_belgesi_strategy())
    def test_veri_dogrulama_tutarliligi(self, belge):
        """
        **Feature: satis-belgeleri-modulu, Property 14: Veri doğrulama tutarlılığı**
        **Validates: Requirements 6.2, 6.3**
        
        Herhangi bir belge satırı için ürün bilgileri doğrulanmalı ve 
        toplam tutarlar satır toplamları ile uyumlu olmalıdır
        """
        # Belge toplam tutarlarını hesapla
        hesaplanan_tutarlar = self.dogrulama_servisi.toplam_tutarlari_hesapla(belge)
        
        # Manuel hesaplama ile karşılaştır
        manuel_toplam_tutar = Decimal('0.00')
        manuel_kdv_tutari = Decimal('0.00')
        
        for satir in belge.satirlar:
            satir_tutarlari = self.dogrulama_servisi.satir_tutarlari_hesapla(satir)
            manuel_toplam_tutar += satir_tutarlari['satir_tutari']
            manuel_kdv_tutari += satir_tutarlari['kdv_tutari']
        
        manuel_genel_toplam = manuel_toplam_tutar + manuel_kdv_tutari
        
        # Hesaplanan tutarlar manuel hesaplama ile uyumlu olmalı
        assert hesaplanan_tutarlar['toplam_tutar'] == manuel_toplam_tutar
        assert hesaplanan_tutarlar['kdv_tutari'] == manuel_kdv_tutari
        assert hesaplanan_tutarlar['genel_toplam'] == manuel_genel_toplam
        
        # Belge tutarlarını güncelle
        belge.toplam_tutar = hesaplanan_tutarlar['toplam_tutar']
        belge.kdv_tutari = hesaplanan_tutarlar['kdv_tutari']
        belge.genel_toplam = hesaplanan_tutarlar['genel_toplam']
        
        # Tutar tutarlılığı kontrolü başarılı olmalı
        tutarlilik_hatalari = self.dogrulama_servisi.tutar_tutarliligi_kontrol_et(belge)
        assert len(tutarlilik_hatalari) == 0
    
    @given(st.lists(belge_satiri_strategy(), min_size=1, max_size=10))
    def test_toplam_tutar_hesaplama_tutarliligi(self, satirlar):
        """
        Toplam tutar hesaplama işleminin tutarlılığını test et
        """
        # Test belgesi oluştur
        belge = SatisBelgesi(
            belge_numarasi="TEST-2024-12-0001",
            belge_turu=BelgeTuru.SIPARIS,
            belge_durumu=BelgeDurumu.TASLAK,
            magaza_id=1,
            olusturan_kullanici_id=1
        )
        
        # Satırları ekle
        for satir in satirlar:
            belge.satir_ekle(satir)
        
        # Toplam tutarları hesapla
        hesaplanan = self.dogrulama_servisi.toplam_tutarlari_hesapla(belge)
        
        # Her satır için ayrı ayrı hesapla ve topla
        toplam_satir_tutari = Decimal('0.00')
        toplam_kdv_tutari = Decimal('0.00')
        
        for satir in satirlar:
            satir_hesaplanan = self.dogrulama_servisi.satir_tutarlari_hesapla(satir)
            toplam_satir_tutari += satir_hesaplanan['satir_tutari']
            toplam_kdv_tutari += satir_hesaplanan['kdv_tutari']
        
        # Sonuçlar uyumlu olmalı
        assert hesaplanan['toplam_tutar'] == toplam_satir_tutari
        assert hesaplanan['kdv_tutari'] == toplam_kdv_tutari
        assert hesaplanan['genel_toplam'] == toplam_satir_tutari + toplam_kdv_tutari
    
    @given(st.floats(min_value=-50.0, max_value=150.0))
    def test_kdv_orani_dogrulama(self, kdv_orani_float):
        """
        KDV oranı doğrulama işleminin tutarlılığını test et
        """
        kdv_orani = Decimal(str(kdv_orani_float))
        
        # KDV oranı doğrulaması
        gecerli = self.dogrulama_servisi.kdv_orani_dogrula(kdv_orani)
        
        # Beklenen sonuç
        beklenen_gecerli = (
            Decimal('0') <= kdv_orani <= Decimal('50') or
            kdv_orani in [Decimal('0.00'), Decimal('8.00'), Decimal('18.00')]
        )
        
        assert gecerli == beklenen_gecerli
    
    @given(belge_satiri_strategy())
    def test_satir_tutar_hesaplama_formulu(self, satir):
        """
        Satır tutar hesaplama formülünün doğruluğunu test et
        """
        # Tutarları hesapla
        hesaplanan = self.dogrulama_servisi.satir_tutarlari_hesapla(satir)
        
        # Formül kontrolü
        # Satır tutarı = miktar * birim_fiyat
        assert hesaplanan['satir_tutari'] == satir.miktar * satir.birim_fiyat
        
        # KDV tutarı = satır_tutarı * (kdv_oranı / 100)
        beklenen_kdv = hesaplanan['satir_tutari'] * (satir.kdv_orani / Decimal('100'))
        assert hesaplanan['kdv_tutari'] == beklenen_kdv
        
        # Satır toplamı = satır_tutarı + kdv_tutarı
        beklenen_toplam = hesaplanan['satir_tutari'] + hesaplanan['kdv_tutari']
        assert hesaplanan['satir_toplami'] == beklenen_toplam
    
    @given(satis_belgesi_strategy())
    def test_belge_dogrulama_kapsamliligi(self, belge):
        """
        Belge doğrulama işleminin kapsamlılığını test et
        """
        # Belge doğrulaması yap
        hatalar = self.dogrulama_servisi.belge_dogrula(belge)
        
        # Hata listesi dönmeli (boş olabilir)
        assert isinstance(hatalar, list)
        
        # Her hata string olmalı
        for hata in hatalar:
            assert isinstance(hata, str)
            assert len(hata) > 0
    
    @given(st.text(min_size=0, max_size=5), 
           st.integers(min_value=-10, max_value=0),
           st.integers(min_value=-10, max_value=0))
    def test_gecersiz_belge_dogrulama(self, belge_numarasi, magaza_id, kullanici_id):
        """
        Geçersiz belge bilgileri ile doğrulama testini yap
        """
        # Geçersiz belge oluştur
        belge = SatisBelgesi(
            belge_numarasi=belge_numarasi,
            belge_turu=BelgeTuru.SIPARIS,
            belge_durumu=BelgeDurumu.TASLAK,
            magaza_id=magaza_id,
            olusturan_kullanici_id=kullanici_id
        )
        
        # Doğrulama hataları olmalı
        hatalar = self.dogrulama_servisi.belge_dogrula(belge)
        
        # En az bir hata olmalı
        assert len(hatalar) > 0
        
        # Belirli hatalar kontrol edilebilir
        hata_metinleri = ' '.join(hatalar).lower()
        
        if not belge_numarasi or not belge_numarasi.strip():
            assert 'belge numarası' in hata_metinleri
        
        if magaza_id <= 0:
            assert 'mağaza' in hata_metinleri
        
        if kullanici_id <= 0:
            assert 'kullanıcı' in hata_metinleri
    
    @given(st.floats(min_value=-1000.0, max_value=0.0),
           st.floats(min_value=-100.0, max_value=-0.01))
    def test_gecersiz_satir_dogrulama(self, miktar_float, birim_fiyat_float):
        """
        Geçersiz satır bilgileri ile doğrulama testini yap
        """
        # Geçersiz satır oluştur
        satir = BelgeSatiri(
            urun_id=1,
            sira_no=1,
            miktar=Decimal(str(miktar_float)),
            birim_fiyat=Decimal(str(birim_fiyat_float)),
            kdv_orani=Decimal('18.00')
        )
        
        # Doğrulama hataları olmalı
        hatalar = self.dogrulama_servisi.satir_dogrula(satir)
        
        # En az bir hata olmalı
        assert len(hatalar) > 0
        
        # Belirli hatalar kontrol edilebilir
        hata_metinleri = ' '.join(hatalar).lower()
        
        if miktar_float <= 0:
            assert 'miktar' in hata_metinleri
        
        if birim_fiyat_float < 0:
            assert 'birim fiyat' in hata_metinleri or 'fiyat' in hata_metinleri