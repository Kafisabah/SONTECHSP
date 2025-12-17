# Version: 0.1.0
# Last Update: 2024-12-16
# Module: tests.test_dto_format_tutarliligi_property
# Description: DTO format tutarlılığı property testi
# Changelog:
# - İlk oluşturma

"""
**Feature: satis-belgeleri-modulu, Property 17: DTO format tutarlılığı**
**Validates: Requirements 7.1, 7.2**

Herhangi bir belge sorgusu için veriler DTO formatında dönülmeli ve 
durum bilgileri zaman damgası ile birlikte sağlanmalıdır
"""

import pytest
from hypothesis import given, strategies as st
from decimal import Decimal
from datetime import datetime

from sontechsp.uygulama.moduller.satis_belgeleri.modeller.satis_belgesi import (
    SatisBelgesi, BelgeTuru, BelgeDurumu
)
from sontechsp.uygulama.moduller.satis_belgeleri.modeller.belge_satiri import BelgeSatiri
from sontechsp.uygulama.moduller.satis_belgeleri.dto.belge_dto import (
    BelgeDTO, BelgeDurumGecmisiDTO
)
from sontechsp.uygulama.moduller.satis_belgeleri.dto.belge_satir_dto import BelgeSatirDTO
from sontechsp.uygulama.moduller.satis_belgeleri.dto.belge_ozet_dto import BelgeOzetDTO
from sontechsp.uygulama.moduller.satis_belgeleri.dto.filtre_dto import (
    BelgeFiltresiDTO, SayfalamaDTO, SayfaliSonucDTO
)


# Test stratejileri
belge_turu_strategy = st.sampled_from([BelgeTuru.SIPARIS, BelgeTuru.IRSALIYE, BelgeTuru.FATURA])
belge_durumu_strategy = st.sampled_from([BelgeDurumu.TASLAK, BelgeDurumu.ONAYLANDI, BelgeDurumu.FATURALANDI])
pozitif_decimal_strategy = st.decimals(min_value=Decimal('0.01'), max_value=Decimal('9999.99'), places=2)
pozitif_int_strategy = st.integers(min_value=1, max_value=1000)


@given(
    belge_turu=belge_turu_strategy,
    belge_durumu=belge_durumu_strategy,
    toplam_tutar=pozitif_decimal_strategy,
    satir_sayisi=pozitif_int_strategy
)
def test_belge_dto_format_tutarliligi(belge_turu, belge_durumu, toplam_tutar, satir_sayisi):
    """
    Property: Belge DTO formatı tutarlılığı
    
    Herhangi bir belge için DTO dönüşümü yapıldığında:
    - Tüm zorunlu alanlar dolu olmalı
    - Tarih alanları ISO format olmalı
    - Decimal alanlar doğru formatında olmalı
    - Durum bilgisi enum değeri olmalı
    """
    # Arrange: Test belgesi oluştur (mock object)
    class MockBelge:
        def __init__(self):
            self.id = 1
            self.belge_turu = belge_turu
            self.belge_durumu = belge_durumu
            self.belge_numarasi = f"TST{datetime.now().strftime('%Y%m%d%H%M%S')}"
            self.toplam_tutar = toplam_tutar
            self.kdv_tutari = toplam_tutar * Decimal('0.18')
            self.genel_toplam = toplam_tutar + self.kdv_tutari
            self.olusturma_tarihi = datetime.now()
            self.guncelleme_tarihi = datetime.now()
            self.magaza_id = 1
            self.musteri_id = None
            self.olusturan_kullanici_id = 1
            self.kaynak_belge_id = None
            self.kaynak_belge_turu = None
            self.iptal_nedeni = None
    
    belge = MockBelge()
    
    # Act: DTO'ya dönüştür
    dto = BelgeDTO.from_model(belge)
    
    # Assert: Format kontrolü
    assert dto.belge_turu == belge_turu
    assert dto.belge_durumu == belge_durumu
    assert isinstance(dto.toplam_tutar, Decimal)
    assert isinstance(dto.olusturma_tarihi, datetime)
    assert isinstance(dto.guncelleme_tarihi, datetime)
    
    # to_dict metodunda format kontrolü
    dto_dict = dto.to_dict()
    assert dto_dict['belge_turu'] == belge_turu.value
    assert dto_dict['belge_durumu'] == belge_durumu.value
    assert isinstance(dto_dict['toplam_tutar'], float)
    assert isinstance(dto_dict['olusturma_tarihi'], str)
    assert isinstance(dto_dict['guncelleme_tarihi'], str)
    
    # Tarih formatı kontrolü (ISO 8601)
    datetime.fromisoformat(dto_dict['olusturma_tarihi'])
    datetime.fromisoformat(dto_dict['guncelleme_tarihi'])


