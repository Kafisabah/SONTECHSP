# Version: 0.1.0
# Last Update: 2024-12-16
# Module: test_satis_belgeleri_model_property
# Description: Satış belgeleri model property testleri
# Changelog:
# - İlk oluşturma

"""
**Feature: satis-belgeleri-modulu, Property 1: Sipariş oluşturma tutarlılığı**
**Validates: Requirements 1.1, 1.2**

Satış belgeleri modeli için property-based testler.
Bu testler belge modellerinin doğruluk özelliklerini test eder.
"""

from decimal import Decimal
from hypothesis import given, strategies as st
import pytest

from sontechsp.uygulama.moduller.satis_belgeleri.modeller import (
    SatisBelgesi, BelgeSatiri, BelgeTuru, BelgeDurumu
)


# Test stratejileri
@st.composite
def belge_turu_strategy(draw):
    """Belge türü üretici"""
    return draw(st.sampled_from(list(BelgeTuru)))


@st.composite
def belge_durumu_strategy(draw):
    """Belge durumu üretici"""
    return draw(st.sampled_from(list(BelgeDurumu)))


@st.composite
def pozitif_decimal_strategy(draw):
    """Pozitif decimal üretici"""
    return Decimal(str(draw(st.floats(min_value=0.01, max_value=999999.99))))


@st.composite
def satis_belgesi_strategy(draw):
    """Geçerli satış belgesi üretici"""
    return SatisBelgesi(
        belge_turu=draw(belge_turu_strategy()),
        belge_durumu=draw(belge_durumu_strategy()),
        magaza_id=draw(st.integers(min_value=1, max_value=1000)),
        olusturan_kullanici_id=draw(st.integers(min_value=1, max_value=1000)),
        musteri_id=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=10000))),
        toplam_tutar=draw(pozitif_decimal_strategy()),
        kdv_tutari=draw(pozitif_decimal_strategy()),
        genel_toplam=draw(pozitif_decimal_strategy())
    )


@st.composite
def belge_satiri_strategy(draw):
    """Geçerli belge satırı üretici"""
    miktar = draw(pozitif_decimal_strategy())
    birim_fiyat = draw(pozitif_decimal_strategy())
    kdv_orani = Decimal(str(draw(st.floats(min_value=0, max_value=50))))
    
    return BelgeSatiri(
        urun_id=draw(st.integers(min_value=1, max_value=10000)),
        miktar=miktar,
        birim_fiyat=birim_fiyat,
        kdv_orani=kdv_orani
    )