@given(
    miktar=pozitif_decimal_strategy,
    birim_fiyat=pozitif_decimal_strategy,
    kdv_orani=st.decimals(min_value=Decimal('0'), max_value=Decimal('20'), places=2)
)
def test_belge_satir_dto_format_tutarliligi(miktar, birim_fiyat, kdv_orani):
    """
    Property: Belge satır DTO formatı tutarlılığı
    
    Belge satırı DTO'sunda:
    - Tüm numeric alanlar doğru formatında olmalı
    - Hesaplanan alanlar doğru olmalı
    """
    # Arrange: Test satırı oluştur (mock object)
    class MockSatir:
        def __init__(self):
            self.id = 1
            self.belge_id = 1
            self.urun_id = 1
            self.miktar = miktar
            self.birim_fiyat = birim_fiyat
            self.kdv_orani = kdv_orani
            self.satir_tutari = miktar * birim_fiyat
            self.kdv_tutari = self.satir_tutari * kdv_orani / Decimal('100')
            self.satir_toplami = self.satir_tutari + self.kdv_tutari
            self.sira_no = 1
    
    satir = MockSatir()
    
    # Act: DTO'ya dönüştür
    dto = BelgeSatirDTO.from_model(satir)
    
    # Assert: Format kontrolü
    assert isinstance(dto.miktar, Decimal)
    assert isinstance(dto.birim_fiyat, Decimal)
    assert isinstance(dto.kdv_orani, Decimal)
    assert isinstance(dto.satir_tutari, Decimal)
    assert isinstance(dto.kdv_tutari, Decimal)
    
    # to_dict metodunda format kontrolü
    dto_dict = dto.to_dict()
    assert isinstance(dto_dict['miktar'], float)
    assert isinstance(dto_dict['birim_fiyat'], float)
    assert isinstance(dto_dict['kdv_orani'], float) or dto_dict['kdv_orani'] == 0.0
    assert isinstance(dto_dict['satir_tutari'], float)
    assert isinstance(dto_dict['kdv_tutari'], float) or dto_dict['kdv_tutari'] == 0.0
    
    # Hesaplama kontrolü
    beklenen_satir_tutari = miktar * birim_fiyat
    beklenen_kdv_tutari = beklenen_satir_tutari * kdv_orani / Decimal('100')
    
    assert dto.satir_tutari == beklenen_satir_tutari
    assert dto.kdv_tutari == beklenen_kdv_tutari