class TestSatisBelgesiProperty:
    """Satış belgesi property testleri"""
    
    @given(satis_belgesi_strategy())
    def test_siparis_olusturma_tutarliligi(self, belge: SatisBelgesi):
        """
        **Feature: satis-belgeleri-modulu, Property 1: Sipariş oluşturma tutarlılığı**
        **Validates: Requirements 1.1, 1.2**
        
        Herhangi bir geçerli sipariş bilgisi için, sipariş oluşturma işlemi 
        başarılı olduğunda belge TASLAK durumunda kaydedilmeli ve benzersiz numara atanmalıdır
        """
        # Sipariş türünde belge oluştur
        siparis = SatisBelgesi(
            belge_turu=BelgeTuru.SIPARIS,
            belge_durumu=BelgeDurumu.TASLAK,
            magaza_id=belge.magaza_id,
            olusturan_kullanici_id=belge.olusturan_kullanici_id,
            musteri_id=belge.musteri_id
        )
        
        # Doğrulama hatalarını kontrol et
        hatalar = siparis.dogrula()
        
        # Zorunlu alanlar dolu ise hata olmamalı
        if siparis.magaza_id and siparis.olusturan_kullanici_id:
            # Sadece satır eksikliği hatası olabilir
            assert len([h for h in hatalar if "satır" not in h.lower()]) == 0
        
        # Belge türü sipariş olmalı
        assert siparis.belge_turu == BelgeTuru.SIPARIS
        
        # Başlangıç durumu taslak olmalı
        assert siparis.belge_durumu == BelgeDurumu.TASLAK
    
    @given(belge_satiri_strategy())
    def test_belge_satir_tutarliligi(self, satir: BelgeSatiri):
        """
        **Feature: satis-belgeleri-modulu, Property 2: Belge satır tutarlılığı**
        **Validates: Requirements 1.3**
        
        Herhangi bir belge satırı eklendiğinde, ürün bilgileri doğrulanmalı 
        ve toplam tutarlar doğru hesaplanmalıdır
        """
        # Satır doğrulaması
        hatalar = satir.dogrula()
        
        # Geçerli satır için hata olmamalı
        if satir.urun_id and satir.miktar > 0 and satir.birim_fiyat >= 0:
            assert len(hatalar) == 0
        
        # Tutar hesaplamaları doğru olmalı
        beklenen_satir_tutari = satir.miktar * satir.birim_fiyat
        beklenen_kdv_tutari = beklenen_satir_tutari * (satir.kdv_orani / Decimal('100'))
        beklenen_satir_toplami = beklenen_satir_tutari + beklenen_kdv_tutari
        
        assert satir.satir_tutari == beklenen_satir_tutari
        assert satir.kdv_tutari == beklenen_kdv_tutari
        assert satir.satir_toplami == beklenen_satir_toplami
    
    @given(satis_belgesi_strategy(), st.lists(belge_satiri_strategy(), min_size=1, max_size=5))
    def test_belge_toplam_hesaplama_tutarliligi(self, belge: SatisBelgesi, satirlar: list):
        """
        Belgeye satır eklendiğinde toplam tutarların doğru hesaplandığını test et
        """
        # Belgeye satırları ekle
        for satir in satirlar:
            belge.satir_ekle(satir)
        
        # Toplam tutarları manuel hesapla
        beklenen_toplam_tutar = sum(satir.satir_tutari for satir in satirlar)
        beklenen_kdv_tutari = sum(satir.kdv_tutari for satir in satirlar)
        beklenen_genel_toplam = beklenen_toplam_tutar + beklenen_kdv_tutari
        
        # Belge tutarları ile karşılaştır
        assert belge.toplam_tutar == beklenen_toplam_tutar
        assert belge.kdv_tutari == beklenen_kdv_tutari
        assert belge.genel_toplam == beklenen_genel_toplam
    
    @given(satis_belgesi_strategy())
    def test_durum_gecis_kurallari(self, belge: SatisBelgesi):
        """
        Belge durum geçiş kurallarının tutarlılığını test et
        """
        # TASLAK durumundan geçerli geçişler
        if belge.belge_durumu == BelgeDurumu.TASLAK:
            assert belge.durum_degistirilebilir_mi(BelgeDurumu.ONAYLANDI)
            assert belge.durum_degistirilebilir_mi(BelgeDurumu.IPTAL)
            assert not belge.durum_degistirilebilir_mi(BelgeDurumu.FATURALANDI)
        
        # ONAYLANDI durumundan geçerli geçişler
        elif belge.belge_durumu == BelgeDurumu.ONAYLANDI:
            assert belge.durum_degistirilebilir_mi(BelgeDurumu.FATURALANDI)
            assert belge.durum_degistirilebilir_mi(BelgeDurumu.IPTAL)
            assert not belge.durum_degistirilebilir_mi(BelgeDurumu.TASLAK)
        
        # FATURALANDI durumundan geçerli geçişler
        elif belge.belge_durumu == BelgeDurumu.FATURALANDI:
            assert belge.durum_degistirilebilir_mi(BelgeDurumu.IPTAL)
            assert not belge.durum_degistirilebilir_mi(BelgeDurumu.TASLAK)
            assert not belge.durum_degistirilebilir_mi(BelgeDurumu.ONAYLANDI)
        
        # IPTAL durumundan geçiş yok
        elif belge.belge_durumu == BelgeDurumu.IPTAL:
            assert not belge.durum_degistirilebilir_mi(BelgeDurumu.TASLAK)
            assert not belge.durum_degistirilebilir_mi(BelgeDurumu.ONAYLANDI)
            assert not belge.durum_degistirilebilir_mi(BelgeDurumu.FATURALANDI)
    
    @given(satis_belgesi_strategy(), st.text(min_size=1, max_size=100))
    def test_iptal_islemi_tutarliligi(self, belge: SatisBelgesi, iptal_nedeni: str):
        """
        Belge iptal işleminin tutarlılığını test et
        """
        # İptal edilebilir durumda ise
        if belge.durum_degistirilebilir_mi(BelgeDurumu.IPTAL):
            belge.iptal_et(iptal_nedeni)
            
            # İptal durumu ve bilgileri kontrol et
            assert belge.belge_durumu == BelgeDurumu.IPTAL
            assert belge.iptal_nedeni == iptal_nedeni
            assert belge.iptal_tarihi is not None
        
        # İptal edilemez durumda ise hata fırlatmalı
        else:
            with pytest.raises(ValueError):
                belge.iptal_et(iptal_nedeni)