@given(
    belge_sayisi=st.integers(min_value=1, max_value=100),
    sayfa_boyutu=st.integers(min_value=1, max_value=50)
)
def test_sayfalama_dto_format_tutarliligi(belge_sayisi, sayfa_boyutu):
    """
    Property: Sayfalama DTO formatı tutarlılığı
    
    Sayfalama sonuçlarında:
    - Toplam sayfa hesabı doğru olmalı
    - Sayfa numaraları geçerli aralıkta olmalı
    - Meta bilgiler tutarlı olmalı
    """
    # Arrange: Sayfalama parametreleri
    sayfa = 1
    toplam_kayit = belge_sayisi
    
    # Act: Sayfalama DTO oluştur
    sayfalama = SayfalamaDTO(
        sayfa=sayfa,
        sayfa_boyutu=sayfa_boyutu
    )
    
    # Toplam sayfa hesabı
    import math
    beklenen_toplam_sayfa = math.ceil(toplam_kayit / sayfa_boyutu)
    
    # Mock belge özet listesi
    class MockBelgeOzet:
        def __init__(self, i):
            self.id = i
            self.belge_numarasi = f"TST{i:06d}"
            self.belge_turu = BelgeTuru.SIPARIS
            self.belge_durumu = BelgeDurumu.TASLAK
            self.magaza_id = 1
            self.musteri_id = None
            self.genel_toplam = Decimal('100.00')
            self.olusturma_tarihi = datetime.now()
            self.olusturan_kullanici_id = 1
        
        def to_dict(self):
            return {
                'id': self.id,
                'belge_numarasi': self.belge_numarasi,
                'belge_turu': self.belge_turu.value,
                'belge_durumu': self.belge_durumu.value,
                'genel_toplam': float(self.genel_toplam)
            }
    
    belgeler = [
        BelgeOzetDTO.from_model(MockBelgeOzet(i))
        for i in range(min(sayfa_boyutu, toplam_kayit))
    ]
    
    sonuc = SayfaliSonucDTO(
        veriler=belgeler,
        toplam_kayit=toplam_kayit,
        sayfa=sayfa,
        sayfa_boyutu=sayfa_boyutu
    )
    
    # Assert: Sayfalama tutarlılığı
    assert sonuc.toplam_sayfa == beklenen_toplam_sayfa
    assert sonuc.sayfa <= sonuc.toplam_sayfa
    assert len(sonuc.veriler) <= sayfa_boyutu
    assert sonuc.toplam_kayit == toplam_kayit


@given(
    filtre_baslangic=st.datetimes(min_value=datetime(2024, 1, 1), max_value=datetime(2024, 6, 30)),
    filtre_bitis=st.datetimes(min_value=datetime(2024, 7, 1), max_value=datetime(2024, 12, 31))
)
def test_filtre_dto_format_tutarliligi(filtre_baslangic, filtre_bitis):
    """
    Property: Filtre DTO formatı tutarlılığı
    
    Filtre parametrelerinde:
    - Tarih aralıkları geçerli olmalı
    - Enum değerleri doğru formatında olmalı
    """
    # Arrange & Act: Filtre DTO oluştur
    filtre = BelgeFiltresiDTO(
        baslangic_tarihi=filtre_baslangic,
        bitis_tarihi=filtre_bitis,
        belge_turu=BelgeTuru.SIPARIS,
        belge_durumu=BelgeDurumu.TASLAK
    )
    
    # Assert: Format kontrolü
    assert isinstance(filtre.baslangic_tarihi, datetime)
    assert isinstance(filtre.bitis_tarihi, datetime)
    assert isinstance(filtre.belge_turu, BelgeTuru)
    assert isinstance(filtre.belge_durumu, BelgeDurumu)
    
    # to_dict metodunda format kontrolü
    filtre_dict = filtre.to_dict()
    assert isinstance(filtre_dict['baslangic_tarihi'], str)
    assert isinstance(filtre_dict['bitis_tarihi'], str)
    assert isinstance(filtre_dict['belge_turu'], str)
    assert isinstance(filtre_dict['belge_durumu'], str)
    
    # Tarih aralığı kontrolü
    assert filtre.baslangic_tarihi <= filtre.bitis_tarihi
    
    # Enum değer kontrolü
    assert filtre_dict['belge_turu'] == BelgeTuru.SIPARIS.value
    assert filtre_dict['belge_durumu'] == BelgeDurumu.TASLAK.value